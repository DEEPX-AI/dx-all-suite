"""DX-APP Inference engine — run, stop, multi-model, pipeline.

Split (P2-2-A) into a layered DAG — each layer imports only downward, no
circular imports:
  dx_app/core/inference_exec.py  (bottom)  — helpers/constants (stdlib+config only)
  dx_app/core/camera.py                    — camera/Xvfb/cam-mux (imports inference_exec)
  dx_app/core/live.py                      — live-mode inference (imports inference_exec+camera)
  dx_app/core/inference.py       (this, top) — run/stop/multi/pipeline; re-exports
                                                the full public API so existing
                                                `from dx_app.core.inference import ...`
                                                call sites (dx_app/server.py) keep working.
"""

import os, json, time, base64, subprocess, threading, tempfile, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dx_app.core import config
from dx_app.core.config import (DX_APP_ROOT, CPP_DIR, PY_DIR, BUILD_DIR, ASSETS_DIR,
                    SAMPLE_DIR, OUTPUTS_DIR, SCRIPTS_DIR, CAT_IMAGE, CAT_VIDEO,
                    _RUNTIME_PYTHON, _RUNTIME_PYTHONPATH)
from shared.runtime import ld_library_path
from dx_app.core.dx_app_security import resolve_existing_file
from dx_app.core.performance import _parse_perf, _cvt_video
from shared.hardware import get_hw
from dx_app.core.run_config import build_run_config

from dx_app.core.inference_exec import (
    _err, _count_images_in_dir, _python_script_path, _python_runtime_ready,
    _effective_run_lang, _find_fallback_binary, _find_saved_video,
    _drain_dxrt_msgqueues, _sweep_stale_temp,
    _TMP, _FALLBACK_BINARIES, _PAIR_COMPARE_CATS, _STDOUT_TAG_CATS, _IMAGE_EXTENSIONS,
)
from dx_app.core.camera import (
    list_cameras, _start_cam_mux, _stop_cam_mux, _get_capture_lock, _crop_roi,
    _ensure_xvfb, capture_live_frame,
)
from dx_app.core.live import (
    run_inference_live, poll_inference, stop_inference_live, get_inference_result,
    shutdown_live_processes, _terminate_proc, _parse_task_tags, _parse_detections,
    _live_jobs, _live_procs, _live_procs_lock,
)
# camera/live own these module-level state dicts (mutated in place, e.g. .clear()/
# item assignment/.pop() — sharing the object, not copying its value); re-imported
# here (module-qualified below via `import dx_app.core.camera as _camera`) only for
# tests that poke `inference._xvfb_procs` / `inference._cam_mux_...` directly. Any
# rebind of a scalar (e.g. _cam_mux_proc) must go through the OWNING module
# (dx_app.core.camera) so there is a single source of truth — see camera.py.
import dx_app.core.camera as _camera
_xvfb_procs = _camera._xvfb_procs
_xvfb_lock = _camera._xvfb_lock

MAX_IMAGE_BASE64_BYTES = 20 * 1024 * 1024
RUN_UPLOAD_ROOTS = (DX_APP_ROOT, OUTPUTS_DIR, SAMPLE_DIR, ASSETS_DIR)

# run_multi shares subprocess handles across concurrent worker threads. A single
# shared handle (config._running_proc) is clobbered when several runs are in flight,
# so a concurrent stop/restart would lose or double-handle a child. Track every
# in-flight multi child here under a lock and stop from a consistent snapshot.
_multi_procs = []            # list of live Popen handles owned by active run_multi calls
_multi_procs_lock = threading.Lock()


def run_inference(model_name, category, model_file, lang="cpp", variant="sync",
                  input_type="image", image_path=None, video_path=None,
                  device_id=None, conf_threshold=None, nms_threshold=None,
                  config_overrides=None,
                  upload_path=None, timeout=120, loop=None,
                  camera_id=None, rtsp_url=None,
                  save_output=True, image_base64=None, _multi=False):
    _sweep_stale_temp()
    if not model_file: return _err("no_model_file", "No model file configured")
    # Multi-model support: if model_file starts with '-', it contains custom CLI args
    is_multi_model = model_file.startswith("-")
    if is_multi_model:
        import shlex
        model_args = shlex.split(model_file)
        for i, arg in enumerate(model_args):
            if not arg.startswith("-") and arg.endswith(".dxnn"):
                mfp = DX_APP_ROOT / arg
                if not mfp.exists():
                    return _err("model_not_found", f"Model file not found: {arg}")
                model_args[i] = str(mfp)
    else:
        mp = DX_APP_ROOT / model_file
        if not mp.exists(): return _err("model_not_found", f"Model file not found: {model_file}")
    _b64_tmp = None
    if input_type == "image" and image_base64:
        try:
            raw = image_base64.split(",", 1)[-1] if "," in image_base64 else image_base64
            if len(raw) > MAX_IMAGE_BASE64_BYTES:
                return _err("image_base64_too_large", "image_base64 too large")
            img_bytes = base64.b64decode(raw, validate=True)
        except Exception:
            return _err("invalid_image_base64", "Invalid image_base64")
        fd, _b64_tmp = tempfile.mkstemp(prefix="dxapp_upload_", suffix=".jpg", dir=_TMP)
        os.close(fd)
        Path(_b64_tmp).write_bytes(img_bytes)
        upload_path = _b64_tmp
    _is_live = input_type in ("camera", "rtsp")
    if _is_live:
        if input_type == "camera":
            _cam_idx = int(camera_id) if camera_id is not None else 0
            inp = Path(f"/dev/video{_cam_idx}")
            if not inp.exists(): return _err("camera_not_found", f"Camera device not found: {inp}")
        else:  # rtsp
            if not rtsp_url: return _err("rtsp_required", "RTSP URL is required")
            inp = Path(rtsp_url)  # placeholder — not a real path, used as string
    elif _b64_tmp and upload_path == _b64_tmp:
        inp = Path(upload_path)
    elif upload_path:
        try:
            inp = resolve_existing_file(upload_path, RUN_UPLOAD_ROOTS, None)
        except ValueError as e:
            return _err("path_outside_allowed_roots", f"Path is outside allowed roots: {upload_path}")
    elif input_type == "image": inp = DX_APP_ROOT / (image_path or CAT_IMAGE.get(category, "sample/img/sample_street.jpg"))
    else: inp = DX_APP_ROOT / (video_path or CAT_VIDEO.get(category, "assets/videos/dance-group.mov"))
    if not _is_live and not inp.exists(): return _err("input_not_found", f"Input not found: {inp}")
    # DXAPP_SAVE_IMAGE forces per-frame render even with --no-display; skip for video (perf + no still needed).
    res_img = None if input_type == "video" else tempfile.mktemp(suffix=".jpg", dir=_TMP)
    # Merge model config.json with UI overrides (schema-aligned; no per-model hardcoding)
    merged_cfg = build_run_config(
        category, model_name, config_overrides, conf_threshold, nms_threshold,
    )
    tmp_config = None
    if merged_cfg is not None:
        tmp_config = tempfile.mktemp(suffix=".json", dir=_TMP)
        Path(tmp_config).write_text(json.dumps(merged_cfg))
    _ld = ld_library_path()
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "LD_LIBRARY_PATH": _ld}
    if res_img:
        env["DXAPP_SAVE_IMAGE"] = res_img
    # dx_engine lives on PYTHONPATH (not pip-installed); the python_example subprocess needs it.
    if _RUNTIME_PYTHONPATH:
        env["PYTHONPATH"] = _RUNTIME_PYTHONPATH + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    if _is_live:
        # Camera/RTSP needs DISPLAY for GStreamer → V4L2 pipeline
        env.setdefault("DISPLAY", ":0")
    else:
        env.pop("DISPLAY", None)
    if input_type == "image":
        inf = "-i"
    else:
        inf = "-v"  # video, camera, rtsp all use -v flag
    _inp_str = rtsp_url if input_type == "rtsp" else str(inp)
    _loop = loop or (100 if _is_live else 1)
    # embedding/reid: pair-folder demo needs 2+ images (1st = reference, 2nd+ = compare canvas)
    if not _is_live and input_type == "image" and category in _PAIR_COMPARE_CATS and inp.is_dir():
        pair_n = _count_images_in_dir(inp)
        if not loop and pair_n >= 2:
            _loop = pair_n
    if _is_live:
        timeout = max(timeout, 300)  # live sources may need more time
    _video_save_dir = None
    run_lang = _effective_run_lang(lang, category, model_name, variant, input_type)
    tag_extra = ["--show-log"] if category in _STDOUT_TAG_CATS else []
    if run_lang == "cpp":
        bp = BUILD_DIR / f"{model_name}_{variant}"
        if not bp.exists():
            bp = _find_fallback_binary(category, variant, build_dir=BUILD_DIR)
            if not bp:
                if _b64_tmp:
                    try: os.unlink(_b64_tmp)
                    except OSError: pass
                return _err("binary_not_found", f"Binary not found: {model_name}_{variant} — run build.sh")
        extra = list(tag_extra)
        # Stock dx-runtime C++ --save can SIGABRT when VideoWriter reports w/h=0; skip save on cpp.
        if input_type != "video":
            pass
        if is_multi_model:
            cmd = [str(bp)] + model_args + [inf, _inp_str, "--no-display", "-l", str(_loop)] + extra
        else:
            if tmp_config: extra += ["--config", tmp_config]
            cmd = [str(bp), "-m", str(mp), inf, _inp_str, "--no-display", "-l", str(_loop)] + extra
    else:
        pf = _python_script_path(category, model_name, variant, py_dir=PY_DIR)
        if not pf:
            if _b64_tmp:
                try: os.unlink(_b64_tmp)
                except OSError: pass
            return _err("script_not_found", f"Script not found: {model_name}_{variant}.py")
        py_extra = list(tag_extra)
        if tmp_config: py_extra += ["--config", tmp_config]
        if input_type == "video":
            _video_save_dir = tempfile.mkdtemp(prefix="dxapp_video_", dir=_TMP)
            py_extra += ["--save", "--save-dir", _video_save_dir]
        if _loop != 1:
            py_extra += ["-l", str(_loop)]
        cmd = [_RUNTIME_PYTHON, str(pf), "--model", str(mp),
               f"--{'image' if input_type=='image' else 'video'}", _inp_str, "--no-display"] + py_extra
    hw0 = get_hw(); t0 = time.time()
    _stdout_file = tempfile.mktemp(suffix=".log", dir=_TMP)
    proc = None
    try:
        with open(_stdout_file, "w") as _fout:
            _drain_dxrt_msgqueues()
            with config._proc_lock:
                config._running_proc = subprocess.Popen(cmd, stdout=_fout, stderr=subprocess.STDOUT,
                 cwd=str(DX_APP_ROOT), env=env, text=True, close_fds=True); proc = config._running_proc
            if _multi: _multi_register(proc)
            proc.wait(timeout=timeout); elapsed = time.time() - t0
        if _multi: _multi_unregister(proc)
        with config._proc_lock: config._running_proc = None
        try:
            stdout = open(_stdout_file, "r").read()
        except:
            stdout = ""
        hw1 = get_hw()
        res = {"exit_code": proc.returncode, "output": stdout[-4000:], "model": model_name,
               "category": category, "lang": lang, "variant": variant, "input_type": input_type,
               "elapsed_s": round(elapsed, 2), "timestamp": time.time(), "device_id": device_id, "hw_after": hw1}
        if run_lang != lang:
            res["lang_effective"] = run_lang
        if input_type == "video":
            res["video_save_mode"] = "python_save" if run_lang == "python" else "cpp_no_save"
        perf = _parse_perf(stdout); res["perf"] = perf
        res["fps"] = perf.get("overall_fps", ""); res["latency"] = perf.get("inference_latency", "")

        task = _parse_task_tags(stdout)
        res["task_tag"] = task["tag"]
        res["task_summary"] = task["summary"]
        res["task_frames"] = task["frame_count"]
        # Human-readable last predictions (e.g. classification top-k "tabby: 85.3%") — the only
        # visualizable result for tasks (classification/depth/pose/...) that emit NO output image.
        res["task_last_pred"] = task["last_pred"]

        # Result image — normalise to input resolution for CMP slider
        if res_img and os.path.exists(res_img) and os.path.getsize(res_img) > 0:
            try:
                import cv2 as _cv2
                _inp_img = _cv2.imread(str(inp))
                _res_img = _cv2.imread(res_img)
                if _inp_img is not None and _res_img is not None:
                    _ih, _iw = _inp_img.shape[:2]
                    _rh, _rw = _res_img.shape[:2]
                    # Side-by-side canvas (e.g. SR = Bicubic|model output): the result is
                    # two panels laid horizontally, so its aspect ratio is ~2x the input's
                    # (holds whether or not the model upscales — the old abs(rh-ih) check
                    # broke for SR because the panels are also 4x taller). Crop to the right
                    # panel (model output). Skip embedding/reid, which use their own layout.
                    _inp_ar = _iw / _ih if _ih else 0
                    _res_ar = _rw / _rh if _rh else 0
                    if (category not in _PAIR_COMPARE_CATS and _inp_ar
                            and abs(_res_ar - _inp_ar * 2) < _inp_ar * 0.3):
                        _res_img = _res_img[:, _rw // 2 + 2:]
                        _rh, _rw = _res_img.shape[:2]
                    # Only resize-back if result is SMALLER than original (denoising/etc.)
                    # For SR, keep the high-res result — CMP slider handles it via object-fit:contain
                    if (_rw, _rh) != (_iw, _ih) and not (_rw > _iw and _rh > _ih):
                        _res_img = _cv2.resize(_res_img, (_iw, _ih), interpolation=_cv2.INTER_LANCZOS4)
                    _cv2.imwrite(res_img, _res_img)
            except Exception:
                pass
            # For video input, skip returning result_image (video is the real result)
            if input_type == "video":
                res["result_image"] = None
            else:
                res["result_image"] = base64.b64encode(open(res_img, "rb").read()).decode()
                # Save a copy to outputs directory for gallery (skip when save_output=False)
                if save_output:
                    try:
                        _out_name = f"result_{model_name}_{int(time.time())}.jpg"
                        _out_dst = OUTPUTS_DIR / _out_name
                        shutil.copy2(res_img, str(_out_dst))
                        res["result_image_url"] = f"/outputs/{_out_name}"
                    except Exception:
                        pass
        else:
            res["result_image"] = None
        res["result_video_url"] = None
        if input_type == "video":
            vo = _find_saved_video(stdout, _video_save_dir) or (DX_APP_ROOT / "result.mp4")
            if vo.exists() and vo.stat().st_size > 0:
                dst = OUTPUTS_DIR / f"result_{model_name}_{int(time.time())}.mp4"
                if _cvt_video(vo, dst): res["result_video_url"] = f"/outputs/{dst.name}"
                if vo == DX_APP_ROOT / "result.mp4":
                    try: vo.unlink(missing_ok=True)
                    except: pass
        if proc.returncode != 0:
            res["error_hint"] = f"Exit code {proc.returncode}"
            # If no usable perf data was parsed, promote to hard error
            # so validation correctly counts this run as failed.

        if proc.returncode != 0 and not res.get("fps"):
                res["error"] = f"Process exited with code {proc.returncode}: {(res.get('output') or '')[-200:].strip()}"
                res["error_key"] = "process_exit"
        with config._history_lock:
            config._recent_runs.appendleft({"model": model_name, "category": category, "lang": lang,
             "variant": variant, "input_type": input_type, "fps": res["fps"], "latency": res["latency"],
             "elapsed_s": res["elapsed_s"], "exit_code": proc.returncode, "timestamp": time.time(),
             })
        return res
    except subprocess.TimeoutExpired:
        if _multi and proc is not None: _multi_unregister(proc)
        with config._proc_lock:
            if config._running_proc: config._running_proc.kill(); config._running_proc.wait(); config._running_proc = None
        return _err("inference_timeout", f"Timeout ({timeout}s)", model=model_name)
    except Exception as e:
        if _multi and proc is not None: _multi_unregister(proc)
        return _err("inference_exception", str(e), model=model_name)
    finally:
        # Single cleanup point for every exit path (success/timeout/exception):
        # remove whatever temp artifacts this run created.
        for _p in (_stdout_file, tmp_config, _b64_tmp, res_img):
            if _p:
                try: os.unlink(_p)
                except OSError: pass
        if _video_save_dir:
            shutil.rmtree(_video_save_dir, ignore_errors=True)


def stop_inference():
    with config._proc_lock:
        if config._running_proc: config._running_proc.kill(); config._running_proc = None; return {"status": "stopped"}
    return {"status": "no_process"}


def _multi_register(proc):
    """Track a run_multi child process handle under the lock."""
    with _multi_procs_lock:
        _multi_procs.append(proc)


def _multi_unregister(proc):
    """Drop a run_multi child once it has finished (guarded)."""
    with _multi_procs_lock:
        try: _multi_procs.remove(proc)
        except ValueError: pass


def stop_multi():
    """Terminate every in-flight run_multi child from a locked snapshot so a
    concurrent stop/restart cannot lose or double-handle a process (F-14b)."""
    with _multi_procs_lock:
        snapshot = list(_multi_procs)
    stopped = 0
    for p in snapshot:
        try:
            if p and p.poll() is None:
                p.terminate(); stopped += 1
        except Exception:
            pass
    return {"status": "stopping", "count": stopped}


def run_multi(reqs):
    results = [None] * len(reqs)
    def _one(idx, req): r = run_inference(_multi=True, **req); r["slot"] = idx; return idx, r
    with ThreadPoolExecutor(max_workers=min(len(reqs), 4)) as ex:
        futs = {ex.submit(_one, i, req): i for i, req in enumerate(reqs)}
        for fut in as_completed(futs):
            try: idx, r = fut.result(timeout=150); results[idx] = r
            except Exception as e: results[futs[fut]] = {"error": str(e), "error_key": "inference_exception", "slot": futs[fut]}
    return results


def run_pipeline(steps, input_path, input_type="image", mode="chain"):
    """Pipeline modes:
    - chain: pass result_image from step N to step N+1
    - cascade: step 1 detects objects, step 2+ runs on each cropped region
    """
    results = []; cur = input_path
    if mode == "cascade" and len(steps) >= 2 and input_type == "image":
        step0 = steps[0]
        r0 = run_inference(step0.get("model_name", ""), step0.get("category", ""), step0.get("model_file", ""),
         step0.get("lang", "cpp"), step0.get("variant", "sync"), "image",
         image_path=str(input_path))
        r0.update({"step_index": 0, "step_model": step0.get("model_name", "")})
        results.append(r0)
        dets = _parse_detections(r0.get("output", ""))
        if not dets:
            r0["cascade_note"] = "No detections found in step 1"
            return results
        for si in range(1, len(steps)):
            step = steps[si]
            crop_results = []
            orig_path = input_path
            for di, det in enumerate(dets):
                bbox = det["bbox"]  # x1,y1,x2,y2 in display coords
                dw, dh = det.get("disp_w", 1), det.get("disp_h", 1)
                try:
                    import cv2
                    orig_img = cv2.imread(str(DX_APP_ROOT / orig_path) if not os.path.isabs(str(orig_path)) else str(orig_path))
                    if orig_img is None: continue
                    oh, ow = orig_img.shape[:2]
                except: continue
                # Scale bbox from display coords to original coords
                sx, sy = ow / dw, oh / dh
                x1 = max(0, int(bbox[0] * sx)); y1 = max(0, int(bbox[1] * sy))
                x2 = min(ow, int(bbox[2] * sx)); y2 = min(oh, int(bbox[3] * sy))
                if x2 <= x1 or y2 <= y1: continue
                crop = orig_img[y1:y2, x1:x2]
                if crop.size == 0: continue
                tmp = tempfile.mktemp(suffix=".jpg", dir=_TMP)
                cv2.imwrite(tmp, crop)
                cr = run_inference(step.get("model_name", ""), step.get("category", ""), step.get("model_file", ""),
                 step.get("lang", "cpp"), step.get("variant", "sync"), "image", image_path=tmp)
                cr.update({"step_index": si, "step_model": step.get("model_name", ""),
                           "crop_index": di, "crop_class": det.get("class", ""),
                           "crop_conf": det.get("conf", 0),
                           "crop_bbox": [x1, y1, x2, y2]})
                crop_results.append(cr)
                try: os.unlink(tmp)
                except: pass
            results.append({"step_index": si, "step_model": step.get("model_name", ""),
                           "cascade_crops": crop_results, "crop_count": len(crop_results)})
        return results
    for i, step in enumerate(steps):
        actual = cur
        if step.get("crop_bbox") and input_type == "image" and os.path.exists(str(cur)):
            c = _crop_roi(Path(cur), step["crop_bbox"])
            if c: actual = c
        r = run_inference(step.get("model_name", ""), step.get("category", ""), step.get("model_file", ""),
         step.get("lang", "cpp"), step.get("variant", "sync"), input_type,
         image_path=str(actual) if input_type == "image" else None,
         video_path=str(actual) if input_type == "video" else None)
        r.update({"step_index": i, "step_model": step.get("model_name", "")}); results.append(r)
        if r.get("result_image") and input_type == "image":
            try:
                tmp = tempfile.mktemp(suffix=".jpg", dir=_TMP)
                open(tmp, "wb").write(base64.b64decode(r["result_image"])); cur = tmp
            except: pass
    return results

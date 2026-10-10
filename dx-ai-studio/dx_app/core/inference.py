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

import os, json, time, base64, signal, subprocess, threading, tempfile, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dx_app.core import config
from dx_app.core.config import (DX_APP_ROOT, CPP_DIR, PY_DIR, BUILD_DIR, ASSETS_DIR,
                    SAMPLE_DIR, OUTPUTS_DIR, SCRIPTS_DIR, CAT_IMAGE, CAT_VIDEO,
                    _RUNTIME_PYTHON, _RUNTIME_PYTHONPATH, resolve_model_path)
from shared.runtime import ld_library_path
from shared import dxrt
from shared import debug_log
from dx_app.core.dx_app_security import resolve_existing_file
from dx_app.core.performance import _parse_perf, _cvt_video, runner_errors
from shared.hardware import get_hw
from dx_app.core.run_config import build_run_config

from dx_app.core.inference_exec import (
    _err, _count_images_in_dir, _python_script_path, _python_runtime_ready,
    _effective_run_lang, _find_fallback_binary, _is_executable_file, _find_saved_video, _find_saved_image,
    _drain_dxrt_msgqueues, _sweep_stale_temp,
    _TMP, _FALLBACK_BINARIES, _PAIR_COMPARE_CATS, _SIDE_BY_SIDE_OUTPUT_CATS,
    _STDOUT_TAG_CATS, _IMAGE_EXTENSIONS,
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


def _video_has_frames(path) -> bool:
    """True if `path` is a video with real content (non-zero duration).

    A C++ example can open a VideoWriter, print "Saving output video: …", and still write
    ZERO frames — the async headless (`--no-display --save`) runner does exactly this, leaving
    a ~260-byte, 0-duration MP4 that is size>0 but unplayable. ffprobe the container duration
    (metadata only, no full decode) to reject those so the GUI never shows a broken empty
    player. If ffprobe is unavailable, fall back to a size heuristic (an empty container is
    tiny; a real annotated clip is comfortably larger)."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
            capture_output=True, text=True, timeout=30)
        out = (r.stdout or "").strip()
        return bool(out) and out != "N/A" and float(out) > 0.0
    except (ValueError, OSError, subprocess.SubprocessError):
        try:
            return path.stat().st_size > 4096
        except OSError:
            return False


def _model_default_input(category, model_name, kind):
    """per-model layout 의 config.json 은 자기 기본 입력을 안다 (default_image / default_video) — task 표보다 정확하다
    (예: classification 중 person_pair 를 쓰는 model)."""
    from shared import dx_app_layout as _layout
    spec = _layout.load_config(DX_APP_ROOT, category, model_name)
    return (spec.get(f"default_{kind}") or "") if "variant" in spec else ""


# The Python runner logs this right before its frame loop (after the model loads and the source opens).
_PY_LOOP_STARTED = "Starting inference"


def _end_live_python_run(proc, stdout_file, budget_s, timeout):
    """A live Python run (camera · RTSP) has no frame limit and ends on SIGINT, printing its summary. Run it for
    budget_s counted from the start of its frame loop — model load and the RTSP connect took most of a budget
    counted from launch (2026-10-11: 3 and 23 frames measured in an A/B run)."""
    t0 = time.time()
    started = None
    while proc.poll() is None:
        now = time.time()
        if started is None:
            try:
                with open(stdout_file, "r", errors="ignore") as f:
                    if _PY_LOOP_STARTED in f.read():
                        started = now
            except OSError:
                pass
            if started is None and now - t0 > timeout:
                return
        elif now - started >= budget_s:
            proc.send_signal(signal.SIGINT)
            return
        time.sleep(0.1)


def run_inference(model_name, category, model_file, lang="cpp", variant="sync",
                  input_type="image", image_path=None, video_path=None,
                  device_id=None, conf_threshold=None, nms_threshold=None,
                  config_overrides=None,
                  upload_path=None, timeout=120, loop=None,
                  camera_id=None, rtsp_url=None,
                  save_output=True, image_base64=None, _multi=False, job_id=None):
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
        mp = resolve_model_path(model_file, DX_APP_ROOT)
        if not mp.exists(): return _err("model_not_found", f"Model file not found: {model_file}")
        _need = dxrt.needs_for_file(mp)
        if _need:
            return _err("needs_dxrt", f"This model needs DX-RT {_need} or later (.dxnn container v9) — "
                        f"the installed DX-RT reads up to v8.", needs_dxrt=_need)
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
    elif input_type == "image": inp = DX_APP_ROOT / (image_path or _model_default_input(category, model_name, "image")
                                                      or CAT_IMAGE.get(category, "sample/img/sample_street.jpg"))
    else: inp = DX_APP_ROOT / (video_path or _model_default_input(category, model_name, "video")
                               or CAT_VIDEO.get(category, "assets/videos/dance-group.mov"))
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
    env = dxrt.run_env({**os.environ, "QT_QPA_PLATFORM": "offscreen", "LD_LIBRARY_PATH": _ld})
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
    # Some Python async runners (keypoint / superpoint) deadlock on video: the async pipeline
    # never drains, so the process hangs until the timeout — a ~2-min dead spinner the user
    # reads as "infinite loading". Cap the wait and, on timeout, return a Sync-pointing note
    # instead of a generic error. (Runtime limitation; no dx-runtime change.)
    _async_video_hang_risk = ("async" in (variant or "") and input_type == "video" and not _is_live)
    if _async_video_hang_risk:
        timeout = min(timeout, 60)
    _video_save_dir = None
    _live_py_budget = None
    _img_save_dir = None
    run_lang = _effective_run_lang(lang, category, model_name, variant, input_type)
    tag_extra = ["--show-log"] if category in _STDOUT_TAG_CATS else []
    if run_lang == "cpp":
        bp = BUILD_DIR / f"{model_name}_{variant}"
        if not _is_executable_file(bp):
            # per-model layout: 예제가 있는 model 의 binary 는 그 model 전용이다 — 빌리지 않는다 (spec 2026-10-01)
            from shared import dx_app_layout as _layout
            _own = _layout.detect(DX_APP_ROOT) == _layout.PER_MODEL and _layout.find(DX_APP_ROOT, category, model_name)
            bp = None if _own else _find_fallback_binary(category, variant, build_dir=BUILD_DIR)
            if not bp:
                if _b64_tmp:
                    try: os.unlink(_b64_tmp)
                    except OSError: pass
                return _err("binary_not_found", f"Binary not found: {model_name}_{variant} — run build.sh")
        extra = list(tag_extra)
        # C++ --save renders an annotated H.264 (avc1) video — the same visualization the
        # terminal run_demo.sh shows — into <save-dir>/<run>/output.mp4 (found by
        # _find_saved_video). Enabled for video so the GUI can display it, not just FPS.
        # If a model makes the stock VideoWriter abort (the rare w/h=0 case), the run just
        # returns without a video (FPS still shown) — handled downstream, no studio crash.
        if input_type == "video":
            _video_save_dir = tempfile.mkdtemp(prefix="dxapp_video_", dir=_TMP)
            extra += ["-s", "--save-dir", _video_save_dir]
        elif input_type == "image":
            # Also enable --save for image runs: the PoseRunner family (pose / object_pose /
            # keypoint) ignores DXAPP_SAVE_IMAGE and only writes the annotated still into the
            # run-dir. We pick it up via _find_saved_image if DXAPP_SAVE_IMAGE stays empty, so
            # those tasks show a result image (matching their Python examples).
            _img_save_dir = tempfile.mkdtemp(prefix="dxapp_img_", dir=_TMP)
            extra += ["-s", "--save-dir", _img_save_dir]
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
        # live source (camera · RTSP) 에는 --loop 가 없다 ("--loop is not valid with --camera or --rtsp") — 끝없이
        # 돌다 SIGINT 를 받으면 성능 요약을 찍고 끝난다. 요청한 frame 수를 30 FPS 기준 시간으로 바꿔 그만큼 돌린다.
        if _is_live:
            _live_py_budget = max(1.0, _loop / 30.0)
        elif _loop != 1:
            py_extra += ["-l", str(_loop)]
        # Python 의 video source 는 디스크의 파일만 연다 — RTSP 를 --video 로 주면 "Input file not found: rtsp://…" 로
        # 끝났다 (2026-10-11 실사용 감사). runner 의 --rtsp · --camera 로 준다. (C++ 은 -v 를 OpenCV 가 열어 그대로 된다.)
        if input_type == "rtsp":
            py_input = ["--rtsp", _inp_str]
        elif input_type == "camera":
            py_input = ["--camera", str(_cam_idx)]
        else:
            py_input = [f"--{'image' if input_type=='image' else 'video'}", _inp_str]
        cmd = [_RUNTIME_PYTHON, str(pf), "--model", str(mp)] + py_input + ["--no-display"] + py_extra
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
            if job_id:
                # Async run: publish this run's live stdout + iteration total so
                # run_progress.poll_run can report frame progress. Best-effort; a failure
                # here must never break the run itself.
                try:
                    from dx_app.core import run_progress as _rp
                    _total = None
                    try:
                        if input_type == "video" and not _is_live and inp.exists():
                            import cv2 as _cv2t
                            _vc = _cv2t.VideoCapture(str(inp))
                            _fc = int(_vc.get(_cv2t.CAP_PROP_FRAME_COUNT)); _vc.release()
                            _total = _fc * _loop if _fc > 0 else None
                        else:
                            _total = _loop  # image/pair: one tag line per loop iteration
                    except Exception:
                        _total = None
                    _rp.register(job_id, _stdout_file, _loop, _total, proc, t0)
                except Exception:
                    pass
            if _live_py_budget:
                _end_live_python_run(proc, _stdout_file, _live_py_budget, timeout)
            proc.wait(timeout=timeout); elapsed = time.time() - t0
        if _multi: _multi_unregister(proc)
        with config._proc_lock: config._running_proc = None
        try:
            with open(_stdout_file, "r") as _f:
                stdout = _f.read()
        except Exception:
            stdout = ""
        hw1 = get_hw()
        res = {"exit_code": proc.returncode, "output": stdout[-4000:], "model": model_name,
               "category": category, "lang": lang, "variant": variant, "input_type": input_type,
               "elapsed_s": round(elapsed, 2), "timestamp": time.time(), "device_id": device_id, "hw_after": hw1}
        if run_lang != lang:
            res["lang_effective"] = run_lang
        if input_type == "video":
            res["video_save_mode"] = "python_save" if run_lang == "python" else "cpp_save"
        perf = _parse_perf(stdout); res["perf"] = perf
        res["fps"] = perf.get("overall_fps", ""); res["latency"] = perf.get("inference_latency", "")

        task = _parse_task_tags(stdout)
        res["task_tag"] = task["tag"]
        res["task_summary"] = task["summary"]
        res["task_frames"] = task["frame_count"]
        # Human-readable last predictions (e.g. classification top-k "tabby: 85.3%") — the only
        # visualizable result for tasks (classification/depth/pose/...) that emit NO output image.
        res["task_last_pred"] = task["last_pred"]

        # Recover the annotated still from the C++ --save run-dir when DXAPP_SAVE_IMAGE was
        # ignored (PoseRunner family: pose / object_pose / keypoint). Copy it onto res_img so
        # the normalisation pipeline below treats it like any other result image.
        if (input_type == "image" and _img_save_dir and res_img
                and (not os.path.exists(res_img) or os.path.getsize(res_img) == 0)):
            _si = _find_saved_image(_img_save_dir)
            if _si:
                try: shutil.copy2(str(_si), res_img)
                except OSError: pass
        # Result image — normalise to input resolution for CMP slider
        if res_img and os.path.exists(res_img) and os.path.getsize(res_img) > 0:
            output_only = (
                os.path.splitext(res_img)[0]
                + "_output_only"
                + os.path.splitext(res_img)[1]
            )
            has_output_only = (
                category in _SIDE_BY_SIDE_OUTPUT_CATS
                and os.path.exists(output_only)
                and os.path.getsize(output_only) > 0
            )
            if has_output_only:
                try:
                    shutil.copy2(output_only, res_img)
                    os.unlink(output_only)
                except OSError:
                    has_output_only = False
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
                    if (not has_output_only and category not in _PAIR_COMPARE_CATS and _inp_ar
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
                with open(res_img, "rb") as _f:
                    res["result_image"] = base64.b64encode(_f.read()).decode()
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
            if vo.exists() and vo.stat().st_size > 0 and _video_has_frames(vo):
                dst = OUTPUTS_DIR / f"result_{model_name}_{int(time.time())}.mp4"
                if _cvt_video(vo, dst): res["result_video_url"] = f"/outputs/{dst.name}"
                if vo == DX_APP_ROOT / "result.mp4":
                    try: vo.unlink(missing_ok=True)
                    except Exception: pass
            elif variant.startswith("async") or "async" in variant:
                # No playable video came back from an async run. Async video-save works for most
                # tasks (detection, etc.) but a few task runners (pose / keypoint / face) drop
                # their frames on the async pipeline's shutdown, leaving either a 0-frame MP4
                # (C++: size>0, unplayable) or no file at all (Python). Surface an honest note
                # pointing at Sync — which renders the identical annotated video — instead of a
                # broken/empty player. (Runtime limitation of those specific async examples.)
                # i18n key — the frontend localises it (6 languages) via T(). Includes the
                # "update coming" + "verify in terminal" guidance the message must carry.
                res["video_note"] = "async_empty_video"
                if vo == DX_APP_ROOT / "result.mp4":
                    try: vo.unlink(missing_ok=True)
                    except Exception: pass
        if proc.returncode != 0:
            res["error_hint"] = f"Exit code {proc.returncode}"
            # If no usable perf data was parsed, promote to hard error
            # so validation correctly counts this run as failed.

        if proc.returncode != 0 and not res.get("fps"):
                res["error"] = f"Process exited with code {proc.returncode}: {(res.get('output') or '')[-200:].strip()}"
                res["error_key"] = "process_exit"
        # exit 0 이어도 runner 가 [ERROR] 를 찍었으면 결과를 못 믿는다 — 이미지 한 장의 결과는 오류로 (release audit Z-1),
        # 영상은 FPS 가 남으므로 경고로만
        _runner_errs = runner_errors(stdout)
        if _runner_errs:
            res["runner_errors"] = _runner_errs[:5]
            if input_type == "image" and not res.get("error"):
                res["error"] = _runner_errs[0]
                res["error_key"] = "runner_error"
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
        if _async_video_hang_risk:
            return _err("async_video_stalled",
                        f"This async example stalled on video within {timeout}s — a known "
                        f"limitation of some async runners (the pipeline doesn't drain). "
                        f"Switch to Sync mode for this video (identical output).",
                        model=model_name)
        return _err("inference_timeout", f"Timeout ({timeout}s)", model=model_name)
    except Exception as e:
        if _multi and proc is not None: _multi_unregister(proc)
        return _err("inference_exception", str(e), model=model_name)
    finally:
        try:
            debug_log.log_exec("dx_app",
                               cmd if 'cmd' in dir() else None,
                               proc.returncode if proc is not None else None,
                               (time.time() - t0) * 1000.0 if 't0' in dir() else 0.0,
                               {"model_name": model_name, "category": category})
        except Exception:
            pass
        # Single cleanup point for every exit path (success/timeout/exception):
        # remove whatever temp artifacts this run created.
        for _p in (_stdout_file, tmp_config, _b64_tmp, res_img):
            if _p:
                try: os.unlink(_p)
                except OSError: pass
        for _save_dir in (_video_save_dir, _img_save_dir):
            if _save_dir:
                shutil.rmtree(_save_dir, ignore_errors=True)


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
                except Exception: continue
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
                except Exception: pass
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
                with open(tmp, "wb") as _f:
                    _f.write(base64.b64decode(r["result_image"]))
                cur = tmp
            except Exception: pass
    return results

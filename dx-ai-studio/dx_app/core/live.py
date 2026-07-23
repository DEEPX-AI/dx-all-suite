"""DX-APP live-mode inference — Xvfb-backed camera/RTSP inference jobs,
progress polling, stdout tag parsing, and process-lifecycle shutdown.

Layer 3 of the inference.py split (see dx_app/core/inference.py docstring for
the layered DAG): imports inference_exec + camera. shutdown_live_processes()
also stops run_multi/run_inference children (owned by inference.py, the top
layer) — that one upward dependency is resolved with a local import inside
the function body (see below) so module-load time stays acyclic.
"""

import os, re, time, uuid, subprocess, tempfile, threading, atexit
from pathlib import Path
from dx_app.core import config
from dx_app.core.config import DX_APP_ROOT, BUILD_DIR
from shared.runtime import ld_library_path
from dx_app.core.performance import _parse_perf
from dx_app.core.inference_exec import _err, _TMP
from dx_app.core.camera import _start_cam_mux, _stop_cam_mux, _ensure_xvfb, _XVFB_BASE, _UDP_BASE_PORT

_live_jobs = {}              # job_id -> {proc, log_file, start_time, slot_idx, ...}
_live_procs = {}             # slot_idx -> running inference proc
_live_procs_lock = threading.Lock()


def run_inference_live(model_name, category, model_file, lang="cpp", variant="sync",
                       input_type="camera", camera_id=None, rtsp_url=None,
                       device_id=None, slot_idx=0, n_total_slots=1, **kwargs):
    """Start inference WITHOUT --no-display on per-slot Xvfb. Returns {job_id}."""
    if not model_file:
        return _err("no_model_file", "No model file configured")

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
        if not mp.exists():
            return _err("model_not_found", f"Model file not found: {model_file}")

    if input_type == "camera":
        _cam_idx = int(camera_id) if camera_id is not None else 0
        if n_total_slots > 1:
            # Multi-slot: ffmpeg reads camera once → N UDP streams
            if slot_idx == 0:
                if not _start_cam_mux(_cam_idx, n_total_slots):
                    return _err("failed_camera_mux", "Failed to start camera multiplexer (ffmpeg). Is ffmpeg installed?")
            else:
                # Give ffmpeg a moment to stabilize for later slots
                time.sleep(0.5)
            _inp_str = f"udp://127.0.0.1:{_UDP_BASE_PORT + slot_idx}"
        else:
            # Single slot: use real camera directly
            _inp_str = f"/dev/video{_cam_idx}"
            if not Path(_inp_str).exists():
                return _err("camera_not_found", f"Camera device not found: {_inp_str}")
    elif input_type == "rtsp":
        if not rtsp_url:
            return _err("rtsp_required", "RTSP URL is required")
        _inp_str = rtsp_url
    else:
        return _err("live_mode_unsupported", "Live mode only supports camera/rtsp")

    with _live_procs_lock:
        old = _live_procs.get(slot_idx)
        if old and old.poll() is None:
            old.terminate()
            try: old.wait(timeout=3)
            except: old.kill()
        _live_procs.pop(slot_idx, None)

    _ensure_xvfb(slot_idx)

    _display = f":{_XVFB_BASE + slot_idx}"
    _loop = 999999  # effectively infinite until SIGTERM
    _ld = ld_library_path()
    env = {**os.environ, "DISPLAY": _display, "LD_LIBRARY_PATH": _ld}
    env.pop("QT_QPA_PLATFORM", None)  # allow real X11 rendering

    inf = "-v"
    if lang == "cpp":
        bp = BUILD_DIR / f"{model_name}_{variant}"
        if not bp.exists():
            return _err("binary_not_found", f"Binary not found: {bp.name}")
        if is_multi_model:
            cmd = [str(bp)] + model_args + [inf, _inp_str, "-l", str(_loop)]
        else:
            cmd = [str(bp), "-m", str(mp), inf, _inp_str, "-l", str(_loop)]
    else:
        return _err("live_cpp_only", "Live mode currently supports C++ only")

    job_id = str(uuid.uuid4())[:8]
    log_file = tempfile.mktemp(suffix=".log", dir=_TMP)

    with open(log_file, "w") as fout:
        proc = subprocess.Popen(cmd, stdout=fout, stderr=subprocess.STDOUT,
                                cwd=str(DX_APP_ROOT), env=env, text=True, close_fds=True)
    with _live_procs_lock:
        _live_procs[slot_idx] = proc
    # keep config._running_proc for slot 0 backward compat
    if slot_idx == 0:
        with config._proc_lock:
            config._running_proc = proc

    _live_jobs[job_id] = {
        "proc": proc, "log_file": log_file,
        "start_time": time.time(), "model_name": model_name,
        "category": category, "slot_idx": slot_idx,
    }
    print(f"[LIVE] Started job {job_id} slot={slot_idx} PID={proc.pid} model={model_name}")
    return {"job_id": job_id, "status": "started", "slot_idx": slot_idx}


def _parse_detections(stdout_text):
    """Parse [DET] class conf x1 y1 x2 y2 disp_w disp_h lines"""
    dets = []
    if not stdout_text: return dets
    for line in stdout_text.split("\n"):
        line = line.strip()
        if not line.startswith("[DET] "): continue
        parts = line[6:].rsplit(" ", 7)  # class conf x1 y1 x2 y2 dw dh
        if len(parts) < 8: continue
        try:
            cls = " ".join(parts[:-7])  # class name may have spaces
            vals = parts[-7:]
            conf = float(vals[0])
            x1, y1, x2, y2 = float(vals[1]), float(vals[2]), float(vals[3]), float(vals[4])
            dw, dh = float(vals[5]), float(vals[6])
            dets.append({"class": cls, "conf": conf, "bbox": [x1, y1, x2, y2], "disp_w": dw, "disp_h": dh})
        except: continue
    return dets


def _parse_task_tags(content):
    """Parse all task-specific stdout tags from C++ runner output.
    Returns dict: {tag: str, lines: list, frame_count: int, last_pred: list, summary: dict}
    """
    _lines = content.split("\n")
    _buckets = {
        "DET":   [l for l in _lines if l.startswith("[DET] ")],
        "CLS":   [l for l in _lines if l.startswith("[CLS]")],
        "SEG":   [l for l in _lines if l.startswith("[SEG]")],
        "ISEG":  [l for l in _lines if l.startswith("[ISEG] ")],
        "DEPTH": [l for l in _lines if l.startswith("[DEPTH] ")],
        "POSE":  [l for l in _lines if l.startswith("[POSE] ")],
        "FACE":  [l for l in _lines if l.startswith("[FACE] ")],
        "ALIGN": [l for l in _lines if l.startswith("[ALIGN] ")],
        "HAND":  [l for l in _lines if l.startswith("[HAND]")],
        "OBB":   [l for l in _lines if l.startswith("[OBB] ")],
        "3D":    [l for l in _lines if l.startswith("[3D] ")],
    }
    # Determine dominant tag
    tag = max(_buckets, key=lambda k: len(_buckets[k]))
    tag_lines = _buckets[tag]
    frame_count = len(tag_lines)
    if frame_count == 0:
        return {"tag": "", "lines": [], "frame_count": 0, "last_pred": [], "summary": {}}

    # Build last_pred (human-readable, last 5 lines)
    last_pred = []
    for tl in tag_lines[-5:]:
        try:
            if tag == "DET":
                parts = tl.split(); cls, conf = parts[1], float(parts[2])
                last_pred.append(f"{cls}: {conf*100:.0f}%")
            elif tag == "CLS":
                parts = tl[5:].split()  # after "[CLS] "
                for i in range(0, len(parts)-1, 2):
                    last_pred.append(f"{parts[i]}: {float(parts[i+1])*100:.1f}%")
                    if len(last_pred) >= 3: break
            elif tag == "SEG":
                parts = tl[5:].split()
                items = []
                for i in range(0, len(parts)-1, 2):
                    items.append(f"{parts[i]}: {parts[i+1]}%")
                last_pred.append(" | ".join(items[:5]))
            elif tag == "ISEG":
                parts = tl.split(); cls = parts[1]; conf = float(parts[2])
                last_pred.append(f"{cls}: {conf*100:.0f}%")
            elif tag == "DEPTH":
                parts = tl.split()
                last_pred.append(f"min={parts[1]} max={parts[2]} mean={parts[3]}")
            elif tag == "POSE":
                parts = tl.split()
                last_pred.append(f"{parts[1]} persons")
            elif tag == "FACE":
                parts = tl.split()
                last_pred.append(f"{parts[1]} faces")
            elif tag == "ALIGN":
                parts = tl.split()
                last_pred.append(f"yaw={parts[1]} pitch={parts[2]} roll={parts[3]}")
            elif tag == "HAND":
                parts = tl[6:].split()  # after "[HAND]"
                for i in range(0, len(parts)-1, 2):
                    last_pred.append(f"{parts[i]}: {float(parts[i+1])*100:.0f}%")
            elif tag == "OBB":
                parts = tl.split(); cls = parts[1]; conf = float(parts[2]); angle = parts[3]
                last_pred.append(f"{cls}: {conf*100:.0f}% {angle}°")
            elif tag == "3D":
                parts = tl.split(); cls = parts[1]; conf = float(parts[2])
                last_pred.append(f"{cls}: {conf*100:.0f}%")
        except:
            continue

    # Build summary (aggregated across all frames)
    summary = {}
    if tag == "DET" or tag == "ISEG" or tag == "OBB" or tag == "3D":
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 3:
                try:
                    cls = parts[1]; conf = float(parts[2])
                    if cls not in summary: summary[cls] = {"count": 0, "conf_sum": 0.0}
                    summary[cls]["count"] += 1; summary[cls]["conf_sum"] += conf
                except: pass
        for cls in summary:
            c = summary[cls]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0
    elif tag == "CLS":
        for tl in tag_lines:
            parts = tl[5:].split()
            if len(parts) >= 2:
                try:
                    cls = parts[0]; conf = float(parts[1])
                    if cls not in summary: summary[cls] = {"count": 0, "conf_sum": 0.0}
                    summary[cls]["count"] += 1; summary[cls]["conf_sum"] += conf
                except: pass
        for cls in summary: c = summary[cls]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0
    elif tag == "SEG":
        pct_sums = {}; n = 0
        for tl in tag_lines:
            parts = tl[5:].split()
            for i in range(0, len(parts)-1, 2):
                try:
                    cid = parts[i]; pct = float(parts[i+1])
                    if cid not in pct_sums: pct_sums[cid] = 0.0
                    pct_sums[cid] += pct
                except: pass
            n += 1
        if n > 0:
            summary = {cid: {"avg_pct": round(v / n, 1)} for cid, v in pct_sums.items()}
    elif tag == "DEPTH":
        mins, maxs, means = [], [], []
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 4:
                try: mins.append(float(parts[1])); maxs.append(float(parts[2])); means.append(float(parts[3]))
                except: pass
        if means:
            summary = {"min": round(min(mins), 2), "max": round(max(maxs), 2),
                       "mean": round(sum(means)/len(means), 2), "frames": len(means)}
    elif tag == "POSE":
        total_persons = 0
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 2:
                try: total_persons += int(parts[1])
                except: pass
        summary = {"total_detections": total_persons, "frames": frame_count,
                   "avg_per_frame": round(total_persons / frame_count, 1) if frame_count else 0}
    elif tag == "FACE":
        total_faces = 0
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 2:
                try: total_faces += int(parts[1])
                except: pass
        summary = {"total_detections": total_faces, "frames": frame_count,
                   "avg_per_frame": round(total_faces / frame_count, 1) if frame_count else 0}
    elif tag == "ALIGN":
        yaws, pitches, rolls = [], [], []
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 4:
                try: yaws.append(float(parts[1])); pitches.append(float(parts[2])); rolls.append(float(parts[3]))
                except: pass
        if yaws:
            summary = {"avg_yaw": round(sum(yaws)/len(yaws), 1),
                       "avg_pitch": round(sum(pitches)/len(pitches), 1),
                       "avg_roll": round(sum(rolls)/len(rolls), 1), "frames": len(yaws)}
    elif tag == "HAND":
        for tl in tag_lines:
            parts = tl[6:].split()
            for i in range(0, len(parts)-1, 2):
                try:
                    hand = parts[i]; conf = float(parts[i+1])
                    if hand not in summary: summary[hand] = {"count": 0, "conf_sum": 0.0}
                    summary[hand]["count"] += 1; summary[hand]["conf_sum"] += conf
                except: pass
        for h in summary: c = summary[h]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0

    return {"tag": tag, "lines": tag_lines, "frame_count": frame_count,
            "last_pred": last_pred, "summary": summary}


def poll_inference(job_id):
    """Poll live job for stats."""
    job = _live_jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}

    proc = job["proc"]
    running = proc.poll() is None
    elapsed = time.time() - job["start_time"]

    try:
        with open(job["log_file"], "r") as f:
            content = f.read()
    except:
        content = ""

    # ── Frame / detection counting (모든 태스크 태그 통합) ──
    task = _parse_task_tags(content)
    task_tag = task["tag"]
    tag_frame_count = task["frame_count"]

    # 분류(sync): "video - Top predictions:" 또는 "Top predictions:" 마커
    frame_markers = content.count("Top predictions:")
    if frame_markers == 0:
        frame_markers = content.count("video -")

    # 검출(async/sync): [DET] 줄 수를 detections으로 사용
    det_lines = task["lines"] if task_tag == "DET" else []
    det_count = len(det_lines)

    # Source FPS 파싱 (로그에서 추출)
    src_fps = 0.0
    m_fps = re.search(r"\[INFO\] Input source FPS:\s*([\d.]+)", content)
    if m_fps:
        try: src_fps = float(m_fps.group(1))
        except: pass

    is_det_mode = det_count > 0 and frame_markers == 0
    has_tag_mode = tag_frame_count > 0  # any task tag found
    # check if inference started (for models that don't print per-frame logs)
    has_started = "Starting" in content and src_fps > 0

    if has_tag_mode:
        # Tag-based frame counting (works for ALL task types)
        est_frames = tag_frame_count
        fps_est = round(est_frames / elapsed, 1) if elapsed > 0.5 else 0
        display_frames = est_frames
    elif frame_markers > 0:
        fps_est = round(frame_markers / elapsed, 1) if elapsed > 0.5 else 0
        display_frames = frame_markers
    elif has_started and running:
        # Models that don't print per-frame logs (restoration, embedding)
        est_frames = int(elapsed * src_fps) if elapsed > 0.5 else 0
        fps_est = round(est_frames / elapsed, 1) if elapsed > 0.5 else 0
        display_frames = est_frames
    else:
        fps_est = 0
        display_frames = 0

    # ── Last prediction / detection (태스크 태그 기반) ──
    last_pred = task["last_pred"] if task["last_pred"] else []
    if not last_pred and not has_tag_mode:
        # Fallback: legacy "Top predictions:" parsing
        lines = content.strip().split("\n")
        for i in range(len(lines) - 1, -1, -1):
            if "Top predictions:" in lines[i]:
                for j in range(i + 1, min(i + 6, len(lines))):
                    line = lines[j].strip()
                    if line and line[0].isdigit():
                        last_pred.append(line)
                    else:
                        break
                break

    # ── Class counts for detection mode (backward compat) ──
    class_counts = {}
    if is_det_mode:
        for dl in det_lines:
            parts = dl.split()
            if len(parts) >= 3:
                try:
                    cls = parts[1]
                    conf = float(parts[2])
                    if cls not in class_counts:
                        class_counts[cls] = {"count": 0, "conf_sum": 0.0}
                    class_counts[cls]["count"] += 1
                    class_counts[cls]["conf_sum"] += conf
                except: pass

    return {"running": running, "frames": display_frames,
            "det_count": det_count, "class_counts": class_counts,
            "elapsed": round(elapsed, 1), "fps_est": fps_est,
            "src_fps": src_fps, "is_det_mode": is_det_mode,
            "last_pred": last_pred,
            "task_tag": task_tag, "task_summary": task["summary"]}


def stop_inference_live(slot_idx=None):
    """Stop inference with SIGTERM. If slot_idx=None, stop all slots."""
    stopped = []
    with _live_procs_lock:
        targets = list(_live_procs.keys()) if slot_idx is None else [slot_idx]
        for s in targets:
            proc = _live_procs.get(s)
            if proc and proc.poll() is None:
                proc.terminate()
                stopped.append(s)
    if slot_idx == 0 or slot_idx is None:
        with config._proc_lock:
            if config._running_proc and config._running_proc.poll() is None:
                config._running_proc.terminate()
    # Stop camera multiplexer when stopping all slots
    if slot_idx is None:
        _stop_cam_mux()
    return {"status": "stopping", "slots": stopped}


def _terminate_proc(p, timeout=3):
    """SIGTERM then SIGKILL a subprocess handle; never raise."""
    try:
        if p and p.poll() is None:
            p.terminate()
            try: p.wait(timeout=timeout)
            except Exception:
                try: p.kill()
                except Exception: pass
    except Exception:
        pass


def shutdown_live_processes():
    """Terminate every live-mode child (live inference, Xvfb, ffmpeg cam-mux) plus
    any in-flight run_multi children. Called on server shutdown AND watchdog restart
    so nothing is left as an orphan (F-13 / F-14a). Safe to call repeatedly."""
    # Local import: inference.py (top layer) owns stop_multi/stop_inference, and
    # imports this module — importing it at module load time here would create a
    # circular import. Deferred so it only resolves when this function actually runs.
    from dx_app.core import inference as _inference
    from dx_app.core import camera
    try: stop_inference_live(None)
    except Exception: pass
    with _live_procs_lock:
        for slot, p in list(_live_procs.items()):
            _terminate_proc(p)
            _live_procs.pop(slot, None)
    with camera._xvfb_lock:
        for slot, p in list(camera._xvfb_procs.items()):
            _terminate_proc(p)
            camera._xvfb_procs.pop(slot, None)
    # ffmpeg camera multiplexer (also cleared by stop_inference_live, but be sure).
    with camera._cam_mux_lock:
        _terminate_proc(camera._cam_mux_proc)
        camera._cam_mux_proc = None
    try: _inference.stop_multi()
    except Exception: pass
    try: _inference.stop_inference()
    except Exception: pass


# Ensure children are reaped when the interpreter exits — this covers the
# SIGINT/SIGTERM shutdown path (DXServer._shutdown calls sys.exit, which runs
# atexit handlers) in addition to the watchdog restart path.
atexit.register(shutdown_live_processes)


def get_inference_result(job_id):
    """Get final result after live job completes."""
    job = _live_jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}

    proc = job["proc"]
    try:
        proc.wait(timeout=8)
    except:
        proc.kill()

    try:
        with open(job["log_file"], "r") as f:
            content = f.read()
    except:
        content = ""

    perf = _parse_perf(content)

    # Build task-specific summary from all tags
    task = _parse_task_tags(content)

    # Backward-compatible det_summary
    det_summary = task["summary"] if task["tag"] == "DET" else {}
    if task["tag"] == "DET":
        pass  # already in correct format
    elif not det_summary:
        # Legacy fallback
        for line in content.split("\n"):
            if not line.startswith("[DET] "): continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    cls = parts[1]; conf = float(parts[2])
                    if cls not in det_summary:
                        det_summary[cls] = {"count": 0, "conf_sum": 0.0}
                    det_summary[cls]["count"] += 1; det_summary[cls]["conf_sum"] += conf
                except: pass
        for cls in det_summary:
            c = det_summary[cls]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0

    result = {
        "job_id": job_id, "exit_code": proc.returncode,
        "model": job["model_name"], "category": job["category"],
        "slot_idx": job.get("slot_idx", 0),
        "perf": perf,
        "fps": perf.get("overall_fps", ""),
        "latency": perf.get("inference_latency", ""),
        "total_frames": perf.get("total_frames", ""),
        "total_time": perf.get("total_time", ""),
        "elapsed_seconds": round(time.time() - job["start_time"], 1),
        "det_summary": det_summary,
        "task_tag": task["tag"],
        "task_summary": task["summary"],
        "task_frames": task["frame_count"],
        "output": content[-4000:],
    }

    slot = job.get("slot_idx", 0)
    try: os.unlink(job["log_file"])
    except: pass
    _live_jobs.pop(job_id, None)
    with _live_procs_lock:
        _live_procs.pop(slot, None)
    if slot == 0:
        with config._proc_lock:
            config._running_proc = None

    return result

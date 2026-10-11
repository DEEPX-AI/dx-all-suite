"""DX-APP live-mode inference — Xvfb-backed camera/RTSP inference jobs,
progress polling, stdout tag parsing, and process-lifecycle shutdown.

Layer 3 of the inference.py split (see dx_app/core/inference.py docstring for
the layered DAG): imports inference_exec + camera. shutdown_live_processes()
also stops run_multi/run_inference children (owned by inference.py, the top
layer) — that one upward dependency is resolved with a local import inside
the function body (see below) so module-load time stays acyclic.
"""

import os, re, math, shutil, time, uuid, subprocess, tempfile, threading, atexit
from pathlib import Path
from dx_app.core import config
from dx_app.core.config import DX_APP_ROOT, BUILD_DIR, resolve_model_path
from shared.runtime import ld_library_path
from shared import dxrt
from dx_app.core.performance import _parse_perf
from dx_app.core.inference_exec import _err, _TMP
from dx_app.core.camera import _start_cam_mux, _stop_cam_mux, _ensure_xvfb, _XVFB_BASE, _UDP_BASE_PORT, _XVFB_RES

_live_jobs = {}              # job_id -> {proc, log_file, start_time, slot_idx, ...}
_live_procs = {}             # slot_idx -> running inference proc
_live_procs_lock = threading.Lock()


def _video_frame_count(path):
    """영상의 프레임 수 (ffprobe, 컨테이너의 값 → 없으면 packet 을 센다). 모르면 None. live 의 'Loop' 기준 하한에 쓴다 —
    많은 runner (segmentation 등) 가 'Total frames' 를 찍지 않는다."""
    import shutil
    if not shutil.which("ffprobe") or not Path(path).is_file():
        return None
    for extra in ([], ["-count_packets"]):
        field = "nb_read_packets" if extra else "nb_frames"
        try:
            out = subprocess.run(["ffprobe", "-v", "error", *extra, "-select_streams", "v:0",
                                  "-show_entries", f"stream={field}", "-of", "csv=p=0", str(path)],
                                 capture_output=True, text=True, timeout=15).stdout.strip().split(",")[0]
            n = int(out)
            if n > 0:
                return n
        except (ValueError, OSError, subprocess.SubprocessError):
            continue
    return None


def run_inference_live(model_name, category, model_file, lang="cpp", variant="sync",
                       input_type="camera", camera_id=None, rtsp_url=None, video_path=None,
                       device_id=None, slot_idx=0, n_total_slots=1, **kwargs):
    """Start inference WITHOUT --no-display on per-slot Xvfb. Returns {job_id}.

    input_type="video" streams a video FILE the same live way as camera/rtsp: the C++
    example renders annotated frames to the Xvfb display (looped, -l 999999) and
    capture_live_frame screen-grabs them into the MJPEG stream — so Run Demo video
    shows frames instantly like DX Stream, instead of the batch save-then-return path.
    Performance stays the example's own stdout log (poll_inference parses it)."""
    if not model_file:
        return _err("no_model_file", "No model file configured")

    # Live streaming needs a virtual display (Xvfb), libX11/libxcb to drive and grab it and Pillow to encode the
    # frames — the only non-stdlib pieces of the live path (all OS packages). Without them frame
    # capture is blank and _ensure_xvfb raises deep inside, surfacing as a cryptic 500. Fail fast
    # + actionable. (No mss — tests/dx_app/test_live_grab.py.)
    import shutil
    from dx_app.core import camera as _camera
    _missing = []
    if not shutil.which("Xvfb"):
        _missing.append("Xvfb (sudo apt install xvfb)")
    if _camera._xlib() is None or _camera._xcb() is None:
        _missing.append("libX11 / libxcb (sudo apt install libx11-6)")
    try:
        import PIL  # noqa: F401
    except Exception:
        _missing.append("Pillow (sudo apt install python3-pil)")
    if _missing:
        return _err("live_deps_missing", "Live streaming requires: " + ", ".join(_missing))

    # 영상을 받지 않는 runner (arcface · CLIP · ReID · VPR · DOPE · SFA3D …) 는 -v 를 거부하고 바로 끝난다 —
    # 검은 화면만 남으므로 이유와 함께 거절한다 (연속 실행의 camera · RTSP 는 UI 가 막지 않는다)
    if config.model_image_only(category, model_name):
        return _err("live_image_only", "This model takes still images only — live (camera / RTSP / video) "
                    "is not supported. Use Run Inference with an image.")

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
        if not mp.exists():
            return _err("model_not_found", f"Model file not found: {model_file}")

    if input_type == "camera":
        _cam_idx = int(camera_id) if camera_id is not None else 0
        if n_total_slots > 1:
            # Multi-slot: ffmpeg reads camera once → N UDP streams
            if slot_idx == 0:
                if not _start_cam_mux(_cam_idx, n_total_slots):
                    from dx_app.core.camera import cam_mux_last_error
                    why = cam_mux_last_error() or ("ffmpeg not found" if not shutil.which("ffmpeg") else "")
                    return _err("failed_camera_mux", "Failed to share the camera between slots (ffmpeg)"
                                + (f": {why}" if why else ""))
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
    elif input_type == "video":
        if not video_path:
            return _err("video_required", "Video path is required")
        _vp = Path(video_path)
        if not _vp.is_absolute():
            _vp = DX_APP_ROOT / video_path
        if not _vp.exists():
            return _err("input_not_found", f"Video not found: {video_path}")
        _inp_str = str(_vp)
    else:
        return _err("live_mode_unsupported", "Live mode only supports camera/rtsp/video")

    with _live_procs_lock:
        old = _live_procs.get(slot_idx)
        if old and old.poll() is None:
            old.terminate()
            try: old.wait(timeout=3)
            except Exception: old.kill()
        _live_procs.pop(slot_idx, None)

    _ensure_xvfb(slot_idx)

    _display = f":{_XVFB_BASE + slot_idx}"
    _loop = 999999  # effectively infinite until SIGTERM
    _ld = ld_library_path()
    env = dxrt.run_env({**os.environ, "DISPLAY": _display, "LD_LIBRARY_PATH": _ld})
    env.pop("QT_QPA_PLATFORM", None)  # allow real X11 rendering
    # 프레임 수를 runner 가 직접 알린다 ([PROGRESS], dx_app fix/studio-live-findings). dx_app 은 창을 화면의
    # 절반으로 열므로 Xvfb 의 두 배를 화면이라 알려 창이 처음부터 Xvfb 를 채우게 한다 (창 맞추기는 그대로 둔다).
    env["DXAPP_PROGRESS"] = "1"
    _xw, _xh = (int(v) for v in _XVFB_RES.split("x")[:2])
    env["DXAPP_SCREEN_W"], env["DXAPP_SCREEN_H"] = str(2 * _xw), str(2 * _xh)

    # SDKREQ-529 부터 runner 는 -v 경로가 디스크에 있어야 한다 — RTSP 와 여러 slot 카메라의 udp:// 는 "Input file not
    # found" 로 바로 끝나 검은 화면만 남았다 (2026-10-11). URL 은 -r (C++ rtsp_url — OpenCV 가 연다).
    inf = "-r" if "://" in _inp_str else "-v"
    if lang == "cpp":
        bp = BUILD_DIR / f"{model_name}_{variant}"
        if not bp.exists():
            return _err("binary_not_found", f"Binary not found: {bp.name}")
        if is_multi_model:
            cmd = [str(bp)] + model_args + [inf, _inp_str, "-l", str(_loop)]
        else:
            cmd = [str(bp), "-m", str(mp), inf, _inp_str, "-l", str(_loop)]
        # runner 는 [DET] · [CLS] 같은 프레임별 줄을 --show-log 일 때만 찍는다 — 없으면 poll 이 frames 0 · FPS 0
        # (main 01b7727 · per-model 8d0b748 의 모든 runner 가 받는다; 계약: tests/dx_app/test_live_display.py)
        cmd.append("--show-log")
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
        "total_frames": _video_frame_count(_inp_str) if input_type == "video" else None,
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
        except Exception: continue
    return dets


# 점수는 숫자 하나로 끝나야 한다 — async callback 들이 동시에 써서 섞인 줄 ('3.50273.5913') 은 건너뛴다
_CLS_VERBOSE_RE = re.compile(r'^\s*(\d+)\.\s*\(class\s+(\d+)\)\s*:\s*(-?\d+(?:\.\d+)?)[ \t]*$', re.M)

def _softmax(xs):
    if not xs:
        return []
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    s = sum(exps) or 1.0
    return [e / s for e in exps]

def _parse_classification_frames(content):
    """Turn the C++ classifier's verbose '  N. (class IDX): SCORE' lines into per-frame
    top-K prediction blocks and softmax each frame's SCORES into real probabilities.

    The machine `[CLS]` tag only carries the raw top-K scores (logits) with NO class index
    — pairing consecutive scores as (label, prob) produced garbage like class "4.8052" @
    469.8%. The verbose lines are the only place the class index appears, so parse those.
    Rank "1." delimits a new frame. Returns [[(idx, prob), ...], ...] (one list per frame)."""
    frames = []
    cur = []
    for m in _CLS_VERBOSE_RE.finditer(content or ""):
        rank = int(m.group(1)); idx = m.group(2); score = float(m.group(3))
        if rank == 1 and cur:
            frames.append(cur); cur = []
        cur.append((idx, score))
    if cur:
        frames.append(cur)
    out = []
    for fr in frames:
        probs = _softmax([s for _, s in fr])
        out.append([(idx, p) for (idx, _), p in zip(fr, probs)])
    return out

_PER_OBJECT_TAGS = ("DET", "OBB", "ISEG")


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
    if tag in _PER_OBJECT_TAGS:
        # [DET] · [OBB] · [ISEG] 는 객체마다 한 줄이고 프레임 번호가 없다. 한 프레임의 객체는 신뢰도 내림차순이므로
        # 신뢰도가 다시 오르는 곳이 새 프레임 (실측 yolov12-n 478/478 · RT-DETR 190/190 · OBB 621/621, ISEG 582/719).
        # 객체 없는 프레임 · 객체 하나인 프레임이 이어지는 곳은 못 센다 — 하한.
        confs = []
        for tl in tag_lines:
            try:
                confs.append(float(tl.split()[2]))
            except (IndexError, ValueError):
                continue
        if confs:
            frame_count = 1 + sum(1 for a, b in zip(confs, confs[1:]) if b > a)

    # Build last_pred (human-readable, last 5 lines)
    last_pred = []
    for tl in tag_lines[-5:]:
        try:
            if tag == "DET":
                parts = tl.split(); cls, conf = parts[1], float(parts[2])
                last_pred.append(f"{cls}: {conf*100:.0f}%")
            elif tag == "CLS":
                pass  # handled after the loop via _parse_classification_frames (needs labels)
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
        except Exception:
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
                except Exception: pass
        for cls in summary:
            c = summary[cls]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0
    elif tag == "CLS":
        # The [CLS] tag is scores-only (no class index); labels live in the verbose
        # "(class IDX): SCORE" lines. Parse those, softmax per frame, aggregate by class.
        cls_frames = _parse_classification_frames(content)
        for fr in cls_frames:
            for idx, prob in fr:
                key = f"class {idx}"
                if key not in summary: summary[key] = {"count": 0, "conf_sum": 0.0}
                summary[key]["count"] += 1; summary[key]["conf_sum"] += prob
        for cls in summary:
            c = summary[cls]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0
        # last_pred from the final frame's top-3 (probabilities, not raw logits)
        if cls_frames:
            last_pred = [f"class {idx}: {prob*100:.1f}%" for idx, prob in cls_frames[-1][:3]]
    elif tag == "SEG":
        pct_sums = {}; n = 0
        for tl in tag_lines:
            parts = tl[5:].split()
            for i in range(0, len(parts)-1, 2):
                try:
                    cid = parts[i]; pct = float(parts[i+1])
                    if cid not in pct_sums: pct_sums[cid] = 0.0
                    pct_sums[cid] += pct
                except Exception: pass
            n += 1
        if n > 0:
            summary = {cid: {"avg_pct": round(v / n, 1)} for cid, v in pct_sums.items()}
    elif tag == "DEPTH":
        mins, maxs, means = [], [], []
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 4:
                try: mins.append(float(parts[1])); maxs.append(float(parts[2])); means.append(float(parts[3]))
                except Exception: pass
        if means:
            summary = {"min": round(min(mins), 2), "max": round(max(maxs), 2),
                       "mean": round(sum(means)/len(means), 2), "frames": len(means)}
    elif tag == "POSE":
        total_persons = 0
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 2:
                try: total_persons += int(parts[1])
                except Exception: pass
        summary = {"total_detections": total_persons, "frames": frame_count,
                   "avg_per_frame": round(total_persons / frame_count, 1) if frame_count else 0}
    elif tag == "FACE":
        total_faces = 0
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 2:
                try: total_faces += int(parts[1])
                except Exception: pass
        summary = {"total_detections": total_faces, "frames": frame_count,
                   "avg_per_frame": round(total_faces / frame_count, 1) if frame_count else 0}
    elif tag == "ALIGN":
        yaws, pitches, rolls = [], [], []
        for tl in tag_lines:
            parts = tl.split()
            if len(parts) >= 4:
                try: yaws.append(float(parts[1])); pitches.append(float(parts[2])); rolls.append(float(parts[3]))
                except Exception: pass
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
                except Exception: pass
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
    except Exception:
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
        except Exception: pass

    is_det_mode = det_count > 0 and frame_markers == 0
    has_tag_mode = tag_frame_count > 0  # any task tag found

    # 영상이 한 바퀴 돌 때마다 찍히는 'Loop k/N' — 끝난 바퀴 × 총 프레임은 실제 처리한 프레임의 하한.
    # 많은 runner (segmentation 등) 가 'Total frames' 를 찍지 않아 시작할 때 잰 영상 길이를 쓴다.
    loops = [int(x) for x in re.findall(r"\bLoop (\d+)/\d+", content)]
    m_total = re.search(r"\[INFO\] Total frames:\s*(\d+)", content)
    total = int(m_total.group(1)) if m_total else job.get("total_frames")
    done = (max(loops) - 1) if loops else 0
    loop_frames = done * int(total) if total and done > 0 else None

    # dx_app 의 runner 가 DXAPP_PROGRESS=1 로 찍는 '[PROGRESS] frames=N' 이 있으면 그것이 프레임 수다 —
    # 아래 추정 (태그 · Loop) 은 그것이 없는 runner (main 01b7727) 를 위한 것
    progress = [int(x) for x in re.findall(r"^\[PROGRESS\] frames=(\d+)", content, re.M)]

    if progress:
        frame_basis, display_frames = "progress", max(progress)
    elif has_tag_mode or frame_markers > 0:
        frame_basis = "tag"
        display_frames = tag_frame_count if has_tag_mode else frame_markers
        # 태그가 일부 프레임에만 찍히는 task (hand detector 는 손이 보일 때만) 는 Loop 쪽이 더 크다
        if loop_frames and loop_frames > display_frames:
            frame_basis, display_frames = "loop", loop_frames
    elif loop_frames:
        frame_basis, display_frames = "loop", loop_frames
    else:
        # segmentation · depth · denoise · SR · matting · anomaly 의 runner 는 프레임별 줄이 없다. 예전에는
        # '원본 FPS × 경과' 를 프레임이라 했다 (PP-Matting: 실제 0.2 FPS 가 24 FPS 로) — 모르면 모른다 (None).
        frame_basis, display_frames = "none", None
    if display_frames is None:
        fps_est = None
    else:
        fps_est = round(display_frames / elapsed, 1) if elapsed > 0.5 else 0

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
                except Exception: pass

    return {"running": running, "frames": display_frames, "frame_basis": frame_basis,
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
    # 멈춘 slot 의 Xvfb 도 끈다 — 예전에는 서버가 끝날 때까지 남았다 (release audit A-15)
    from dx_app.core import camera as _camera
    for s in targets:
        _camera.stop_xvfb(s)
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
    except Exception:
        proc.kill()

    try:
        with open(job["log_file"], "r") as f:
            content = f.read()
    except Exception:
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
                except Exception: pass
        for cls in det_summary:
            c = det_summary[cls]; c["conf_avg"] = round(c["conf_sum"] / c["count"], 3) if c["count"] else 0

    # runner 가 스스로 끝났다 — 영상을 거부했거나 (config.json 과 C++ 예제가 다른 CLIP ViT-B/32 등) 죽었다.
    # 'error' 는 API 오류 자리라 (UI 가 합성 결과로 덮는다) run_error 로 싣는다.
    run_error_key = run_error = None
    if "Interrupted by user" not in content and not perf.get("overall_fps") and not task["frame_count"]:
        plain = re.sub(r"\x1b\[[0-9;]*m", "", content)
        hint = next((l.strip() for l in plain.splitlines() if "image-only" in l or "supports image input only" in l), None)
        err = next((l.strip() for l in plain.splitlines()
                    if re.search(r"\[ERROR\]|does not exist|Abort|Segmentation|terminate called", l)), None)
        if hint:
            run_error_key, run_error = "live_image_only", hint
        elif err or (proc.returncode not in (0, None)):
            run_error_key = "live_runner_failed"
            run_error = err or f"The example exited with code {proc.returncode}"

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
    if run_error_key:
        result["run_error_key"], result["run_error"] = run_error_key, run_error

    slot = job.get("slot_idx", 0)
    try: os.unlink(job["log_file"])
    except Exception: pass
    _live_jobs.pop(job_id, None)
    with _live_procs_lock:
        _live_procs.pop(slot, None)
    if slot == 0:
        with config._proc_lock:
            config._running_proc = None

    return result

#!/usr/bin/env python3
"""Exhaustive dx_stream Pipeline-BUILDER streaming verification.

Runs every meaningful (model x structure) combination through the SAME path the
GUI Pipeline Builder uses — ``core.pipeline.pipeline_json_to_gst(builder_json)``
— then streams it headlessly (gst-launch -> JPEG frame on fd 1) and records
PASS/FAIL/SKIP. A produced JPEG frame proves the full chain actually ran on the
NPU (decode -> dxpreprocess -> dxinfer -> dxpostprocess -> dxosd -> encode).

WHY per-combo service restart:
  Tearing a pipeline down can crash/destabilise the dxrtd daemon, and NPU
  Device 1 (FW v2.7.0) intermittently hits "Firmware Timeout / Device not
  response" under load. To get UNCONTAMINATED per-combo truth we restart
  dxrt.service before each run (needs passwordless `sudo systemctl restart
  dxrt.service`). Without this, a single bad combo cascades into false failures.

PRECONDITIONS (run only when BOTH NPUs are free — no other agent using them):
  - `sudo -n systemctl restart dxrt.service` must work (passwordless), OR pass
    --no-restart to skip isolation (results then subject to cascade noise).
  - dx-runtime/dx_stream built; models in samples/models; postproc libs in
    /usr/local/share/gstdxstream/lib; NPU present (/dev/dxrt*).

USAGE:
  python3 verify_all_streaming.py --full          # every (model x structure) ~120 combos, ~80 min
  python3 verify_all_streaming.py --quick         # representative ~20 combos
  python3 verify_all_streaming.py --no-restart    # skip per-combo dxrt restart (faster, noisier)
  python3 verify_all_streaming.py --timeout 30    # first-frame timeout per combo (s)

OUTPUT: writes a timestamped report (md + csv) next to this script.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DX_STREAM = HERE.parent

from dx_stream.core import mjpeg                                      # noqa: E402
from dx_stream.core.pipeline import pipeline_json_to_gst, detect_encoder  # noqa: E402
from dx_stream.core.config import VIDEOS_DIR, MODELS_DIR             # noqa: E402
from dx_stream.core.mjpeg import get_sink_str, build_mjpeg_pipeline  # noqa: E402

LIB = "/usr/local/share/gstdxstream/lib"


def _ensure_display():
    """DeepX HW elements (DxScale/DxConvert) allocate GPU/DMA-buf buffers and need an
    active DRM master — a running X/Wayland session. Headless (no DISPLAY) makes the
    userspace amdgpu accel query fail with EACCES and the pipeline dies at buffer map.
    Auto-attach to the running session so `ssh` / service runs work like the GUI does."""
    import os
    import glob
    if os.environ.get("DISPLAY"):
        return
    socks = sorted(glob.glob("/tmp/.X11-unix/X*"))
    if not socks:
        return
    os.environ["DISPLAY"] = ":" + socks[0].split("/X")[-1]
    if not os.environ.get("XAUTHORITY"):
        for cand in sorted(glob.glob("/run/user/*/gdm/Xauthority")) + \
                [os.path.expanduser("~/.Xauthority")]:
            if os.path.exists(cand):
                os.environ["XAUTHORITY"] = cand
                break

# postproc is either ("lib", "<lib_basename>", "<func>") or ("config", "<dir>", None)
# Keys are the actual sample-model file names from model_list.json v2_4_0
# (<name>_640x640.dxnn; efficientnet is 256x256). PPU models keep their names.
M = {
    "yolo26-n_640x640.dxnn":         (("lib", "yolo26od", "PostProcess"),     "od",       (640, 640)),
    "yolo11-n_640x640.dxnn":         (("lib", "yolov11", "PostProcess"),      "od",       (640, 640)),
    "yolov5-s_640x640.dxnn":         (("lib", "yolov5s_6", "PostProcess"),    "od",       (640, 640)),
    "yolov7_640x640.dxnn":           (("lib", "yolov7", "PostProcess"),       "od",       (640, 640)),
    "yolov8-n_640x640.dxnn":         (("lib", "yolov8n", "PostProcess"),      "od",       (640, 640)),
    "yolov9-s_640x640.dxnn":         (("lib", "yolov9s", "PostProcess"),      "od",       (640, 640)),
    "yolox-s_640x640.dxnn":          (("lib", "yoloxs", "PostProcess"),       "od",       (640, 640)),
    "yolov5-s-face_640x640.dxnn":    (("lib", "yolov5s_face", "PostProcess"), "face",     (640, 640)),
    "scrfd-500m_640x640.dxnn":       (("lib", "scrfd500m", "PostProcess"),    "face",     (640, 640)),
    "yolo26-n-pose_640x640.dxnn":    (("lib", "yolo26pose", "PostProcess"),   "pose",     (640, 640)),
    "yolov8-m-pose_640x640.dxnn":    (("lib", "yolov8m_pose", "PostProcess"), "pose",     (640, 640)),
    "yolo26-n-seg_640x640.dxnn":     (("lib", "yolo26seg", "PostProcess"),    "seg",      (640, 640)),
    "efficientnet-lite0_256x256.dxnn": (("lib", "object_class", "PostProcess"), "cls",   (256, 256)),
    "yolov5-s_640x640_ppu.dxnn":     (("config", "YoloV5S_PPU", None),        "od-ppu",   None),
    "SCRFD500M_PPU.dxnn":            (("lib", "ppu", "SCRFD500M_PPU"),        "face-ppu", (640, 640)),
    "YOLOV5Pose_PPU.dxnn":           (("lib", "ppu", "YOLOV5Pose_PPU"),       "pose-ppu", (640, 640)),
}

# Videos extract into a sample_videos/ subdir → search recursively.
VIDS = sorted(f"file://{p}" for p in VIDEOS_DIR.rglob("*.mp4")) or [
    f"file://{VIDEOS_DIR}/sample_videos/boat.mp4"]
V0 = VIDS[0]


def _nodes_edges(seq):
    nodes, edges = [], []
    for i, (t, p) in enumerate(seq):
        nid = f"n{i}"
        nodes.append({"id": nid, "type": t, "properties": p})
        if i:
            edges.append({"from": f"n{i-1}", "to": nid})
    return nodes, edges


def _infer_block(model):
    """Return the [pre, infer, post] node specs for a model (standard or PPU-config)."""
    pp, task, size = M[model]
    if pp[0] == "config":
        cfg = pp[1]
        return [
            ("DxPreprocess", {"config-file-path": f"{cfg}/preprocess_config.json"}),
            ("DxInfer", {"config-file-path": f"{cfg}/inference_config.json"}),
            ("DxPostprocess", {"config-file-path": f"{cfg}/postprocess_config.json"}),
        ], task
    w, h = size
    _, lib, func = pp
    return [
        ("DxPreprocess", {"preprocess-id": 1, "resize-width": w, "resize-height": h}),
        ("DxInfer", {"preprocess-id": 1, "inference-id": 1, "model-path": str(MODELS_DIR / model)}),
        ("DxPostprocess", {"inference-id": 1,
                           "library-file-path": f"{LIB}/libpostprocess_{lib}.so",
                           "function-name": func}),
    ], task


def s_linear(model, tail=None, head=None):
    # head = elements placed in the PREPROCESS position (after decode, before dxpreprocess).
    # DxScale/DxConvert are HW-accelerated preprocess elements and MUST go here — placing
    # them after DxOsd makes DxOsd negotiate a HW buffer it cannot CPU-map for overlay
    # drawing ("Failed to map video frame for OSD rendering"). tail = post-OSD elements
    # (e.g. DxRate) that operate on the already-rendered stream.
    blk, _ = _infer_block(model)
    seq = [("urisourcebin", {"uri": V0}), ("decodebin", {})] + (head or []) + blk + [("DxOsd", {})] + (tail or [])
    n, e = _nodes_edges(seq)
    return {"nodes": n, "edges": e}


def s_tracker(model):
    blk, _ = _infer_block(model)
    seq = [("urisourcebin", {"uri": V0}), ("decodebin", {})] + blk + \
          [("DxTracker", {"config-file-path": "tracker_config.json"}), ("DxOsd", {})]
    n, e = _nodes_edges(seq)
    return {"nodes": n, "edges": e}


def s_multi(model, ch):
    nodes, edges = [], []
    for i in range(ch):
        pfx = f"s{i}_"
        blk, _ = _infer_block(model)
        # DxScale in preprocess position (input scaling); compositor lays out the OSD output.
        seq = [("urisourcebin", {"uri": VIDS[i % len(VIDS)]}), ("decodebin", {}),
               ("DxScale", {"width": 640, "height": 360})] + blk + [("DxOsd", {})]
        for j, (t, p) in enumerate(seq):
            nid = f"{pfx}{j}"
            nodes.append({"id": nid, "type": t, "properties": p})
            if j:
                edges.append({"from": f"{pfx}{j-1}", "to": nid})
        edges.append({"from": f"{pfx}{len(seq)-1}", "to": "comp"})
    nodes.append({"id": "comp", "type": "compositor", "properties": {}})
    return {"nodes": nodes, "edges": edges}


# Models that cannot run as a standalone PRIMARY (single-network) pipeline:
#  - efficientnet-lite0: classification; libpostprocess_object_class.so is a SECONDARY-mode
#    postproc (writes object_meta from an upstream detector's crop). No primary reference
#    exists in dx_stream/pipelines. Driving it as a primary is a harness misuse.
#  - scrfd-500m (non-PPU): dx-runtime BUG — libpostprocess_scrfd500m.so NULL-derefs the
#    (primary-mode NULL) object_meta and SIGSEGVs. Crashes dx_stream's OWN reference
#    run_SCRFD500M.sh (its libpostprocess_scrfd500m.so dereferences the primary-mode
#    NULL object_meta). Use SCRFD500M_PPU instead, which works.
PRIMARY_UNSUPPORTED = {
    "efficientnet-lite0_256x256.dxnn": "classification postproc is secondary-mode only",
    "scrfd-500m_640x640.dxnn": "libpostprocess_scrfd500m.so SIGSEGVs in primary mode (NULL object_meta deref); use SCRFD500M_PPU",
}


def build_matrix(full):
    """Yield (label, builder_json). `full` -> every model x structure; else representative."""
    combos = []
    models = [m for m in M.keys() if m not in PRIMARY_UNSUPPORTED]
    for m, why in PRIMARY_UNSUPPORTED.items():
        print(f"[skip] {m}: {why}", flush=True)
    rep_models = ["yolo26-n_640x640.dxnn", "yolov5-s_640x640_ppu.dxnn", "yolov5-s-face_640x640.dxnn",
                  "SCRFD500M_PPU.dxnn", "yolo26-n-pose_640x640.dxnn", "yolo26-n-seg_640x640.dxnn"]
    use = models if full else rep_models

    # 1) linear per model
    for m in use:
        combos.append((f"linear::{m}", s_linear(m)))
    # 2) tail variants (scale/rate/convert) per model
    if full:
        for m in use:
            combos.append((f"linear+scale::{m}", s_linear(m, head=[("DxScale", {"width": 960, "height": 540})])))
            combos.append((f"linear+rate::{m}", s_linear(m, [("DxRate", {"framerate": 15})])))
            combos.append((f"linear+convert::{m}", s_linear(m, head=[("DxConvert", {})])))
    else:
        combos.append(("linear+scale::yolo26-n_640x640.dxnn", s_linear("yolo26-n_640x640.dxnn", head=[("DxScale", {"width": 960, "height": 540})])))
        combos.append(("linear+rate::yolo26-n_640x640.dxnn", s_linear("yolo26-n_640x640.dxnn", [("DxRate", {"framerate": 15})])))
    # 3) tracker (detection models)
    for m in (use if full else ["yolov5-s_640x640_ppu.dxnn"]):
        if M[m][1] in ("od", "od-ppu", "face", "face-ppu"):
            combos.append((f"tracker::{m}", s_tracker(m)))
    # 4) multistream 2ch + 4ch
    for m in (use if full else ["yolov5-s_640x640_ppu.dxnn", "yolo26-n_640x640.dxnn"]):
        combos.append((f"multi2ch::{m}", s_multi(m, 2)))
        if full:
            combos.append((f"multi4ch::{m}", s_multi(m, 4)))
    return combos


def restart_service():
    try:
        subprocess.run(["sudo", "-n", "systemctl", "restart", "dxrt.service"],
                       check=False, capture_output=True, timeout=30)
    except Exception:
        return False
    for _ in range(20):
        r = subprocess.run(["systemctl", "is-active", "dxrt.service"],
                           capture_output=True, text=True)
        if r.stdout.strip() == "active":
            time.sleep(4)
            return True
        time.sleep(1)
    return False


def run_combo(label, defn, timeout, restart):
    try:
        gst = pipeline_json_to_gst(defn)
    except Exception as e:
        return ("BUILD_FAIL", str(e)[:300], None)
    src_req = sum(1 for n in defn["nodes"] if n["type"] in ("urisourcebin", "rtspsrc"))
    src_got = gst.count("urisourcebin") + gst.count("rtspsrc")
    struct = "" if src_req == src_got else f" [STRUCT {src_got}/{src_req} src]"
    run_str = gst + " ! " + get_sink_str() if "fdsink" not in gst and "sink" not in gst.split()[-1] \
        else build_mjpeg_pipeline(gst)
    if restart:
        restart_service()
    t0 = time.time()
    mjpeg.start(run_str)
    ready, error = mjpeg.wait_until_ready(timeout=timeout, require_frame=True)
    lat = round(time.time() - t0, 1)
    mjpeg.stop()
    status = "PASS" if ready else "FAIL"
    detail = (f"{lat}s" if ready else (error or "no frame")[:300]) + struct
    return (status, detail, lat)


def main():
    _ensure_display()
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="every model x structure (~120)")
    ap.add_argument("--quick", action="store_true", help="representative subset (~20)")
    ap.add_argument("--no-restart", action="store_true", help="skip per-combo dxrt restart")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()
    full = args.full or not args.quick

    combos = build_matrix(full)
    restart = not args.no_restart
    print(f"== exhaustive streaming verification: {len(combos)} combos, "
          f"restart={'on' if restart else 'OFF'}, timeout={args.timeout}s ==", flush=True)

    results = []
    for i, (label, defn) in enumerate(combos, 1):
        print(f"[{i}/{len(combos)}] {label} ...", flush=True)
        status, detail, lat = run_combo(label, defn, args.timeout, restart)
        results.append((label, status, detail))
        print(f"    {status} — {detail}", flush=True)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    md = HERE / f"report-{stamp}.md"
    csv = HERE / f"report-{stamp}.csv"
    npass = sum(1 for _, s, _ in results if s == "PASS")
    lines = [f"# dx_stream streaming verification — {stamp}", "",
             f"{npass}/{len(results)} PASS  (restart={'on' if restart else 'off'})", "",
             "| # | combo | result | detail |", "|---|---|---|---|"]
    for i, (label, status, detail) in enumerate(results, 1):
        lines.append(f"| {i} | `{label}` | {status} | {detail} |")
    md.write_text("\n".join(lines))
    csv.write_text("combo,result,detail\n" +
                   "\n".join(f'"{l}",{s},"{d}"' for l, s, d in results))
    print(f"\n{npass}/{len(results)} PASS", flush=True)
    print(f"report: {md}", flush=True)


if __name__ == "__main__":
    main()

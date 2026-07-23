"""DX-APP Performance parsing and video conversion."""

import re, subprocess
from pathlib import Path
from dx_app.core.config import OUTPUTS_DIR


def _parse_perf(stdout):
    p={"pipeline":[]};in_s=False;in_img=False
    for line in stdout.splitlines():
        s=line.strip()
        if "PERFORMANCE SUMMARY" in s:in_s=True;continue
        if "IMAGE PROCESSING SUMMARY" in s:in_img=True;continue
        # ── IMAGE PROCESSING SUMMARY (Python sync image: latency-only, single frame) ──
        if in_img:
            if s.startswith("=====") and p["pipeline"]:
                in_img=False;continue
            m_img=re.match(r'^\s*(Read|Preprocess|Inference|Postprocess|Display)\s+([\d.]+)\s+ms',s)
            if m_img:
                lat=float(m_img.group(2))
                fps_equiv=round(1000.0/lat,1) if lat>0 else 0.0
                p["pipeline"].append({"step":m_img.group(1),"latency_ms":lat,"throughput_fps":fps_equiv,"is_async":False})
                if m_img.group(1)=="Inference":p.update({"inference_latency":m_img.group(2),"inference_fps":str(fps_equiv)})
            elif "Total Time" in s:
                m_tt=re.search(r'([\d.]+)\s*ms',s)
                if m_tt:
                    total_ms=float(m_tt.group(1))
                    p["total_time"]=str(round(total_ms/1000.0,3))
                    overall=round(1000.0/total_ms,1) if total_ms>0 else 0.0
                    p["overall_fps"]=str(overall)
                    p["total_frames"]="1"
                    p["single_frame_mode"]=True
            continue
        # ── PERFORMANCE SUMMARY (C++ / Python video) ──
        if not in_s:continue
        if s.startswith("=====") and p["pipeline"]:break
        m=re.match(r'^\s*(Read|Preprocess|Inference|Postprocess|Display)\s+([\d.]+)\s+ms\s+([\d.]+)\s+FPS(\*)?',s)
        if m:
            p["pipeline"].append({"step":m.group(1),"latency_ms":float(m.group(2)),"throughput_fps":float(m.group(3)),"is_async":bool(m.group(4))})
            if m.group(1)=="Inference":p.update({"inference_latency":m.group(2),"inference_fps":m.group(3)})
        elif "Total Frames" in s:p["total_frames"]=s.split(":")[-1].strip()
        elif "Total Time" in s:p["total_time"]=s.split(":")[-1].strip().rstrip(" s")
        elif "Overall FPS" in s:p["overall_fps"]=s.split(":")[-1].strip().split()[0]
        elif "Infer Completed" in s:p["infer_completed"]=s.split(":")[-1].strip()
        elif "Infer Inflight Avg" in s or "Inflight Avg" in s:p["inflight_avg"]=s.split(":")[-1].strip()
        elif "Infer Inflight Max" in s or "Inflight Max" in s:p["inflight_max"]=s.split(":")[-1].strip()
        # Type A: "Inference Throughput : 568.5 FPS"
        elif re.search(r"Inference Throughput\s*:",s):
            val=re.search(r"([\d.]+)\s*FPS",s)
            if val:p["inference_fps"]=val.group(1)
    if p["pipeline"]:
        # Type B: async-only (all latency_ms == 0) → mark flag, keep Inference FPS row only
        all_zero=all(r["latency_ms"]==0 for r in p["pipeline"])
        if all_zero:
            p["pipeline_async_only"]=True
            # Extract inference FPS from async row (FPS*)
            for r in p["pipeline"]:
                if r["step"]=="Inference" and r["throughput_fps"]>0:
                    p["inference_fps"]=str(r["throughput_fps"])
            p["pipeline"]=[]  # don't render 0-latency rows in table
        else:
            # Type C: real latency rows → bottleneck calc
            mx=max(p["pipeline"],key=lambda x:x["latency_ms"])
            p.update({"bottleneck":mx["step"],"total_pipeline_ms":sum(x["latency_ms"] for x in p["pipeline"])})
    return p

def _cvt_video(src,dst):
    try:
        r=subprocess.run(["ffmpeg","-y","-i",str(src),"-c:v","libx264","-preset","fast",
         "-movflags","+faststart","-pix_fmt","yuv420p",str(dst)],capture_output=True,timeout=120)
        return r.returncode==0
    except:
        try:
            import shutil
            shutil.copy2(src,dst);return True
        except:return False

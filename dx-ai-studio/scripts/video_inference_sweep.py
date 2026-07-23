#!/usr/bin/env python3
"""Sweep video inference across all dx_app model × lang × variant combos (real dx-runtime)."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from dx_app.core.models import get_models  # noqa: E402
from dx_app.core.config import CAT_VIDEO, DX_APP_ROOT, BUILD_DIR, PY_DIR  # noqa: E402
from dx_app.core.inference import run_inference  # noqa: E402

IMAGE_ONLY = frozenset({"embedding", "reid", "attribute_recognition"})
CRASH_EXITS = frozenset({-6, -11, -8, 134, 139})


def _variants_for(m: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    pairs = [
        ("cpp", "sync", m.get("cpp_sync")),
        ("cpp", "async", m.get("cpp_async")),
        ("python", "sync", m.get("py_sync")),
        ("python", "async", m.get("py_async")),
    ]
    for lang, var, ok in pairs:
        if ok:
            out.append((lang, var))
    cat, name = m["category"], m["name"]
    for var in ("sync_cpp_postprocess", "async_cpp_postprocess"):
        if (PY_DIR / cat / name / f"{name}_{var}.py").exists():
            out.append(("python", var))
    return out


def enumerate_jobs(models: list[dict]) -> list[dict]:
    jobs = []
    for m in models:
        if not m.get("model_file") or not m.get("model_exists"):
            continue
        cat = m["category"]
        if cat in IMAGE_ONLY:
            continue
        vid = CAT_VIDEO.get(cat)
        if not vid or not (DX_APP_ROOT / vid).exists():
            continue
        for lang, variant in _variants_for(m):
            jobs.append({
                "model": m["name"],
                "category": cat,
                "lang": lang,
                "variant": variant,
                "video_path": vid,
                "model_file": m["model_file"],
            })
    return jobs


def _parse_fps(stdout: str) -> str:
    m = re.search(r"Overall FPS\s*:\s*([\d.]+)", stdout or "")
    return m.group(1) if m else ""


def _direct_cpp_fps(model: str, variant: str, model_file: str, video_path: str, timeout: int) -> tuple[str, int]:
    """Baseline: invoke stock C++ binary directly (no --save), same as run_demo perf path."""
    bp = BUILD_DIR / f"{model}_{variant}"
    if not bp.exists() or variant not in ("sync", "async"):
        return "", -1
    mp = DX_APP_ROOT / model_file if not model_file.startswith("-") else None
    if not mp or not mp.exists():
        return "", -1
    cmd = [
        str(bp), "-m", str(mp), "-v", str(DX_APP_ROOT / video_path),
        "--no-display", "-l", "1",
    ]
    try:
        proc = subprocess.run(
            cmd, cwd=str(DX_APP_ROOT), capture_output=True, text=True, timeout=timeout,
        )
        return _parse_fps(proc.stdout + proc.stderr), proc.returncode
    except subprocess.TimeoutExpired:
        return "", -2
    except Exception:
        return "", -3


def _job_key(job: dict) -> tuple[str, str, str]:
    return (job["model"], job["lang"], job["variant"])


def _load_resume_keys(csv_path: Path, retry_failed: bool) -> set[tuple[str, str, str]]:
    if not csv_path.exists():
        return set()
    done: set[tuple[str, str, str]] = set()
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row.get("model", ""), row.get("lang", ""), row.get("variant", ""))
            if not key[0]:
                continue
            if retry_failed:
                if str(row.get("ok")).lower() == "true":
                    done.add(key)
            else:
                done.add(key)
    return done


def run_job(job: dict, timeout: int, compare_direct: bool, retries: int = 0) -> dict:
    attempts = max(1, retries + 1)
    last_row: dict | None = None
    for attempt in range(attempts):
        last_row = _run_job_once(job, timeout, compare_direct)
        if last_row["ok"] or not last_row["crash"]:
            return last_row
        if attempt + 1 < attempts:
            time.sleep(2.0)
    return last_row or _run_job_once(job, timeout, compare_direct)


def _run_job_once(job: dict, timeout: int, compare_direct: bool) -> dict:
    t0 = time.time()
    row = {**job, "ok": False, "crash": False, "exit_code": None, "fps": "",
           "fps_direct": "", "fps_delta_pct": "", "exit_direct": "", "elapsed_s": 0, "lang_effective": "",
           "video_save_mode": "", "result_video": False, "error": ""}
    try:
        res = run_inference(
            job["model"], job["category"], job["model_file"],
            lang=job["lang"], variant=job["variant"],
            input_type="video", video_path=job["video_path"],
            timeout=timeout, save_output=False,
        )
    except Exception as exc:
        row["error"] = str(exc)[:500]
        row["elapsed_s"] = round(time.time() - t0, 2)
        return row

    row["exit_code"] = res.get("exit_code")
    row["fps"] = res.get("fps") or _parse_fps(res.get("output", ""))
    row["lang_effective"] = res.get("lang_effective", "")
    row["video_save_mode"] = res.get("video_save_mode", "")
    row["result_video"] = bool(res.get("result_video_url"))
    row["error"] = (res.get("error") or "")[:500]
    row["elapsed_s"] = round(time.time() - t0, 2)
    ec = row["exit_code"]
    row["crash"] = ec in CRASH_EXITS or (isinstance(ec, int) and ec < 0 and ec not in (-1,))
    row["ok"] = ec == 0 and not row["error"]

    if compare_direct and job["lang"] == "cpp" and job["variant"] in ("sync", "async"):
        fps_d, ec_d = _direct_cpp_fps(
            job["model"], job["variant"], job["model_file"], job["video_path"], timeout,
        )
        row["fps_direct"] = fps_d
        row["exit_direct"] = ec_d
        try:
            if row["fps"] and fps_d:
                row["fps_delta_pct"] = round(
                    (float(row["fps"]) - float(fps_d)) / float(fps_d) * 100, 1
                )
        except (TypeError, ValueError, ZeroDivisionError):
            row["fps_delta_pct"] = ""

    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--filter", type=str, default="")
    ap.add_argument("--compare-direct", action="store_true",
                    help="Also run stock C++ binary (no save) for cpp sync/async FPS baseline")
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--resume", type=Path, default=None,
                    help="Existing results.csv — skip completed jobs")
    ap.add_argument("--retry-failed", action="store_true",
                    help="With --resume, only skip rows where ok=true")
    ap.add_argument("--job-delay", type=float, default=1.5,
                    help="Seconds to wait between jobs (NPU/dxrt recovery)")
    ap.add_argument("--retries", type=int, default=1,
                    help="Retry count for crash exits (-6 etc.)")
    args = ap.parse_args()

    jobs = enumerate_jobs(get_models())
    if args.filter:
        f = args.filter.lower()
        jobs = [j for j in jobs if f in j["model"].lower() or f in j["category"].lower()]
    if args.limit:
        jobs = jobs[: args.limit]

    resume_csv = args.resume
    if resume_csv and not args.out_dir:
        args.out_dir = resume_csv.parent
    out_dir = args.out_dir or (ROOT / "logs" / f"video_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "results.csv"
    if resume_csv and resume_csv.resolve() != csv_path.resolve():
        raise SystemExit("--resume must point to out-dir/results.csv")

    skip_keys = _load_resume_keys(csv_path, args.retry_failed) if resume_csv else set()
    if skip_keys:
        jobs = [j for j in jobs if _job_key(j) not in skip_keys]

    fields = [
        "model", "category", "lang", "variant", "video_path", "ok", "crash",
        "exit_code", "fps", "fps_direct", "fps_delta_pct", "exit_direct", "lang_effective",
        "video_save_mode", "result_video", "elapsed_s", "error",
    ]

    print(f"[sweep] jobs={len(jobs)} timeout={args.timeout}s out={out_dir} delay={args.job_delay}s")
    if skip_keys:
        print(f"[sweep] resumed skip={len(skip_keys)} retry_failed={args.retry_failed}")
    done = 0
    crashes = 0
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    mode = "w" if not resume_csv else "a"
    with csv_path.open(mode, newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if write_header:
            w.writeheader()
            fh.flush()
        for job in jobs:
            done += 1
            label = f"{job['model']}/{job['lang']}/{job['variant']}"
            print(f"[{done}/{len(jobs)}] {label} ...", flush=True)
            row = run_job(job, args.timeout, args.compare_direct, retries=args.retries)
            if row["crash"]:
                crashes += 1
            w.writerow({k: row.get(k, "") for k in fields})
            fh.flush()
            if args.job_delay > 0:
                time.sleep(args.job_delay)

    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    summary = {
        "total": len(rows),
        "pending_this_run": len(jobs),
        "crashes": crashes,
        "finished_at": datetime.now().isoformat(),
        "csv": str(csv_path),
    }
    summary["ok"] = sum(1 for r in rows if str(r.get("ok")).lower() == "true")
    summary["failed"] = len(rows) - summary["ok"]
    summary["crashes"] = sum(1 for r in rows if str(r.get("crash")).lower() == "true")
    fps_rows = []
    for r in rows:
        try:
            if r.get("lang") == "cpp" and r.get("fps") and r.get("fps_direct"):
                fps_rows.append(abs(float(r["fps_delta_pct"] or 0)))
        except (TypeError, ValueError):
            pass
    if fps_rows:
        summary["cpp_fps_delta_pct_max"] = max(fps_rows)
        summary["cpp_fps_delta_pct_avg"] = round(sum(fps_rows) / len(fps_rows), 2)
        summary["cpp_fps_compared"] = len(fps_rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 1 if crashes else 0


if __name__ == "__main__":
    raise SystemExit(main())

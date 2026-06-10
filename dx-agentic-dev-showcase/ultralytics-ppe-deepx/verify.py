#!/usr/bin/env python3
"""Verify the 4-way benchmark deliverables are real and self-consistent.

Checks:
  1. both *_deepx_model/ dirs exist and each contains a real .dxnn (INT8 NPU binary)
  2. bench_results.json has all 4 required rows, each with numeric map50_95 + fps
  3. domain retraining actually improved accuracy (retrained fp32 mAP > base fp32 mAP)
  4. INT8 quantization keeps the retrained NPU mAP sane (> 0, within a reasonable gap of fp32)
  5. report.md exists and contains the 4-way comparison table

Exit 0 + 'RESULT: PASS' only when all checks pass; exit 1 + 'RESULT: FAIL' otherwise.
"""
import json
import sys
from pathlib import Path

SESSION_DIR = Path(__file__).resolve().parent
REQUIRED_TAGS = ["base_fp32_gpu", "base_int8_npu", "retrained_fp32_gpu", "retrained_int8_npu"]
DEEPX_DIRS = ["yolo26n_deepx_model", "yolo26n_ppe_deepx_model"]


def main() -> int:
    failures = []

    # 1. DeepX model dirs + .dxnn
    for d in DEEPX_DIRS:
        p = SESSION_DIR / d
        dxnn = list(p.glob("*.dxnn")) if p.is_dir() else []
        if not dxnn:
            failures.append(f"missing .dxnn in {d}/")
        else:
            print(f"[OK] {d}/{dxnn[0].name} ({dxnn[0].stat().st_size} bytes)")

    # 2. benchmark rows
    res = SESSION_DIR / "bench_results.json"
    rows = {}
    if not res.exists():
        failures.append("bench_results.json missing")
    else:
        rows = {r["tag"]: r for r in json.loads(res.read_text())}
        for tag in REQUIRED_TAGS:
            r = rows.get(tag)
            if not r:
                failures.append(f"benchmark row missing: {tag}")
            elif not isinstance(r.get("map50_95"), (int, float)) or not isinstance(r.get("fps"), (int, float)):
                failures.append(f"benchmark row {tag} has non-numeric map/fps (status={r.get('status')})")
            else:
                print(f"[OK] {tag}: mAP50-95={r['map50_95']:.4f} fps={r['fps']:.2f}")

    def m(tag):
        v = rows.get(tag, {}).get("map50_95")
        return v if isinstance(v, (int, float)) else None

    # 3. retraining improved accuracy
    b, r = m("base_fp32_gpu"), m("retrained_fp32_gpu")
    if b is not None and r is not None:
        if r > b:
            print(f"[OK] domain retrain improved fp32 mAP50-95: {b:.4f} -> {r:.4f}")
        else:
            failures.append(f"retrain did not improve mAP ({b:.4f} -> {r:.4f})")

    # 4. INT8 sanity
    rf, ri = m("retrained_fp32_gpu"), m("retrained_int8_npu")
    if rf is not None and ri is not None:
        if ri > 0 and ri >= 0.5 * rf:
            print(f"[OK] retrained INT8 NPU mAP sane vs fp32: {ri:.4f} vs {rf:.4f}")
        else:
            failures.append(f"INT8 NPU mAP unexpectedly low: {ri:.4f} vs fp32 {rf:.4f}")

    # 5. report.md
    rep = SESSION_DIR / "report.md"
    if rep.is_file() and "mAP50-95" in rep.read_text():
        print("[OK] report.md present with comparison table")
    else:
        failures.append("report.md missing or incomplete")

    if failures:
        for f in failures:
            print(f"[FAIL] {f}")
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

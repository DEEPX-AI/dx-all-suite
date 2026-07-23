"""Accuracy self-check (F22) — compare reference (ONNX) vs compiled (DXNN) outputs.

The numeric comparison is pure-numpy and fully testable. Actually *running* ONNX
(onnxruntime) and DXNN (dx_engine on NPU) to get the two output sets is environment-coupled
(needs the runtime/hardware) and lives in verify.py / live runs — this module just judges the
two arrays so a self-heal can gate on "did quantization stay accurate enough?".
"""
from __future__ import annotations

from typing import Any


def compare_outputs(ref: Any, got: Any, *, rtol: float = 1e-2, atol: float = 1e-2,
                    cosine_min: float = 0.99) -> dict:
    """Compare two output tensors. Returns a structured verdict.

    keys: ok, reason, max_abs_diff, mean_abs_diff, cosine, within_tol, shape_match.
    """
    import numpy as np
    a = np.asarray(ref, dtype=np.float64).ravel()
    b = np.asarray(got, dtype=np.float64).ravel()

    res = {"ok": False, "reason": "", "max_abs_diff": None, "mean_abs_diff": None,
           "cosine": None, "within_tol": False, "shape_match": a.shape == b.shape}
    if a.shape != b.shape:
        res["reason"] = f"shape mismatch: {a.shape} vs {b.shape}"
        return res
    if a.size == 0:
        res["reason"] = "empty output"
        return res

    diff = np.abs(a - b)
    res["max_abs_diff"] = float(diff.max())
    res["mean_abs_diff"] = float(diff.mean())
    res["within_tol"] = bool(np.allclose(a, b, rtol=rtol, atol=atol))

    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    res["cosine"] = float(np.dot(a, b) / (na * nb)) if na > 0 and nb > 0 else (1.0 if na == nb else 0.0)

    res["ok"] = res["within_tol"] or res["cosine"] >= cosine_min
    res["reason"] = "ok" if res["ok"] else (
        f"diverged: max_abs={res['max_abs_diff']:.4g}, cosine={res['cosine']:.4f}"
    )
    return res


def summarize(verdicts: list[dict]) -> dict:
    """Aggregate per-output verdicts into a pass/fail summary for a model."""
    if not verdicts:
        return {"ok": False, "reason": "no outputs compared", "n": 0, "n_ok": 0}
    n_ok = sum(1 for v in verdicts if v.get("ok"))
    worst = min((v.get("cosine") for v in verdicts if v.get("cosine") is not None), default=None)
    ok = n_ok == len(verdicts)
    return {"ok": ok, "n": len(verdicts), "n_ok": n_ok, "worst_cosine": worst,
            "reason": "all outputs within tolerance" if ok else f"{len(verdicts) - n_ok} output(s) diverged"}

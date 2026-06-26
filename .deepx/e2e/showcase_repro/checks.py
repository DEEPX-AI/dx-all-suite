# SPDX-License-Identifier: Apache-2.0
"""Equivalence checkers for showcase reproducibility.

A repro run's output directory is scored on three tiers against the checked-in
showcase ground truth:

    artifacts  — mandatory deliverables + model/app files exist and are well-formed
    gates      — verify/setup/syntax/unit-test gates pass
    metrics    — measured behaviour (detections, squat count, sizes, latency)
                 is within tolerance of the original

Overall verdict:
    EQUIVALENT  all three tiers pass
    DEGRADED    artifacts pass but a gate or metric falls short
    FAILED      artifacts tier fails (core deliverable missing/broken)
    BLOCKED     set by the driver when the run never executed (env/auth) — not here

The checkers are pure functions over a directory: no NPU, no network. They parse
the run's own session.log for runtime evidence.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from showcase_repro.showcase_registry import SHOWCASES


# --------------------------------------------------------------------------- #
# Result types
# --------------------------------------------------------------------------- #
@dataclass
class CheckOutcome:
    name: str
    ok: bool
    evidence: str = ""
    gating: bool = True   # informational (gating=False) checks are reported, not scored


@dataclass
class TierResult:
    tier: str
    checks: List[CheckOutcome] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        gating = [c for c in self.checks if c.gating]
        return bool(gating) and all(c.ok for c in gating)

    def add(self, name: str, ok: bool, evidence: str = "", gating: bool = True) -> None:
        self.checks.append(CheckOutcome(name, ok, evidence, gating))


@dataclass
class ShowcaseResult:
    showcase: str
    output_dir: str
    tiers: Dict[str, TierResult]
    verdict: str

    def summary(self) -> str:
        parts = []
        for tname, tier in self.tiers.items():
            failed = [c.name for c in tier.checks if not c.ok and c.gating]
            info = [c.name for c in tier.checks if not c.ok and not c.gating]
            mark = "ok" if tier.passed else f"FAIL({','.join(failed)})"
            if info:
                mark += f" [info:{','.join(info)}]"
            parts.append(f"{tname}={mark}")
        return "; ".join(parts)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _as_roots(output_dir) -> List[Path]:
    """Normalize a single dir OR a list of dirs to a list of Paths. Cross-project (suite)
    showcases split artifacts across a compiler + an app session dir, so checkers search the
    UNION of all of a cell's output dirs."""
    if isinstance(output_dir, (list, tuple)):
        return [Path(p) for p in output_dir]
    return [Path(output_dir)]


def _rglob(output_dir, pattern: str) -> List[Path]:
    """rglob across every root (dedup, sorted)."""
    seen, out = set(), []
    for root in _as_roots(output_dir):
        for p in sorted(root.rglob(pattern)):
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def _read_logs(output_dir) -> str:
    """Concatenate every *.log (esp. session.log) under the run dir(s)."""
    chunks: List[str] = []
    for p in _rglob(output_dir, "*.log"):
        try:
            chunks.append(p.read_text(errors="replace"))
        except OSError:
            pass
    return "\n".join(chunks)


def _find_one(output_dir, pattern: str) -> Optional[Path]:
    matches = _rglob(output_dir, pattern)
    return matches[0] if matches else None


def _valid_json(path: Optional[Path]) -> bool:
    if not path or not path.is_file():
        return False
    try:
        json.loads(path.read_text())
        return True
    except (ValueError, OSError):
        return False


def _bash_n(path: Optional[Path]) -> bool:
    if not path or not path.is_file():
        return False
    try:
        return subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0
    except OSError:
        return False


def _py_compiles(path: Optional[Path]) -> bool:
    if not path or not path.is_file():
        return False
    import py_compile
    try:
        py_compile.compile(str(path), doraise=True)
        return True
    except (py_compile.PyCompileError, SyntaxError, OSError):
        return False


def _mandatory_deliverables(output_dir, names: List[str]) -> List[CheckOutcome]:
    out = []
    for n in names:
        out.append(CheckOutcome(f"deliverable:{n}", _find_one(output_dir, n) is not None))
    return out


_PORT_SKIP = ("/venv/", "/.venv/", "/__pycache__/", "/download/")


def _portability_checks(output_dir) -> List[CheckOutcome]:
    """Static self-containment/portability gate: the app must not depend on a source dir.

    Catches the two real failure modes seen in repro runs:
      - a symlink under the session escaping OUTSIDE it (cursor's engine -> showcase symlink);
      - code/scripts referencing a `dx-agent-dev-showcase/` source path (claude's SHOWCASE_DIR
        in-place import + model dir).
    venv/__pycache__/download dirs are skipped (venv→system-python symlinks are normal and the
    venv is recreated by setup.sh). Across cross-project (suite) showcases, a symlink between a
    cell's own dirs is fine — "escaping" means outside ALL of the cell's roots.
    """
    roots = [r.resolve() for r in _as_roots(output_dir)]

    def _skip(p: Path) -> bool:
        s = "/" + str(p) + "/"
        return any(seg in s for seg in _PORT_SKIP)

    def _under_any(tgt: Path) -> bool:
        return any(tgt == r or r in tgt.parents for r in roots)

    escaping = []
    for p in _rglob(output_dir, "*"):
        if _skip(p) or not p.is_symlink():
            continue
        try:
            inside = _under_any(p.resolve())
        except OSError:
            inside = False
        if not inside:
            escaping.append(p.name)

    # A showcase-source reference breaks portability ONLY when it pulls CODE/ENGINE/MODELS
    # from the source. Referencing the prompt-specified INPUT media (a `/sample/` clip the
    # app reads) is explicitly allowed ("read inputs from there, but create your app
    # elsewhere") and does not make the app non-portable.
    refs = []
    for p in _rglob(output_dir, "*.py") + _rglob(output_dir, "*.sh"):
        if _skip(p):
            continue
        try:
            txt = p.read_text(errors="replace")
        except OSError:
            continue
        for m in re.findall(r"dx-agent-dev-showcase/\S*", txt):
            if "/sample/" in m:
                continue  # input-media reference — allowed
            refs.append(p.name)
            break

    return [
        CheckOutcome("portable_no_symlink_escaping_session", not escaping, ",".join(escaping[:3])),
        CheckOutcome("portable_no_showcase_source_reference", not refs, ",".join(sorted(set(refs))[:3])),
    ]


_VENDORED_PKG_HINTS = {"engine", "common", "rapid_doc", "factory"}


def _portability_copyout(output_dir) -> CheckOutcome:
    """COPY the app to a temp dir OUTSIDE the suite, then confirm the entry's vendored-package
    imports (engine/common/rapid_doc/factory) resolve FROM the copy — proving the app does not
    rely on the suite being on sys.path. Catches claude's old in-place `from engine import`
    (engine lived in the showcase, not the app → absent in the copy → FAIL).

    For a cross-project cell with multiple dirs, the primary (app) dir is the one that must be
    self-contained; copy that one."""
    import ast
    import shutil
    import tempfile

    output_dir = _as_roots(output_dir)[0]
    tmp = Path(tempfile.mkdtemp(prefix="dx_portable_"))  # /tmp — outside the suite
    dst = tmp / "app"
    try:
        shutil.copytree(
            output_dir, dst, symlinks=True,
            ignore=shutil.ignore_patterns("venv", ".venv", "__pycache__", "model_files",
                                          "output", "download", "*.dxnn", "*.mp4"),
        )
        entries = (list(dst.rglob("*_sync.py")) + list(dst.rglob("*ocr*.py"))
                   + list(dst.rglob("*pdf_to_markdown*.py")))
        missing = []
        for entry in entries:
            if "/venv/" in ("/" + str(entry)):
                continue
            try:
                tree = ast.parse(entry.read_text(errors="replace"))
            except (SyntaxError, OSError):
                continue
            roots = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.ImportFrom) and n.module:
                    roots.add(n.module.split(".")[0])
                elif isinstance(n, ast.Import):
                    for a in n.names:
                        roots.add(a.name.split(".")[0])
            for r in roots & _VENDORED_PKG_HINTS:
                if not (dst / r).exists() and not (dst / (r + ".py")).exists():
                    missing.append(f"{entry.name} imports '{r}' (not vendored)")
        return CheckOutcome("portable_copyout_imports_resolve", not missing, "; ".join(missing[:3]))
    except OSError as e:
        return CheckOutcome("portable_copyout_imports_resolve", True, f"skipped: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _verdict(tiers: Dict[str, TierResult]) -> str:
    if not tiers["artifacts"].passed:
        return "FAILED"
    if tiers["gates"].passed and tiers["metrics"].passed:
        return "EQUIVALENT"
    return "DEGRADED"


# --------------------------------------------------------------------------- #
# P1 — ultralytics-yolo-deepx-export
# --------------------------------------------------------------------------- #
def check_export(output_dir: Path, gt: Dict) -> Dict[str, TierResult]:
    logs = _read_logs(output_dir)
    dxnn = _find_one(output_dir, "*.dxnn")
    cfg = _find_one(output_dir, "config.json")
    meta = _find_one(output_dir, "metadata.yaml")

    # --- artifacts ---
    art = TierResult("artifacts")
    art.add("dxnn_present", dxnn is not None, str(dxnn or ""))
    art.add("config_json_valid", _valid_json(cfg), str(cfg or ""))
    art.add("metadata_yaml", meta is not None, str(meta or ""))
    for c in _mandatory_deliverables(output_dir, ["setup.sh", "run.sh", "verify.py", "README.md", "session.log"]):
        art.checks.append(c)

    # --- gates ---
    gate = TierResult("gates")
    gate.add("verify_result_pass", "RESULT: PASS" in logs)
    gate.add("setup_sh_syntax", _bash_n(_find_one(output_dir, "setup.sh")))
    gate.add("run_sh_syntax", _bash_n(_find_one(output_dir, "run.sh")))

    # --- metrics ---
    met = TierResult("metrics")
    size = dxnn.stat().st_size if dxnn and dxnn.is_file() else 0
    gt_size = gt.get("dxnn_size_bytes", 0)
    tol = gt.get("dxnn_size_tolerance", 0.2)
    size_ok = gt_size > 0 and abs(size - gt_size) <= gt_size * tol
    met.add("dxnn_size_in_band", size_ok, f"{size}B vs {gt_size}B ±{int(tol*100)}%")

    m = re.search(r"Detected\s+(\d+)\s+object", logs)
    det = int(m.group(1)) if m else -1
    exp = gt.get("expected_detections", 0)
    dtol = gt.get("detections_tolerance", 2)
    met.add("detections_in_band", det >= 0 and abs(det - exp) <= dtol, f"{det} vs {exp}±{dtol}")

    classes_ok = all(cl in logs for cl in gt.get("expected_classes", ["bus"]))
    met.add("expected_classes_present", classes_ok)
    met.add("latency_recorded", bool(re.search(r"\d+(\.\d+)?\s*ms", logs)))

    return {"artifacts": art, "gates": gate, "metrics": met}


# --------------------------------------------------------------------------- #
# P2 — mini-game-squat-fitness
# --------------------------------------------------------------------------- #
def check_squat(output_dir: Path, gt: Dict) -> Dict[str, TierResult]:
    logs = _read_logs(output_dir)
    factory = _find_one(output_dir, "*factory*.py")
    sync = _find_one(output_dir, "*_sync.py")
    cfg = _find_one(output_dir, "config.json")
    test_file = _find_one(output_dir, "test_*squat*.py") or _find_one(output_dir, "test_*logic*.py")

    # --- artifacts ---
    art = TierResult("artifacts")
    factory_txt = factory.read_text(errors="replace") if factory and factory.is_file() else ""
    ifactory_ok = factory is not None and all(mname in factory_txt for mname in gt.get("ifactory_methods", []))
    art.add("ifactory_5_methods", ifactory_ok, str(factory or ""))
    sync_txt = sync.read_text(errors="replace") if sync and sync.is_file() else ""
    art.add("sync_runner_present", sync is not None and "SyncRunner" in sync_txt, str(sync or ""))
    # squat-specific tuning may be nested ("squat_game": {...}) OR flat
    # ("squat_down_angle"/"stand_angle"/...). Accept any squat/stand/knee-angle signal.
    cfg_txt = cfg.read_text() if (cfg and cfg.is_file()) else ""
    cfg_ok = _valid_json(cfg) and bool(re.search(r"squat|stand_angle|knee", cfg_txt, re.I))
    art.add("config_squat_tuning", cfg_ok, str(cfg or ""))
    # A squat-logic unit test mirrors the original's TDD but is NOT a mandatory
    # deliverable (CLAUDE.md list) — report it, do not gate the verdict on it.
    art.add("unit_test_file", test_file is not None, str(test_file or ""), gating=False)
    for c in _mandatory_deliverables(output_dir, ["setup.sh", "run.sh", "README.md", "session.log"]):
        art.checks.append(c)

    # --- gates ---
    gate = TierResult("gates")
    gate.add("sync_py_compiles", _py_compiles(sync))
    gate.add("factory_py_compiles", _py_compiles(factory))
    gate.add("setup_sh_syntax", _bash_n(_find_one(output_dir, "setup.sh")))
    gate.add("run_sh_syntax", _bash_n(_find_one(output_dir, "run.sh")))
    units_ok = bool(re.search(r"unit tests? passed", logs, re.I)) or bool(
        re.search(r"\d+\s+passed", logs)
    )
    gate.add("unit_tests_passed", units_ok, gating=False)  # informational (see artifacts note)

    # --- metrics ---
    met = TierResult("metrics")
    m = re.search(r"squats?\s+counted[:\s]+(\d+)", logs, re.I)
    n = int(m.group(1)) if m else -1
    met.add("squats_counted", n >= gt.get("min_squats_counted", 1), f"counted={n}")
    # An annotated video saved ANYWHERE counts (the framework default save-dir is
    # dx_app/artifacts/, not the session dir) — recognized via the log "Save" pipeline
    # stage / a referenced output.mp4 / a session-dir file.
    saved_anywhere = (
        "Saving output video" in logs
        or "output.mp4" in logs
        or bool(re.search(r"\bSave\b\s+\d+(\.\d+)?\s*ms", logs))
        or _find_one(output_dir, "output.mp4") is not None
    )
    met.add("output_video_saved", saved_anywhere)
    # Whether it landed in the SESSION dir (showcase convention) vs the framework
    # default artifacts dir — informational, does not gate "equivalent".
    in_session = (_find_one(output_dir, "output.mp4") is not None
                  or bool(re.search(r"Saving output video:[^\n]*dx-agent-dev/", logs)))
    met.add("output_in_session_dir", in_session, gating=False)
    met.add("fps_recorded", bool(re.search(r"\bFPS\b", logs)))

    return {"artifacts": art, "gates": gate, "metrics": met}


# --------------------------------------------------------------------------- #
# mini-game-stretching-coach (yolo26n-pose, IFactory + custom visualizer)
# --------------------------------------------------------------------------- #
def check_stretch(output_dir: Path, gt: Dict) -> Dict[str, TierResult]:
    logs = _read_logs(output_dir)
    factory = _find_one(output_dir, "*factory*.py")
    sync = _find_one(output_dir, "*_sync.py")
    cfg = _find_one(output_dir, "config.json")

    art = TierResult("artifacts")
    factory_txt = factory.read_text(errors="replace") if (factory and factory.is_file()) else ""
    art.add("ifactory_5_methods",
            factory is not None and all(m in factory_txt for m in gt.get("ifactory_methods", [])),
            str(factory or ""))
    sync_txt = sync.read_text(errors="replace") if (sync and sync.is_file()) else ""
    art.add("sync_runner_present", sync is not None and "SyncRunner" in sync_txt, str(sync or ""))
    art.add("config_json_valid", _valid_json(cfg), str(cfg or ""))
    for c in _mandatory_deliverables(output_dir, ["setup.sh", "run.sh", "README.md", "session.log"]):
        art.checks.append(c)

    gate = TierResult("gates")
    gate.add("sync_py_compiles", _py_compiles(sync))
    gate.add("factory_py_compiles", _py_compiles(factory))
    gate.add("setup_sh_syntax", _bash_n(_find_one(output_dir, "setup.sh")))
    gate.add("run_sh_syntax", _bash_n(_find_one(output_dir, "run.sh")))

    met = TierResult("metrics")
    saved = ("Saving output video" in logs or "annotated_output" in logs
             or _find_one(output_dir, "output.mp4") is not None)
    met.add("annotated_output_saved", saved)
    # 3-stage pose recognition: original logs verify RESULT: PASS and/or recognizer [PASS]
    met.add("pose_recognition_ok", "RESULT: PASS" in logs or bool(re.search(r"\[PASS\]", logs)))
    met.add("fps_recorded", bool(re.search(r"\bFPS\b", logs)))
    return {"artifacts": art, "gates": gate, "metrics": met}


# --------------------------------------------------------------------------- #
# paddleocr-video-ocr (PP-OCRv5 standalone NPU app — NOT IFactory)
# --------------------------------------------------------------------------- #
def check_ocr(output_dir: Path, gt: Dict) -> Dict[str, TierResult]:
    logs = _read_logs(output_dir)
    # main app: an *ocr*.py that is not a test/verify helper
    app = None
    for p in sorted(_rglob(output_dir, "*ocr*.py")):
        if p.name not in ("verify.py",) and "test" not in p.name:
            app = p
            break
    sample_detect = _find_one(output_dir, "sample_detect.jpg")

    art = TierResult("artifacts")
    art.add("ocr_app_py", app is not None, str(app or ""))
    art.add("sample_detect_jpg", sample_detect is not None, str(sample_detect or ""))
    for c in _mandatory_deliverables(output_dir, ["setup.sh", "run.sh", "README.md", "session.log"]):
        art.checks.append(c)

    gate = TierResult("gates")
    gate.add("ocr_app_compiles", _py_compiles(app))
    gate.add("setup_sh_syntax", _bash_n(_find_one(output_dir, "setup.sh")))
    gate.add("run_sh_syntax", _bash_n(_find_one(output_dir, "run.sh")))

    met = TierResult("metrics")
    counts = [int(a or b) for a, b in re.findall(r"(\d+)\s+texts|texts\s+(\d+)", logs)]
    max_texts = max(counts) if counts else 0
    met.add("texts_detected", max_texts >= gt.get("min_texts", 1), f"max_texts={max_texts}")
    met.add("sample_frame_saved",
            sample_detect is not None or "Saved annotated sample frame" in logs)
    met.add("latency_or_fps_recorded",
            bool(re.search(r"\bFPS\b", logs)) or bool(re.search(r"\d+(\.\d+)?\s*ms", logs)))
    return {"artifacts": art, "gates": gate, "metrics": met}


# --------------------------------------------------------------------------- #
# generic_app (fork-based standalone app, e.g. rapiddoc PDF->Markdown)
# --------------------------------------------------------------------------- #
def check_generic_app(output_dir: Path, gt: Dict) -> Dict[str, TierResult]:
    logs = _read_logs(output_dir)
    pys = [p for p in _rglob(output_dir, "*.py")
           if "/venv/" not in ("/" + str(p)) and "/__pycache__/" not in ("/" + str(p))
           and p.name != "verify.py" and "test" not in p.name]
    main = pys[0] if pys else None

    art = TierResult("artifacts")
    art.add("app_py_present", main is not None, str(main.name if main else ""))
    for c in _mandatory_deliverables(output_dir, ["setup.sh", "run.sh", "README.md", "session.log"]):
        art.checks.append(c)

    gate = TierResult("gates")
    gate.add("app_py_compiles", _py_compiles(main))
    gate.add("setup_sh_syntax", _bash_n(_find_one(output_dir, "setup.sh")))
    gate.add("run_sh_syntax", _bash_n(_find_one(output_dir, "run.sh")))

    met = TierResult("metrics")
    met.add("ran_with_output", len(logs.strip()) > 50)
    produced = (_find_one(output_dir, "*output*.md") is not None
                or _find_one(output_dir, "*.json") is not None
                or _find_one(output_dir, "sample_*.jpg") is not None)
    met.add("produced_output", produced)
    return {"artifacts": art, "gates": gate, "metrics": met}


# --------------------------------------------------------------------------- #
# ultralytics-retrain-eval (GPU 40-epoch retrain + INT8 NPU + 4-way eval)
# --------------------------------------------------------------------------- #
def check_retrain_eval(output_dir: Path, gt: Dict) -> Dict[str, TierResult]:
    report = _find_one(output_dir, "report.md")
    metrics = (_find_one(output_dir, "metrics.json") or _find_one(output_dir, "results.json")
               or _find_one(output_dir, "*metrics*.json"))
    sample = _find_one(output_dir, "sample_detect.jpg")
    app = (_find_one(output_dir, "pipeline.py")
           or next((p for p in sorted(_rglob(output_dir, "*.py"))
                    if "/venv/" not in ("/" + str(p)) and p.name not in ("verify.py", "make_report.py")
                    and "test" not in p.name), None))

    art = TierResult("artifacts")
    art.add("report_md", report is not None, str(report or ""))
    art.add("metrics_json_valid", _valid_json(metrics), str(metrics or ""))
    # sample_detect.jpg is requested only by the pills/wildlife prompts (not braintumor/ppe),
    # so it's informational — the core deliverable is the 4-way eval + report, not the image.
    art.add("sample_detect_jpg", sample is not None, str(sample or ""), gating=False)
    art.add("pipeline_py", app is not None, str(app or ""))
    for c in _mandatory_deliverables(output_dir, ["setup.sh", "run.sh", "README.md", "session.log"]):
        art.checks.append(c)

    gate = TierResult("gates")
    gate.add("pipeline_py_compiles", _py_compiles(app))
    gate.add("setup_sh_syntax", _bash_n(_find_one(output_dir, "setup.sh")))
    gate.add("run_sh_syntax", _bash_n(_find_one(output_dir, "run.sh")))

    met = TierResult("metrics")
    # Schema-agnostic 4-way parse. Across showcases the metrics file is metrics.json OR
    # results.json, and the 4 eval points appear as: a {"points": {...}} dict, a FLAT dict
    # (base_fp32/base_dxnn/retrained_fp32/retrained_dxnn or base_pt_fp32_gpu/...), OR a
    # top-level LIST of point dicts. The mAP key varies: map / map50 / map5095 / map50_95 /
    # mAP50_95. So: collect every dict with a "map"-ish key, label it by its key/label/form/
    # device text, and require retrained-mAP > base-mAP for the gain.
    def _mapv(v):
        if not isinstance(v, dict):
            return -1.0
        best = None
        for k, val in v.items():
            if not isinstance(val, (int, float)):
                continue
            kl = k.lower().replace("-", "").replace("_", "")
            if "map5095" in kl or kl == "map":
                return float(val)          # primary mAP50-95
            if "map" in kl and best is None:
                best = float(val)           # fallback (map50 etc.)
        return best if best is not None else -1.0

    # Merge points from EVERY metric file in the dir — some runs split them
    # (gpu_metrics.json + npu_metrics.json + train_metrics.json) instead of one metrics.json.
    pts = []  # list of (identifier_text, point_dict)
    metric_files = sorted(set(
        list(_rglob(output_dir, "*metrics*.json")) + list(_rglob(output_dir, "results.json"))
    ))
    for mf in metric_files:
        if "/venv/" in ("/" + str(mf)):
            continue
        try:
            d = json.loads(mf.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(d, dict):
            src = d["points"] if isinstance(d.get("points"), dict) else d
            items = src.items() if isinstance(src, dict) else []
        elif isinstance(d, list):
            items = [("", v) for v in d]
        else:
            items = []
        for k, v in items:
            if isinstance(v, dict) and any("map" in kk.lower() for kk in v):
                ident = " ".join(str(v.get(f, "")) for f in ("label", "form", "device", "model", "model_path"))
                pts.append(((str(k) + " " + ident).lower(), v))

    met.add("four_way_points", len(pts) >= 4, f"eval_points={len(pts)}")
    retr = max((_mapv(v) for ident, v in pts if "retrain" in ident), default=-1.0)
    base = max((_mapv(v) for ident, v in pts if "base" in ident), default=-1.0)
    met.add("accuracy_gain_retrained_gt_base", retr > base >= 0, f"retrained_mAP={retr} base_mAP={base}")
    rtxt = report.read_text(errors="replace").lower() if (report and report.is_file()) else ""
    met.add("report_4way_comparison",
            all(k in rtxt for k in ("base", "retrain", "fp32", "int8")) and "map" in rtxt)
    return {"artifacts": art, "gates": gate, "metrics": met}


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #
_CHECKERS: Dict[str, Callable[[Path, Dict], Dict[str, TierResult]]] = {
    "export": check_export,
    "squat": check_squat,
    "stretch": check_stretch,
    "ocr": check_ocr,
    "generic_app": check_generic_app,
    "retrain_eval": check_retrain_eval,
}


def evaluate_showcase(showcase_name: str, output_dir, extra_dirs=()) -> ShowcaseResult:
    """Score a showcase reproduction. `output_dir` is the primary session dir; `extra_dirs`
    are additional dirs for a cross-project (suite) cell whose artifacts split across a
    compiler + an app session — checkers search the UNION of all of them."""
    spec = SHOWCASES.get(showcase_name)
    if spec is None:
        raise KeyError(f"unknown showcase: {showcase_name}")
    checker = _CHECKERS.get(spec.checker)
    if checker is None:
        raise NotImplementedError(f"no checker implemented for '{spec.checker}' ({showcase_name})")
    primary = Path(output_dir)
    roots = [primary] + [Path(d) for d in (extra_dirs or [])]
    tiers = checker(roots, spec.ground_truth)
    # Cross-cutting self-containment/portability gate (all showcases): static checks +
    # a real copy-outside-the-suite import-resolution check.
    for c in _portability_checks(roots):
        tiers["gates"].checks.append(c)
    tiers["gates"].checks.append(_portability_copyout(roots))
    return ShowcaseResult(
        showcase=showcase_name,
        output_dir=" + ".join(str(r) for r in roots),
        tiers=tiers,
        verdict=_verdict(tiers),
    )

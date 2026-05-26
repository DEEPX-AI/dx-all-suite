"""Execution Trace analysis — scenario-aware rubric (v2).

For each scenario, the rubric defines components that sum to 100. Each component
is a binary check on artifacts in the agent's output dir(s):

  - compiler:           dxnn artifact size, compile log, session log substance,
                        success markers, clean logs, verify.py
  - dx_app / dx_stream: code/structural checks (factory completeness, pipeline
                        elements) + execution evidence + clean logs
  - dx_stream_cascaded: dx_stream checks + two-stage (primary + secondary)
  - runtime:            independent dx_app + dx_stream sub-project evaluation
                        (multi-domain routing — both must produce real artifacts)
  - suite:              compile artifact + app-consumes-dxnn chain + execution

Each scenario's components sum to exactly 100 — the final score is directly
comparable across scenarios (fixes the v1 issue where non-compiler scenarios
had a 75-85 ceiling but were still normalized as /100).

Checks are READ-ONLY — no subprocess execution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union


SUCCESS_MARKERS = [
    r"\bSanity check PASSED\b",
    r"\bCompilation DONE\b",
    r"\bCompilation complete\b",
    r"\bSuccess(?:fully)?\b",
    r"\b(?:RESULT|VERDICT):\s*PASS\b",
    r"\bRESULT:\s*PASS\b",
    r"\bAll checks passed\b",
    r"\bgenerated successfully\b",
]

FAILURE_MARKERS = [
    r"Traceback \(most recent call last\)",
    r"\bError:",
    r"\bERROR:",
    r"\bFAIL(?:ED)?\b",
    r"\bRESULT:\s*FAIL\b",
    r"NotImplementedError",
    r"\bImportError\b",
    r"\bModuleNotFoundError\b",
    r"PEP 668",
    r"externally-managed-environment",
]

TIMEOUT_MARKERS = [
    r"\btimeout\b",
    r"\bTimeout\b",
    r"\bTIMEOUT\b",
    r"\bkilled\b",
    r"signal.*SIGKILL",
    r"signal.*SIGTERM",
    r"killed.*timeout",
    r"Process exceeded.*timeout",
]


RUBRIC_VERSIONS = ("v2", "v3")
DEFAULT_RUBRIC_VERSION = "v3"
# Legacy alias — preserved for callers that imported `RUBRIC_VERSION` directly.
RUBRIC_VERSION = DEFAULT_RUBRIC_VERSION

# v3 vs v2:
#   * Marker dictionary expanded so the execution evidence emitted by all 5
#     tools in practice (e.g. "Overall FPS", "RESULT: PASS", "End of stream")
#     is recognized — v2's narrow regex caused 4 of 5 tools to false-fail
#     `inference_run_evidence` even when they had run inference.
#   * `verify_py` (5 pts) removed from dx_app/dx_stream/dx_stream_cascaded
#     where every tool scored 0% (the skill doesn't request verify.py for
#     user-facing scenarios). The 5 points are reallocated to the dominant
#     execution-evidence component for that scenario.
#   * compiler/suite keep `verify_py` (the compiler skill actually requires it).

EXECUTION_RUBRIC_V2: Dict[str, Dict[str, int]] = {
    "compiler": {
        "session_log_substantial": 15,
        "compile_evidence":        20,
        "verify_py":                5,
        "success_markers":         15,
        "clean_logs":              15,
        "dxnn_artifact_size":      30,
    },
    "dx_app": {
        "session_log_substantial": 10,
        "inference_run_evidence":  25,
        "verify_py":                5,
        "factory_smoke_test":      20,
        "success_markers":         20,
        "clean_logs":              20,
    },
    "dx_stream": {
        "pipeline_log_substantial":15,
        "pipeline_dot_or_video":   25,
        "verify_py":                5,
        "gst_element_usage":       20,
        "success_markers":         15,
        "clean_logs":              20,
    },
    "dx_stream_cascaded": {
        "pipeline_log_substantial":15,
        "pipeline_dot_or_video":   20,
        "verify_py":                5,
        "two_stage_evidence":      25,
        "success_markers":         15,
        "clean_logs":              20,
    },
    "runtime": {
        "dx_app_evidence":         35,
        "dx_stream_evidence":      35,
        "verify_py":                5,
        "success_markers":         10,
        "clean_logs":              15,
    },
    "suite": {
        "compile_artifact":        25,
        "app_consumes_dxnn":       25,
        "session_log_substantial": 10,
        "verify_py":                5,
        "success_markers":         15,
        "clean_logs":              20,
    },
}


EXECUTION_RUBRIC_V3: Dict[str, Dict[str, int]] = {
    "compiler": dict(EXECUTION_RUBRIC_V2["compiler"]),  # unchanged
    "dx_app": {
        "session_log_substantial": 10,
        "inference_run_evidence":  30,  # +5 (absorbed from removed verify_py)
        "factory_smoke_test":      20,
        "success_markers":         20,
        "clean_logs":              20,
    },
    "dx_stream": {
        "pipeline_log_substantial":15,
        "pipeline_dot_or_video":   30,  # +5
        "gst_element_usage":       20,
        "success_markers":         15,
        "clean_logs":              20,
    },
    "dx_stream_cascaded": {
        "pipeline_log_substantial":15,
        "pipeline_dot_or_video":   25,  # +5
        "two_stage_evidence":      25,
        "success_markers":         15,
        "clean_logs":              20,
    },
    "runtime": dict(EXECUTION_RUBRIC_V2["runtime"]),    # unchanged
    "suite":   dict(EXECUTION_RUBRIC_V2["suite"]),      # unchanged
}


# Back-compat alias: existing callers importing EXECUTION_RUBRIC see the
# version dictated by DEFAULT_RUBRIC_VERSION.
EXECUTION_RUBRIC: Dict[str, Dict[str, int]] = (
    EXECUTION_RUBRIC_V3 if DEFAULT_RUBRIC_VERSION == "v3" else EXECUTION_RUBRIC_V2
)


# -- v3 marker dictionaries ----------------------------------------------
# Recognized in session.log when no physical output artifact (output/, .dot,
# .mp4) is present.  Each pattern is matched case-insensitively via re.search.

INFERENCE_MARKERS_V3 = [
    # v2 patterns (carried forward)
    r"\b(?:Inference|Detection|Prediction)\s+(?:complete|done|finished|results?)\b",
    r"\bbbox(?:es)?:?\s*\[",
    # v3 new: dx_app standard performance output (emitted by claude/codex/opencode)
    r"\bOverall\s+FPS\s*[:=]?\s*\d",
    r"\bPERFORMANCE\s+SUMMARY\b",
    r"\bTotal\s+Frames\s*[:=]?\s*\d",
    r"\bInference\s+\d+\.\d+\s*ms\b",
    r"\bRESULT\s*:\s*PASS\b",
    r"\bAll\s+(?:validations|variants)\s+PASSED\b",
    # v3.1: bare FPS metric (e.g. "40.6 FPS") emitted via agent Bash tool
    # captures into session.txt — claude-code dx_app rarely emits the
    # "Overall FPS" prefix, just the raw "<number> FPS" line from the python
    # script.  Without this, 4/5 R2/R4/R6/R7/R8 sessions were scored 0
    # despite real inference runs in their session.txt transcripts.
    r"\b\d+(?:\.\d+)?\s*FPS\b",
    # v3.1: "exit code 0" near inference command tokens (sync.py / detection /
    # Inference) — common pattern in agent-Bash-tool execution where the
    # transcript captures both the command and its zero exit.
    r"exit\s+code\s+0[^\n]{0,200}(?:Inference|sync\.py|detection)",
]

PIPELINE_RUN_MARKERS_V3 = [
    r"\bEnd[- ]of[- ][Ss]tream\b",
    r"\bgst_pipeline\s+state[- ]changed\b",
    r"\bPipeline\s+(?:started|running|stopped|EOS)\b",
    r"\bGST_DEBUG\b",
]


@dataclass
class ExecutionReport:
    has_session_log: bool = False
    session_log_size: int = 0
    has_compile_log: bool = False
    has_pid_file: bool = False
    has_error_log: bool = False
    error_log_nonempty: bool = False
    has_verify_script: bool = False
    success_markers: List[str] = field(default_factory=list)
    failure_markers: List[str] = field(default_factory=list)
    timeout_markers: List[str] = field(default_factory=list)
    primary_artifact_size_bytes: int = 0
    suspected_timeout: bool = False
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    rubric_version: str = RUBRIC_VERSION


def _scan_file_for_markers(path: Path, patterns: List[str], limit: int = 50_000) -> List[str]:
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8", errors="ignore") as f:
            text = f.read(limit)
    except Exception:
        return []
    hits = []
    for p in patterns:
        m = re.search(p, text)
        if m:
            hits.append(m.group(0)[:60])
    return hits


def _scan_dir_for_markers(out_dir: Path, log_globs: List[str], patterns: List[str]) -> List[str]:
    if not out_dir.is_dir():
        return []
    hits = []
    for glob in log_globs:
        for f in out_dir.rglob(glob):
            if f.is_file():
                hits.extend(_scan_file_for_markers(f, patterns))
    return list(dict.fromkeys(hits))[:5]


def _read_text_safely(path: Path, limit: int = 100_000) -> str:
    if not path.is_file():
        return ""
    try:
        with path.open(encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""


# --- Single-dir component checks ---

def _has_substantial_session_log(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, "no out_dir"
    sl = out_dir / "session.log"
    if not sl.is_file():
        return False, "session.log missing"
    try:
        size = sl.stat().st_size
    except Exception:
        return False, "session.log unreadable"
    return (size >= 1024, f"session.log {size}B")


def _has_compile_evidence(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    if any(out_dir.glob("compile.pid")):
        return True, "compile.pid"
    if any(out_dir.glob("*compile*.log")):
        return True, "compile log present"
    return False, "no compile.pid or compile log"


def _has_verify_py(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    return ((out_dir / "verify.py").is_file(), "verify.py")


def _has_success_markers(out_dir: Path) -> Tuple[bool, str]:
    log_globs = ["session.log", "compile_out.log", "compile_output.log",
                 "compiler.log", "verify_out.log", "*.log"]
    hits = _scan_dir_for_markers(out_dir, log_globs, SUCCESS_MARKERS)
    return (bool(hits), ", ".join(hits[:3]) if hits else "none")


def _has_clean_logs(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    log_globs = ["session.log", "compile_out.log", "compile_output.log",
                 "compiler.log", "verify_out.log", "*.log"]
    failure_hits = _scan_dir_for_markers(out_dir, log_globs, FAILURE_MARKERS)
    error_log = out_dir / "error.log"
    error_nonempty = False
    if error_log.is_file():
        try:
            error_nonempty = error_log.stat().st_size > 0
        except Exception:
            pass
    if failure_hits or error_nonempty:
        return False, f"failures={len(failure_hits)} err_log={error_nonempty}"
    return True, "clean"


def _has_dxnn_realistic_size(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    max_size = 0
    for dxnn in out_dir.glob("*.dxnn"):
        try:
            max_size = max(max_size, dxnn.stat().st_size)
        except Exception:
            pass
    mb = max_size / (1024 * 1024)
    return (mb >= 1.0, f".dxnn {mb:.1f}MB")


def _has_compile_artifact(out_dir: Path) -> Tuple[bool, str]:
    return _has_dxnn_realistic_size(out_dir)


IFACTORY_METHODS = (
    "create_preprocessor",
    "create_postprocessor",
    "create_visualizer",
    "get_model_name",
    "get_task_type",
)


def _has_factory_smoke_test(out_dir: Path) -> Tuple[bool, str]:
    """Static smoke test: factory file references all 5 IFactory methods."""
    if not out_dir.is_dir():
        return False, ""
    candidates = list(out_dir.glob("factory/*.py")) + list(out_dir.glob("*_factory.py"))
    if not candidates:
        return False, "no factory file"
    for f in candidates:
        text = _read_text_safely(f)
        if all(m in text for m in IFACTORY_METHODS):
            return True, f"{f.name} has all 5 IFactory methods"
    return False, f"factory ({candidates[0].name}) missing IFactory methods"


def _has_inference_run_evidence(out_dir: Path, rubric_version: str = "v2") -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    for od in (out_dir / "output", out_dir / "outputs", out_dir / "results"):
        if od.is_dir() and any(od.iterdir()):
            return True, f"{od.name}/ has artifacts"

    # Check session.log first (shell-script-written) AND session.txt
    # (claude-CLI transcript copied here by conftest line 2167). Both can carry
    # legitimate inference evidence:
    #  - session.log: setup.sh/run.sh inline `python yolo26n_sync.py --image ...`
    #    captures argparse/output here.
    #  - session.txt: claude/codex/cursor agents that invoke inference through
    #    their own Bash tool path land FPS / exit_code / "Inference complete"
    #    markers in the CLI transcript, NOT in session.log. Without checking
    #    session.txt, those legitimate runs are scored 0.
    # Other agent CLIs use different transcript filenames — include them too.
    sl_text = (
        _read_text_safely(out_dir / "session.log")
        + "\n"
        + _read_text_safely(out_dir / "session.txt")
        + "\n"
        + _read_text_safely(out_dir / "session.md")
    )
    if rubric_version == "v3":
        for pat in INFERENCE_MARKERS_V3:
            m = re.search(pat, sl_text, re.IGNORECASE)
            if m:
                return True, f"transcript: {m.group(0)[:60]}"
    else:
        if re.search(
            r"\b(?:Inference|Detection|Prediction)\s+(?:complete|done|finished|results?)\b",
            sl_text,
            re.IGNORECASE,
        ):
            return True, "transcript mentions inference"
        if re.search(r"\bbbox(?:es)?:?\s*\[", sl_text):
            return True, "transcript shows bbox output"
        # Additional FPS / exit_code patterns commonly emitted by agent CLI Bash tool
        if re.search(r"\b\d+(?:\.\d+)?\s*FPS\b", sl_text, re.IGNORECASE):
            return True, "transcript shows FPS metric"
        if re.search(r"\bexit\s+code\s+0\b.*\b(?:Inference|sync\.py|detection)\b", sl_text, re.IGNORECASE | re.DOTALL):
            return True, "transcript shows successful inference exit"
    return False, "no inference evidence"


def _has_pipeline_log_substantial(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    candidates = [out_dir / "session.log"]
    candidates.extend(out_dir.glob("pipeline*.log"))
    candidates.extend(out_dir.glob("gst*.log"))
    for f in candidates:
        if f.is_file():
            try:
                if f.stat().st_size >= 1024:
                    return True, f"{f.name} {f.stat().st_size}B"
            except Exception:
                pass
    return False, "no substantial pipeline log"


def _has_pipeline_dot_or_video(out_dir: Path, rubric_version: str = "v2") -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    dots = list(out_dir.rglob("*.dot"))
    if dots:
        return True, f"{dots[0].name}"
    for ext in ("*.mp4", "*.ts", "*.mkv", "*.avi"):
        vids = list(out_dir.rglob(ext))
        if vids:
            return True, f"{vids[0].name}"
    if rubric_version == "v3":
        sl_text = _read_text_safely(out_dir / "session.log")
        for pat in PIPELINE_RUN_MARKERS_V3:
            m = re.search(pat, sl_text, re.IGNORECASE)
            if m:
                return True, f"session.log: {m.group(0)[:60]}"
    return False, "no .dot or video output"


def _has_gst_element_usage(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    for src in list(out_dir.rglob("*.py")) + list(out_dir.rglob("*.sh")):
        if not src.is_file():
            continue
        t = _read_text_safely(src)
        if "dxinfer" in t or "dxpostprocess" in t or "dxpreprocess" in t:
            return True, f"{src.name} uses dx* element"
    return False, "no dxinfer/dxpostprocess element usage"


def _has_two_stage_evidence(out_dir: Path) -> Tuple[bool, str]:
    if not out_dir.is_dir():
        return False, ""
    primary_secondary = False
    dxnn_refs = set()
    for src in list(out_dir.rglob("*.py")) + list(out_dir.rglob("*.sh")):
        if not src.is_file():
            continue
        t = _read_text_safely(src)
        if ("primary-model" in t and "secondary-model" in t) or \
           ("primary_model" in t and "secondary_model" in t):
            primary_secondary = True
        for m in re.finditer(r"([a-zA-Z0-9_\-./]+\.dxnn)", t):
            dxnn_refs.add(m.group(1))
    if primary_secondary:
        return True, "primary+secondary model refs"
    if len(dxnn_refs) >= 2:
        return True, f"{len(dxnn_refs)} distinct .dxnn refs"
    return False, "only one (or zero) model referenced"


# --- Multi-dir component checks ---

def _find_subproject_dir(output_dirs: Iterable[Path], subproject: str) -> Optional[Path]:
    target = f"/{subproject}/"
    for od in output_dirs:
        if target in str(od) + "/":
            return od
    return None


def _has_dx_app_evidence(output_dirs: List[Path]) -> Tuple[bool, str]:
    app_dir = _find_subproject_dir(output_dirs, "dx_app")
    if app_dir is None:
        return False, "no dx_app/ output dir"
    factory_ok, _ = _has_factory_smoke_test(app_dir)
    if factory_ok or any(app_dir.rglob("*.py")):
        return True, f"dx_app/{app_dir.name}"
    return False, "dx_app dir empty"


def _has_dx_stream_evidence(output_dirs: List[Path]) -> Tuple[bool, str]:
    stream_dir = _find_subproject_dir(output_dirs, "dx_stream")
    if stream_dir is None:
        return False, "no dx_stream/ output dir"
    gst_ok, _ = _has_gst_element_usage(stream_dir)
    if gst_ok or any(stream_dir.rglob("*.py")):
        return True, f"dx_stream/{stream_dir.name}"
    return False, "dx_stream dir empty"


def _has_app_consumes_dxnn(output_dirs: List[Path]) -> Tuple[bool, str]:
    app_dir = _find_subproject_dir(output_dirs, "dx_app") or _find_subproject_dir(output_dirs, "dx-runtime")
    if app_dir is None:
        return False, "no app dir"
    for f in list(app_dir.rglob("*.py")) + list(app_dir.rglob("config.json")):
        if not f.is_file():
            continue
        if ".dxnn" in _read_text_safely(f):
            return True, f"{f.name} references .dxnn"
    return False, "app code does not reference .dxnn"


_SINGLE_DIR_CHECKS = {
    "session_log_substantial": _has_substantial_session_log,
    "compile_evidence":        _has_compile_evidence,
    "verify_py":               _has_verify_py,
    "success_markers":         _has_success_markers,
    "clean_logs":              _has_clean_logs,
    "dxnn_artifact_size":      _has_dxnn_realistic_size,
    "compile_artifact":        _has_compile_artifact,
    "factory_smoke_test":      _has_factory_smoke_test,
    "inference_run_evidence":  _has_inference_run_evidence,
    "pipeline_log_substantial":_has_pipeline_log_substantial,
    "pipeline_dot_or_video":   _has_pipeline_dot_or_video,
    "gst_element_usage":       _has_gst_element_usage,
    "two_stage_evidence":      _has_two_stage_evidence,
}

_MULTI_DIR_CHECKS = {
    "dx_app_evidence":     _has_dx_app_evidence,
    "dx_stream_evidence":  _has_dx_stream_evidence,
    "app_consumes_dxnn":   _has_app_consumes_dxnn,
}


def _pick_primary_dir(output_dirs: List[Path], scenario: str) -> Optional[Path]:
    if not output_dirs:
        return None
    hints = {
        "compiler": "dx-compiler",
        "dx_app": "dx_app",
        "dx_stream": "dx_stream",
        "dx_stream_cascaded": "dx_stream",
        "suite": "dx-compiler",
    }
    hint = hints.get(scenario)
    if hint:
        for od in output_dirs:
            if f"/{hint}/" in str(od) + "/":
                return od
    return output_dirs[0]


def evaluate_execution(
    output_dirs: Union[Path, Iterable[Path]],
    scenario: str,
    rubric_version: str = DEFAULT_RUBRIC_VERSION,
) -> ExecutionReport:
    """Score execution evidence using a scenario-aware rubric.

    Accepts either a single Path (backward-compat) or an iterable of Paths.
    Each scenario's rubric sums to 100 — scores are directly comparable.

    ``rubric_version`` selects the marker dictionary and weight allocation:
      * ``"v2"`` — legacy behavior, preserved for data lineage / reproducibility.
      * ``"v3"`` (default) — expanded markers + verify_py reallocation; see
        the ``EXECUTION_RUBRIC_V3`` docstring above.
    """
    if rubric_version not in RUBRIC_VERSIONS:
        raise ValueError(f"unknown rubric_version: {rubric_version!r}")

    if isinstance(output_dirs, Path):
        dirs: List[Path] = [output_dirs]
    else:
        dirs = [p for p in output_dirs if isinstance(p, Path)]

    rep = ExecutionReport()
    rep.rubric_version = rubric_version
    if not dirs:
        return rep

    rubric_map = EXECUTION_RUBRIC_V3 if rubric_version == "v3" else EXECUTION_RUBRIC_V2
    rubric = rubric_map.get(scenario, rubric_map["dx_app"])
    primary = _pick_primary_dir(dirs, scenario)

    # Legacy informational fields (preserved for reports / SessionEval)
    if primary is not None and primary.is_dir():
        sl = primary / "session.log"
        if sl.is_file():
            rep.has_session_log = True
            try:
                rep.session_log_size = sl.stat().st_size
            except Exception:
                pass
        error_log = primary / "error.log"
        if error_log.is_file():
            rep.has_error_log = True
            try:
                rep.error_log_nonempty = error_log.stat().st_size > 0
            except Exception:
                pass
        if any(primary.glob("compile.pid")):
            rep.has_pid_file = True
        if any(primary.glob("*compile*.log")):
            rep.has_compile_log = True
        if (primary / "verify.py").is_file():
            rep.has_verify_script = True
        if scenario in ("compiler", "suite"):
            for od in dirs:
                if not od.is_dir():
                    continue
                for dxnn in od.glob("*.dxnn"):
                    try:
                        rep.primary_artifact_size_bytes = max(
                            rep.primary_artifact_size_bytes, dxnn.stat().st_size
                        )
                    except Exception:
                        pass
        log_globs = ["session.log", "compile_out.log", "compile_output.log",
                     "compiler.log", "verify_out.log", "*.log"]
        rep.success_markers = _scan_dir_for_markers(primary, log_globs, SUCCESS_MARKERS)
        rep.failure_markers = _scan_dir_for_markers(primary, log_globs, FAILURE_MARKERS)
        rep.timeout_markers = _scan_dir_for_markers(primary, log_globs, TIMEOUT_MARKERS)
        if rep.timeout_markers:
            rep.suspected_timeout = True

    # Rubric-driven scoring
    version_aware_checks = {"inference_run_evidence", "pipeline_dot_or_video"}
    breakdown: Dict[str, float] = {}
    score = 0.0
    for component, weight in rubric.items():
        passed = False
        if component in _MULTI_DIR_CHECKS:
            passed, _ev = _MULTI_DIR_CHECKS[component](dirs)
        elif component in _SINGLE_DIR_CHECKS:
            check = _SINGLE_DIR_CHECKS[component]
            if component in ("dxnn_artifact_size", "compile_artifact"):
                for od in dirs:
                    if od.is_dir():
                        p, _ev = check(od)
                        if p:
                            passed = True
                            break
            elif primary is not None:
                if component in version_aware_checks:
                    passed, _ev = check(primary, rubric_version)
                else:
                    passed, _ev = check(primary)
        else:
            continue
        breakdown[component] = float(weight) if passed else 0.0
        if passed:
            score += weight

    rep.score = max(0.0, min(100.0, score))
    rep.score_breakdown = breakdown
    return rep

"""Verification gate — the checklist of recurring mistakes, as code.

Each check returns a (name, ok, detail) row. ``verify_showcase`` aggregates them;
the CLI exits non-zero unless every check passes. This is what the skill runs
before declaring a showcase DONE.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from . import constants as C
from . import augment, manifest, recorder, transcript


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Report:
    checks: List[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(Check(name, ok, detail))

    @property
    def passed(self) -> bool:
        return all(c.ok for c in self.checks)

    def render(self) -> str:
        lines = []
        for c in self.checks:
            mark = "PASS" if c.ok else "FAIL"
            lines.append(f"[{mark}] {c.name}" + (f" — {c.detail}" if c.detail else ""))
        lines.append("")
        lines.append("RESULT: PASS" if self.passed else "RESULT: FAIL")
        return "\n".join(lines)


def _py_ok(path: Path) -> bool:
    cp = subprocess.run(["python3", "-m", "py_compile", str(path)],
                        capture_output=True, text=True)
    return cp.returncode == 0


def _bash_ok(path: Path) -> bool:
    cp = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    return cp.returncode == 0


# Fork-based showcases (RapidDoc / PaddleOCR) MUST ship a GENERATED standalone app, not a
# run.sh that shells out to the fork's own demo/example. Match an invocation of a fork demo
# script (e.g. `python demo/demo_offline.py`, `.../demo/foo.py`, `examples/bar.py`).
_FORK_DEMO_RE = re.compile(
    r"(?:python\d?|python3)\s+\S*(?:demo|examples?)/\S*\.py", re.MULTILINE)


def runsh_wraps_fork_demo(run_sh: Path) -> Optional[bool]:
    """True if run.sh invokes a fork demo/example script instead of a generated app entry.
    None if run.sh is absent (check skipped)."""
    if not run_sh.exists():
        return None
    try:
        return bool(_FORK_DEMO_RE.search(run_sh.read_text(errors="replace")))
    except Exception:
        return None


# A dx_app-asset model path resolved through an EMPTY-default var expansion
# (e.g. `${DX_APP_ROOT:-}/assets/models/x.dxnn`) collapses to an absolute `/assets/...`
# when the var is unset — the squat model-discovery regression. The correct pattern
# derives the path from `$SUITE_ROOT/dx-runtime/dx_app` (always resolvable).
_BROKEN_MODEL_RE = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*:-\}[^\n]*assets/models", re.MULTILINE)


def runsh_model_discovery_broken(run_sh: Path) -> Optional[bool]:
    """True if run.sh resolves a dx_app model via an empty-default var expansion
    (collapses to an unresolvable absolute path). None if run.sh is absent."""
    if not run_sh.exists():
        return None
    try:
        return bool(_BROKEN_MODEL_RE.search(run_sh.read_text(errors="replace")))
    except Exception:
        return None


def setupsh_local_venv_without_bridge(setup_sh: Path) -> Optional[bool]:
    """True if setup.sh creates a local venv (`python3 -m venv`) but never writes a
    dx_engine bridge `*.pth` — so dx_engine is unimportable in the new venv (the
    stretching FATAL). None if setup.sh is absent. False if no local venv is created
    (reuses venv-dx-runtime) or a bridge .pth is written."""
    if not setup_sh.exists():
        return None
    try:
        text = setup_sh.read_text(errors="replace")
    except Exception:
        return None
    creates_local_venv = bool(re.search(r"python3?\s+-m\s+venv\b", text))
    writes_bridge = ".pth" in text
    return creates_local_venv and not writes_bridge


def verify_showcase(showcase_dir: str, *, stream_json: Optional[str] = None,
                    expected_tool: str = C.DEFAULT_TOOL,
                    expected_model: str = C.DEFAULT_MODEL,
                    gifs: Optional[List[str]] = None,
                    require_files: Optional[List[str]] = None,
                    augment_targets: Optional[List[str]] = None,
                    showcase_name: Optional[str] = None) -> Report:
    """Run the full showcase verification gate."""
    rep = Report()
    sc = Path(showcase_dir)
    name = showcase_name or sc.name

    # 1. transcript files exist
    tprefix = C.TRANSCRIPT_PREFIX
    tmd = sc / f"{tprefix}.md"
    rep.add("transcript files present",
            all((sc / f"{tprefix}.{e}").exists() for e in ("md", "html", "jsonl")),
            f"{tprefix}.{{md,html,jsonl}} in {sc}")

    # 2. transcript completeness + model/tool (from the stream-json capture)
    if stream_json and Path(stream_json).exists():
        m = transcript.metrics_from_stream(stream_json) or {}
        has_wall = bool(m.get("duration_ms"))
        has_cost = m.get("total_cost_usd") is not None
        rep.add("transcript complete (Wall-clock + Cost)", has_wall and has_cost,
                f"duration_ms={m.get('duration_ms')} cost={m.get('total_cost_usd')}")
        model = (m.get("model") or "")
        rep.add("model matches expected", expected_model in model or model == expected_model,
                f"got '{model}', expected '{expected_model}'")
        ts = m.get("toolsets") or []
        sk = m.get("skills") or []
        # Canonical KB = toolsets OR the dx-* skill sequence. KB-routed builds (compile /
        # fork-apps) read a .deepx/toolsets/*.md; pure dx_app builds (e.g. pose mini-games)
        # use the skill sequence (router → brainstorm → … → verify) with no separate toolset.
        # Fail only if NEITHER was used (⇒ improvised from memory/prior outputs).
        rep.add("KB used (toolsets or skill sequence)", bool(ts) or bool(sk),
                (", ".join(ts) if ts else "skills: " + " → ".join(sk)) if (ts or sk)
                else "NONE read — relied on prior outputs/memory?")
    else:
        # fall back to the rendered md (model line); cost/wall not assertable
        body = tmd.read_text(errors="replace") if tmd.exists() else ""
        rep.add("transcript complete (Wall-clock + Cost)",
                "Wall-clock" in body and "Cost" in body,
                "checked rendered md (no stream-json supplied)")
        rep.add("model matches expected", expected_model in body,
                f"expected '{expected_model}' in md")
    rep.add("tool is claude (auto-transcript supported)", expected_tool == "claude",
            f"tool={expected_tool}")

    # 3. GIFs: exist, < 10MB, non-black
    for g in (gifs or []):
        gp = Path(g)
        size = gp.stat().st_size if gp.exists() else 0
        ok = gp.exists() and 0 < size <= C.GIF_MAX_BYTES
        rep.add(f"gif ok: {gp.name}", ok, f"{size // 1024}KB (<10MB={size <= C.GIF_MAX_BYTES})")
        nb = recorder.gif_first_frame_nonblack(g, at_secs=0.0)
        if nb is not None:
            rep.add(f"gif non-black: {gp.name}", nb, "frame extrema check")
        st = recorder.gif_is_static(g)
        if st is not None:
            rep.add(f"gif not static: {gp.name}", not st,
                    "frames differ (build rendered live)" if not st
                    else "STATIC — recording didn't show the build live (skill Phase 3)")

    # 4. artifacts copied + scripts syntax
    for rf in (require_files or []):
        p = sc / rf
        rep.add(f"artifact present: {rf}", p.exists(), str(p))
        if p.exists() and p.suffix == ".py":
            rep.add(f"py syntax: {rf}", _py_ok(p))
        elif p.exists() and p.suffix == ".sh":
            rep.add(f"bash syntax: {rf}", _bash_ok(p))

    # 4b. fork-based apps: run.sh must run a GENERATED entry, not the fork's demo/example
    # (RapidDoc/PaddleOCR — wrapping demo_offline.py is not a standalone app; skill rule 9).
    wraps = runsh_wraps_fork_demo(sc / "run.sh")
    if wraps is not None:
        rep.add("run.sh runs a generated app (not a fork demo)", not wraps,
                "own entry" if not wraps
                else "run.sh shells out to a fork demo/example — generate a standalone entry")

    # 4c. relocatability regressions (squat / stretching / ppe classes)
    rs = sc / "run.sh"
    broken_model = runsh_model_discovery_broken(rs)
    if broken_model is not None:
        rep.add("run.sh model discovery (dx_app asset) resolvable", not broken_model,
                "derives from $SUITE_ROOT/dx-runtime/dx_app" if not broken_model
                else "uses empty-default ${VAR:-}/assets/models — collapses to an unresolvable path")
    ss = sc / "setup.sh"
    no_bridge = setupsh_local_venv_without_bridge(ss)
    if no_bridge is not None:
        rep.add("setup.sh local venv bridges dx_engine", not no_bridge,
                "reuses venv-dx-runtime or writes a bridge .pth" if not no_bridge
                else "creates a local venv with no dx_engine bridge .pth — import will FATAL")
    from . import artifacts
    flags = artifacts.scan_nonportable(str(sc), strict=True)
    rep.add("portable (no build-session/absolute paths)", not flags,
            "clean" if not flags
            else f"{len(flags)} nonportable ref(s), e.g. {flags[0]['file'].split('/')[-1]}:{flags[0]['line']}")

    # 5. README/docs augmented (idempotent marker present for this showcase)
    for tgt in (augment_targets or []):
        tp = Path(tgt)
        rep.add(f"augmented: {tp.name}", augment.has_marker(tgt, name),
                f"marker dx-showcase:{name}:gif")

    # 6. manifest coverage — the showcase MUST be listed in showcases.json so the
    # card grid / catalog / docs table include it (the yolo-export omission class of bug)
    root = sc.resolve().parent.parent  # dx-agent-dev-showcase/<name> -> repo root
    man_path = root / manifest.MANIFEST_REL
    if man_path.exists():
        try:
            listed = {s.name for s in manifest.load_manifest(str(root)).showcases}
            rep.add("listed in showcases.json", name in listed,
                    "present" if name in listed else f"'{name}' missing — add it + run regen-docs")
        except Exception as e:  # malformed manifest is itself a failure
            rep.add("listed in showcases.json", False, f"manifest error: {e}")
    return rep

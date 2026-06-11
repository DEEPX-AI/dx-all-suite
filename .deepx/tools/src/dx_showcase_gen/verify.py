"""Verification gate — the checklist of recurring mistakes, as code.

Each check returns a (name, ok, detail) row. ``verify_showcase`` aggregates them;
the CLI exits non-zero unless every check passes. This is what the skill runs
before declaring a showcase DONE.
"""
from __future__ import annotations

import json
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
        rep.add("KB toolsets read (canonical KB used)", bool(ts),
                ", ".join(ts) if ts else "NONE read — relied on prior outputs/memory?")
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

    # 4. artifacts copied + scripts syntax
    for rf in (require_files or []):
        p = sc / rf
        rep.add(f"artifact present: {rf}", p.exists(), str(p))
        if p.exists() and p.suffix == ".py":
            rep.add(f"py syntax: {rf}", _py_ok(p))
        elif p.exists() and p.suffix == ".sh":
            rep.add(f"bash syntax: {rf}", _bash_ok(p))

    # 5. README/docs augmented (idempotent marker present for this showcase)
    for tgt in (augment_targets or []):
        tp = Path(tgt)
        rep.add(f"augmented: {tp.name}", augment.has_marker(tgt, name),
                f"marker dx-showcase:{name}:gif")

    # 6. manifest coverage — the showcase MUST be listed in showcases.json so the
    # card grid / catalog / docs table include it (the yolo-export omission class of bug)
    root = sc.resolve().parent.parent  # dx-agentic-dev-showcase/<name> -> repo root
    man_path = root / manifest.MANIFEST_REL
    if man_path.exists():
        try:
            listed = {s.name for s in manifest.load_manifest(str(root)).showcases}
            rep.add("listed in showcases.json", name in listed,
                    "present" if name in listed else f"'{name}' missing — add it + run regen-docs")
        except Exception as e:  # malformed manifest is itself a failure
            rep.add("listed in showcases.json", False, f"manifest error: {e}")
    return rep

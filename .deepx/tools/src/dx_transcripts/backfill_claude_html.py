#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Backfill missing claude-code session HTML across past e2e runs.

For each scenario directory ``results/<run_id>/<result_dir>/claude_code__<scenario>/``,
checks whether ``<scenario>-claude-code-session.html`` is missing. If so:

1. Read ``<scenario>-claude-code-stream.jsonl`` to extract ``session_id``.
2. Look up that UUID in ``~/.claude/projects/*/<uuid>.jsonl`` via
   ``parse_claude_session.find_sessions(session_id=...)`` (no time filter,
   no encoding mismatch).
3. Render HTML with ``parse_session`` + ``render_html`` and write to disk.

Default mode is dry-run; pass ``--apply`` to actually write files. Pass
``--run-id <id>`` (repeatable) to scope to specific run-ids.
"""

from __future__ import annotations

# --- self-bootstrap: make the `dx_transcripts` package importable when this
# --- module is run as a standalone script (parents[1] == .deepx/tools/src).
import sys as _sys
from pathlib import Path as _Path
_SRC = str(_Path(__file__).resolve().parents[1])
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

_TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))

from dx_transcripts.parse_claude_session import find_sessions, parse_session, render_html  # noqa: E402


RESULTS_ROOT = Path(__file__).resolve().parents[2] / "dx-agent-dev" / "e2e-tests" / "results"


def _extract_session_uuid(jsonl_path: Path) -> Optional[str]:
    """Return the first ``session_id`` (or ``session.id``) seen in the stream."""
    try:
        text = jsonl_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    for line in text.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = d.get("session_id")
        if not sid:
            sess = d.get("session")
            if isinstance(sess, dict):
                sid = sess.get("id")
        if sid:
            return sid
    return None


def _iter_scenario_dirs(run_ids: List[str]):
    """Yield ``(run_id, result_dir, scenario_dir, scenario_name)`` tuples."""
    for run_id_dir in sorted(RESULTS_ROOT.iterdir()):
        if not run_id_dir.is_dir():
            continue
        if run_ids and run_id_dir.name not in run_ids:
            continue
        for result_dir in sorted(run_id_dir.iterdir()):
            if not result_dir.is_dir():
                continue
            if "claude-code-autopilot" not in result_dir.name:
                continue
            for scenario_dir in sorted(result_dir.iterdir()):
                if not scenario_dir.is_dir():
                    continue
                if not scenario_dir.name.startswith("claude_code__"):
                    continue
                scenario = scenario_dir.name[len("claude_code__"):]
                yield run_id_dir.name, result_dir.name, scenario_dir, scenario


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", action="append", default=[],
                    help="Limit to specific run-ids (repeatable). Default: all.")
    ap.add_argument("--apply", action="store_true",
                    help="Actually write HTML files. Without this flag, only summarize.")
    args = ap.parse_args()

    stats = {
        "scanned": 0,
        "already_has_html": 0,
        "no_jsonl": 0,
        "no_uuid": 0,
        "no_meta": 0,
        "render_error": 0,
        "would_write": 0,
        "wrote": 0,
        "session_dir_copied": 0,
        "session_dir_would_copy": 0,
    }
    actions: List[str] = []
    errors: List[str] = []

    for run_id, result_name, scenario_dir, scenario in _iter_scenario_dirs(args.run_id):
        stats["scanned"] += 1
        # cascaded scenarios reuse scenario_key="dx_stream" → file prefix is
        # ``dx_stream-claude-code-*``, not ``dx_stream_cascaded-…``.  Discover
        # the stream.jsonl by glob so we don't hardcode the scenario→prefix
        # mapping.
        jsonl_candidates = sorted(scenario_dir.glob("*-claude-code-stream.jsonl"))
        html_candidates = sorted(scenario_dir.glob("*-claude-code-session.html"))

        # Even when the wrapper already has an HTML, the per-session-dir copy
        # (created at conftest.py:~2185 during normal runs) can still be
        # missing — past sessions that hit the encode_project_path bug were
        # backfilled to the wrapper only.  Resolve symlinks here and propagate.
        if html_candidates and jsonl_candidates:
            prefix = jsonl_candidates[0].name[: -len("-stream.jsonl")]
            # symlink naming: ``{prefix}-session_<scenario>_<session_id>``
            # (e.g. ``dx_app-claude-code-session_dx_app_20260523-015147_...``)
            # — note the "-session_" infix, NOT just "_".
            symlink_prefix = f"{prefix}-session_"
            html_src = html_candidates[0]
            for entry in scenario_dir.iterdir():
                if entry.is_symlink() and entry.name.startswith(symlink_prefix):
                    try:
                        resolved = entry.resolve(strict=True)
                    except (OSError, RuntimeError):
                        break
                    if resolved.is_dir():
                        dst = resolved / "session.html"
                        if not dst.exists():
                            if args.apply:
                                try:
                                    dst.write_text(html_src.read_text(encoding="utf-8"), encoding="utf-8")
                                    stats["session_dir_copied"] += 1
                                    actions.append(f"COPIED → {dst}")
                                except OSError as e:
                                    errors.append(f"session.html copy error: {dst}: {e}")
                            else:
                                stats["session_dir_would_copy"] += 1
                                actions.append(f"WOULD copy → {dst}")
                    break
            stats["already_has_html"] += 1
            continue
        if not jsonl_candidates:
            stats["no_jsonl"] += 1
            errors.append(f"no jsonl: {run_id}/{result_name}/{scenario}")
            continue

        jsonl = jsonl_candidates[0]
        # derive html name from jsonl prefix (e.g. dx_stream-claude-code-…)
        prefix = jsonl.name[: -len("-stream.jsonl")]
        html = scenario_dir / f"{prefix}-session.html"

        uuid = _extract_session_uuid(jsonl)
        if not uuid:
            stats["no_uuid"] += 1
            errors.append(f"no uuid in jsonl: {run_id}/{result_name}/{scenario}")
            continue

        metas = find_sessions(session_id=uuid)
        if not metas:
            stats["no_meta"] += 1
            errors.append(f"no projects jsonl for uuid {uuid[:8]}: {run_id}/{result_name}/{scenario}")
            continue

        try:
            parsed = parse_session(metas[0])
            html_text = render_html(parsed)
        except Exception as e:  # noqa: BLE001
            stats["render_error"] += 1
            errors.append(f"render error {type(e).__name__}: {run_id}/{result_name}/{scenario}: {e}")
            continue

        # Also copy into the per-session output dir (the symlink target). The
        # conftest.py harness does this at session-creation time (line ~2185)
        # but a retro backfill writes only to the wrapper dir, leaving the
        # actual artifact dir without its session.html. Resolve the symlink in
        # ``scenario_dir`` (e.g. ``<scenario>-claude-code-session_<scenario>_<sid>``)
        # and copy session.html into that dir too.
        session_dir_html: Optional[Path] = None
        for entry in scenario_dir.iterdir():
            if entry.is_symlink() and entry.name.startswith(f"{prefix}_"):
                try:
                    resolved = entry.resolve(strict=True)
                except (OSError, RuntimeError):
                    continue
                if resolved.is_dir():
                    candidate = resolved / "session.html"
                    if not candidate.exists():
                        session_dir_html = candidate
                break

        if args.apply:
            try:
                html.write_text(html_text, encoding="utf-8")
                stats["wrote"] += 1
                actions.append(f"WROTE  {html} ({len(html_text):,}B)")
                if session_dir_html is not None:
                    try:
                        session_dir_html.write_text(html_text, encoding="utf-8")
                        actions.append(f"  + copied to {session_dir_html}")
                    except OSError as e:
                        errors.append(f"session.html copy error: {session_dir_html}: {e}")
            except OSError as e:
                stats["render_error"] += 1
                errors.append(f"write error: {html}: {e}")
        else:
            stats["would_write"] += 1
            extra = f" + session.html → {session_dir_html}" if session_dir_html else ""
            actions.append(f"WOULD  {run_id}/{result_name}/{scenario} ({len(html_text):,}B from uuid {uuid[:8]}){extra}")

    print("=== Summary ===")
    for k, v in stats.items():
        print(f"  {k:18s} {v}")
    if actions:
        print(f"\n=== Actions ({len(actions)}) ===")
        for a in actions:
            print(f"  {a}")
    if errors:
        print(f"\n=== Errors / skipped ({len(errors)}) ===")
        for e in errors:
            print(f"  {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

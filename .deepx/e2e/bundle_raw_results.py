#!/usr/bin/env python3
"""Bundle a runner results dir into a self-contained, relocatable archive.

results/<run_id>/<autopilot>/ contains manifest.json, session logs, and SYMLINKS into
scattered sub-project session dirs (dx-runtime/dx_app/dx-agent-dev/<session>/, ...). A plain
copy leaves dangling symlinks + manifest paths pointing at a (soon-deleted) worktree. This
bundler dereferences everything into one tree keyed by manifest `relative_path`, excludes
large artifacts, and rewrites manifest paths to be bundle-relative so the bundle opens
standalone after the worktree is gone.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
from pathlib import Path
from typing import Dict, List

DEFAULT_EXCLUDES = ("*.dxnn", "*.onnx", "venv", ".venv", "__pycache__", "*.engine")


def _copy_tree_deref(src: Path, dst: Path, excludes, excluded: List[str]) -> None:
    """Copy src->dst following symlinks, skipping excluded names; record what was dropped."""
    dst.mkdir(parents=True, exist_ok=True)
    for entry in sorted(src.iterdir()):
        if any(fnmatch.fnmatch(entry.name, p) for p in excludes):
            excluded.append(str(entry))
            continue
        real = entry.resolve()
        target = dst / entry.name
        if real.is_dir():
            _copy_tree_deref(real, target, excludes, excluded)
        elif real.is_file():
            shutil.copy2(real, target)
        # else: broken link / special -> skip silently


def bundle(results_run_dir: Path, out_dir: Path, suite_root: Path | None = None,
           excludes=DEFAULT_EXCLUDES) -> Dict:
    """Bundle every <autopilot> subdir of results_run_dir into out_dir. Returns a report dict."""
    results_run_dir = Path(results_run_dir).resolve()
    out_dir = Path(out_dir)
    excluded: List[str] = []
    bundled_autopilots: List[str] = []

    autodirs = [d for d in sorted(results_run_dir.iterdir())
                if d.is_dir() and (d / "manifest.json").exists()]
    if not autodirs and (results_run_dir / "manifest.json").exists():
        autodirs = [results_run_dir]

    for auto in autodirs:
        auto_out = out_dir / "results" / auto.name
        _copy_tree_deref(auto, auto_out, excludes, excluded)
        mf_path = auto / "manifest.json"
        mf = json.loads(mf_path.read_text())
        srels = suite_root.resolve() if suite_root else None
        for key, info in mf.get("artifacts", {}).items():
            rel = info.get("relative_path")
            real_src = Path(info["path"])
            if not real_src.is_absolute() and srels:
                real_src = srels / real_src
            real_src = real_src.resolve()
            if rel and real_src.exists():
                dest = out_dir / "suite" / rel
                _copy_tree_deref(real_src, dest, excludes, excluded)
                info["path"] = f"suite/{rel}"
            link_in_bundle = auto_out / key
            if link_in_bundle.is_symlink() or link_in_bundle.exists():
                if link_in_bundle.is_dir() and not link_in_bundle.is_symlink():
                    shutil.rmtree(link_in_bundle, ignore_errors=True)
                else:
                    link_in_bundle.unlink(missing_ok=True)
            if rel:
                rel_target = Path("..") / ".." / "suite" / rel
                try:
                    link_in_bundle.symlink_to(rel_target)
                except OSError:
                    pass
        (auto_out / "manifest.json").write_text(json.dumps(mf, indent=2, ensure_ascii=False) + "\n")
        bundled_autopilots.append(auto.name)

    report = {"bundled": bundled_autopilots, "excluded": excluded, "out": str(out_dir)}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "BUNDLE_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    if excluded:
        (out_dir / "EXCLUDED.txt").write_text(
            "Excluded (large/regenerable) — NOT in this bundle:\n" + "\n".join(excluded) + "\n")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Bundle runner raw results into a self-contained archive")
    ap.add_argument("--results-dir", required=True, help="results/<run_id>/ (or a single autopilot dir)")
    ap.add_argument("--out", required=True, help="output bundle dir (under $DX_MODEL_EVAL_ARCHIVE)")
    ap.add_argument("--suite-root", default=None, help="suite root for resolving relative_path")
    ap.add_argument("--exclude", action="append", default=None, help="extra glob to exclude (repeatable)")
    a = ap.parse_args()
    excludes = list(DEFAULT_EXCLUDES) + (a.exclude or [])
    rep = bundle(Path(a.results_dir), Path(a.out),
                 Path(a.suite_root) if a.suite_root else None, tuple(excludes))
    print(f"bundled {len(rep['bundled'])} autopilot dir(s); excluded {len(rep['excluded'])} entries -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Static code quality assessment of artifacts produced in a session output dir."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class QualityReport:
    """Per-output-dir code quality summary."""
    python_files: int = 0
    python_syntax_ok: int = 0
    python_syntax_errors: List[str] = field(default_factory=list)
    json_files: int = 0
    json_valid: int = 0
    json_errors: List[str] = field(default_factory=list)
    bash_files: int = 0
    bash_syntax_ok: int = 0
    bash_syntax_errors: List[str] = field(default_factory=list)
    placeholder_hits: List[str] = field(default_factory=list)
    direct_engine_use: List[str] = field(default_factory=list)
    relative_import_hits: List[str] = field(default_factory=list)

    @property
    def python_pct(self) -> float:
        return 100.0 * self.python_syntax_ok / self.python_files if self.python_files else 100.0

    @property
    def json_pct(self) -> float:
        return 100.0 * self.json_valid / self.json_files if self.json_files else 100.0

    @property
    def bash_pct(self) -> float:
        return 100.0 * self.bash_syntax_ok / self.bash_files if self.bash_files else 100.0

    @property
    def syntax_pct(self) -> float:
        denom = self.python_files + self.json_files + self.bash_files
        if denom == 0:
            return 100.0
        ok = self.python_syntax_ok + self.json_valid + self.bash_syntax_ok
        return 100.0 * ok / denom

    @property
    def quality_score(self) -> float:
        """0-100 composite: syntax weighted + penalties for placeholders/direct engine use."""
        score = self.syntax_pct
        # Penalty 5 per placeholder hit (cap at 30)
        score -= min(30, 5 * len(self.placeholder_hits))
        # Penalty 5 per direct engine use (cap at 15)
        score -= min(15, 5 * len(self.direct_engine_use))
        # Penalty 2 per relative import (cap at 10)
        score -= min(10, 2 * len(self.relative_import_hits))
        return max(0.0, score)


PLACEHOLDER_PATTERNS = [
    (re.compile(r"#\s*TODO\s*:\s*implement", re.IGNORECASE), "TODO: implement"),
    (re.compile(r"^\s*#\s*from\s+dxnn_sdk", re.MULTILINE), "commented dxnn_sdk import"),
    (re.compile(r"^\s*#\s*from\s+dx_engine", re.MULTILINE), "commented dx_engine import"),
    (re.compile(r"result\s*=\s*np\.zeros\("), "fake result = np.zeros()"),
    (re.compile(r"#\s*Similar to (sync|async) version"), "stub Similar-to comment"),
    (re.compile(r"pass\s*#\s*placeholder", re.IGNORECASE), "pass placeholder"),
]

# Direct InferenceEngine usage outside factory pattern (anti-pattern)
DIRECT_ENGINE_PATTERNS = [
    re.compile(r"InferenceEngine\(\)\.\w*\b"),
    re.compile(r"engine\.run\s*\("),
    re.compile(r"engine\.run_async\s*\("),
]

# Relative imports anti-pattern
RELATIVE_IMPORT_PATTERN = re.compile(
    r"^\s*from\s+\.+[a-zA-Z_]", re.MULTILINE
)


def _bash_n(path: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            ["bash", "-n", str(path)],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0, (r.stderr or "").strip()[:200]
    except Exception as e:
        return False, str(e)[:200]


def _py_compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except py_compile.PyCompileError as e:
        return False, str(e)[:200]
    except Exception as e:
        return False, str(e)[:200]


def _json_load(path: Path) -> tuple[bool, str]:
    try:
        with path.open(encoding="utf-8") as f:
            json.load(f)
        return True, ""
    except Exception as e:
        return False, str(e)[:200]


def evaluate_quality(output_dir: Path) -> QualityReport:
    """Walk output_dir; check syntax + anti-patterns of all .py / .json / .sh files."""
    rep = QualityReport()
    if not output_dir.is_dir():
        return rep
    # Skip cached/vendored directories (exact match or prefix match for venv*)
    skip_dirs_exact = {"__pycache__", ".venv", "node_modules", ".pytest_cache",
                       "site-packages", "dist-info", ".cache", ".tox"}
    skip_dir_prefixes = ("venv",)   # venv, venv_<sid>, venv-py3.12 etc.
    for path in output_dir.rglob("*"):
        if not path.is_file():
            continue
        # Skip files within skip_dirs
        skip = False
        for seg in path.parts:
            if seg in skip_dirs_exact:
                skip = True
                break
            if seg.startswith(skip_dir_prefixes):
                skip = True
                break
        if skip:
            continue
        suffix = path.suffix.lower()
        rel = path.relative_to(output_dir)
        if suffix == ".py":
            rep.python_files += 1
            ok, err = _py_compile(path)
            if ok:
                rep.python_syntax_ok += 1
            else:
                rep.python_syntax_errors.append(f"{rel}: {err}")
            # placeholder/anti-pattern scan
            try:
                body = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                body = ""
            for rx, label in PLACEHOLDER_PATTERNS:
                if rx.search(body):
                    rep.placeholder_hits.append(f"{rel}: {label}")
            # Don't flag factory.py files for direct engine use (factory IS the engine wrapper)
            if "_factory.py" not in path.name:
                for rx in DIRECT_ENGINE_PATTERNS:
                    if rx.search(body):
                        rep.direct_engine_use.append(f"{rel}: {rx.pattern}")
                        break
            if RELATIVE_IMPORT_PATTERN.search(body):
                rep.relative_import_hits.append(str(rel))
        elif suffix == ".json":
            rep.json_files += 1
            ok, err = _json_load(path)
            if ok:
                rep.json_valid += 1
            else:
                rep.json_errors.append(f"{rel}: {err}")
        elif suffix == ".sh":
            rep.bash_files += 1
            ok, err = _bash_n(path)
            if ok:
                rep.bash_syntax_ok += 1
            else:
                rep.bash_syntax_errors.append(f"{rel}: {err}")
    return rep

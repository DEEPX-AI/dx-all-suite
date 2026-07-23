"""Runtime i18n refresh gap inventory — JS files with dynamic DOM + i18n but no lang hook."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import is_excluded_path
from .schema import Finding

_MIN_DYNAMIC_WRITES = 3
_DYNAMIC_RE = re.compile(r"\.(?:textContent|innerHTML)\s*=")
_I18N_RE = re.compile(r"\bT\s*\(|(?:^|[^\w])_lt\s*\(|ns\._lt\s*\(")
_HOOK_PATTERNS = (
    "onLangChange",
    "_DX_I18N_CALLBACKS",
    "dx-lang-change",
    "refreshActivePageLanguage",
    "refreshStreamLanguage",
    "refreshLauncherChrome",
    "refreshCompilerLanguage",
    "refreshLanguage",
    "refreshValidationLanguage",
    "registerLangRefresher",
    "registerStreamLangRefresher",
    "registerCompilerLangRefresher",
    "registerBenchmarkLangRefresher",
    "registerModelZooLangRefresher",
    "registerPlannerLangRefresher",
    "registerSharedLangRefresher",
    "applyLang",
    "LangRefresh.",
)
_STALE_COMPARE_RE = re.compile(
    r"\.textContent\s*===\s*T\s*\("
    r"|\.textContent\s*!==\s*T\s*\("
)

# Files exempt: pure utilities / no user-visible i18n (review before adding).
_EXEMPT_FILES: frozenset[str] = frozenset()


@dataclass(frozen=True)
class RuntimeRefreshRecord:
    source_file: str
    dynamic_writes: int
    i18n_calls: int
    has_lang_hook: bool
    stale_lang_compare: bool
    module: str

    @property
    def record_id(self) -> str:
        return f"runtime:{self.source_file}"

    @property
    def needs_hook(self) -> bool:
        if self.source_file in _EXEMPT_FILES:
            return False
        return (
            self.dynamic_writes >= _MIN_DYNAMIC_WRITES
            and self.i18n_calls > 0
            and not self.has_lang_hook
        )


def _module_for(rel_path: str) -> str:
    first = rel_path.split("/", 1)[0]
    return first if first.startswith("dx_") or first in ("launcher", "shared") else "other"


def _scan_js_file(repo_root: Path, path: Path) -> RuntimeRefreshRecord | None:
    rel = path.relative_to(repo_root).as_posix()
    if is_excluded_path(rel):
        return None
    if "vendor" in rel or ".min." in rel:
        return None
    if path.suffix != ".js":
        return None
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    dynamic = len(_DYNAMIC_RE.findall(src))
    i18n = len(_I18N_RE.findall(src))
    has_hook = any(p in src for p in _HOOK_PATTERNS)
    stale = bool(_STALE_COMPARE_RE.search(src))
    if dynamic < 1 and i18n < 1:
        return None
    return RuntimeRefreshRecord(
        source_file=rel,
        dynamic_writes=dynamic,
        i18n_calls=i18n,
        has_lang_hook=has_hook,
        stale_lang_compare=stale,
        module=_module_for(rel),
    )


def extract_runtime_inventory(repo_root: Path) -> list[RuntimeRefreshRecord]:
    records: list[RuntimeRefreshRecord] = []
    for path in sorted(repo_root.rglob("*.js")):
        rec = _scan_js_file(repo_root, path)
        if rec is not None:
            records.append(rec)
    return records


def classify_runtime_gaps(records: list[RuntimeRefreshRecord]) -> list[Finding]:
    findings: list[Finding] = []
    for rec in records:
        if rec.needs_hook:
            findings.append(Finding(
                record_id=rec.record_id,
                issue_type="missing-lang-hook",
                severity="High" if rec.dynamic_writes >= 10 else "Medium",
                message=(
                    f"{rec.source_file}: {rec.dynamic_writes} dynamic DOM writes, "
                    f"{rec.i18n_calls} i18n calls, no lang-change hook"
                ),
                suggested_fix="Register refresh*Language via DXI18n.onLangChange or _DX_I18N_CALLBACKS.",
                verification_method="runtime inventory",
            ))
        if rec.stale_lang_compare:
            findings.append(Finding(
                record_id=rec.record_id,
                issue_type="stale-lang-compare",
                severity="Medium",
                message=f"{rec.source_file}: compares textContent to T(...) — breaks across locales",
                suggested_fix="Store data-i18n-key or compare against language-neutral state flag.",
                verification_method="runtime inventory",
            ))
    return findings


def check_runtime_gaps_gate(findings: list[Finding]) -> str | None:
    gap_types = {"missing-lang-hook", "stale-lang-compare"}
    bad = [f for f in findings if f.issue_type in gap_types]
    if bad:
        summary = "\n".join(f"  {f.record_id}: {f.message}" for f in bad[:25])
        extra = f"\n  ... and {len(bad) - 25} more" if len(bad) > 25 else ""
        return f"{len(bad)} runtime refresh gap(s):\n{summary}{extra}"
    return None

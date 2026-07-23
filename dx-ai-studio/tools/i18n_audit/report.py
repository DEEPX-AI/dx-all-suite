from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import BRAND_TERMS, LANGUAGES
from .schema import AuditRecord, Finding


def build_payload(
    records: list[AuditRecord],
    findings: list[Finding],
    coverage_states: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    severity_counts = Counter(f.severity for f in findings)
    record_map = {r.record_id: r.module for r in records}
    module_counts = Counter(record_map.get(f.record_id, "unknown") for f in findings)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "record_count": len(records),
            "finding_count": len(findings),
            "severity_counts": dict(severity_counts),
            "module_counts": dict(module_counts),
            "languages": list(LANGUAGES),
        },
        "records": [r.to_dict() for r in records],
        "findings": [f.to_dict() for f in findings],
        "coverage_states": coverage_states or [],
        "brand_terms": sorted(BRAND_TERMS),
    }


def _without_generated_at(payload: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in payload.items() if k != "generated_at"}


def _preserve_generated_at_when_content_matches(payload: dict[str, Any], path: Path) -> None:
    if not path.exists():
        return
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if (
        isinstance(existing, dict)
        and existing.get("generated_at")
        and _without_generated_at(existing) == _without_generated_at(payload)
    ):
        payload["generated_at"] = existing["generated_at"]


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _preserve_generated_at_when_content_matches(payload, path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    summary = payload["summary"]
    lines.append("# Six-Language Copy Audit Report\n")
    lines.append(f"Generated: {payload['generated_at']}\n")
    lines.append(f"- **Records:** {summary['record_count']}")
    lines.append(f"- **Findings:** {summary['finding_count']}")
    lines.append(f"- **Languages:** {', '.join(summary['languages'])}")
    lines.append("")

    lines.append("## Findings by Severity\n")
    sev_counts = summary.get("severity_counts", {})
    for sev in ("Critical", "High", "Medium", "Low"):
        count = sev_counts.get(sev, 0)
        lines.append(f"- **{sev}:** {count}")
    lines.append("")

    lines.append("## Findings by Module\n")
    module_findings: dict[str, int] = Counter()
    for f in payload["findings"]:
        mod = f["record_id"].split(":")[0]
        module_findings[mod] += 1
    for mod, count in sorted(module_findings.items()):
        lines.append(f"- **{mod}:** {count}")
    if not module_findings:
        lines.append("No findings.")
    lines.append("")

    lines.append("## Terminology Allowlist\n")
    for term in payload.get("brand_terms", []):
        lines.append(f"- {term}")
    lines.append("")

    lines.append("## Browser Coverage Matrix\n")
    coverage = payload.get("coverage_states", [])
    if coverage:
        lines.append("| Module | State | Locale | Issue Type |")
        lines.append("|--------|-------|--------|------------|")
        for cs in coverage:
            mod = cs.get("module", "")
            state = cs.get("state", "")
            locale = cs.get("locale", "")
            issue = cs.get("issue_type", "")
            lines.append(f"| {mod} | {state} | {locale} | {issue} |")
        lines.append("")
        for cs in coverage:
            mod = cs.get("module", "")
            state = cs.get("state", "")
            locale = cs.get("locale", "")
            lines.append(f"- Evidence key: {mod} / {state} / {locale}")
    else:
        lines.append("No browser evidence collected yet.")
    lines.append("")

    findings = payload["findings"]
    for sev in ("Critical", "High", "Medium", "Low"):
        lines.append(f"## {sev} Findings\n")
        sev_findings = [f for f in findings if f["severity"] == sev]
        if sev_findings:
            for f in sev_findings:
                lines.append(f"### `{f['record_id']}`\n")
                lines.append(f"- **Issue:** {f['issue_type']}")
                lines.append(f"- **Message:** {f['message']}")
                if f.get("suggested_fix"):
                    lines.append(f"- **Suggested fix:** {f['suggested_fix']}")
                lines.append(f"- **Verification:** {f['verification_method']}")
                lines.append("")
        else:
            lines.append("No findings at this severity level.\n")

    lines.append("## Next Implementation Scope\n")
    lines.append("1. Fill missing locale values for High-severity findings.")
    lines.append("2. Run browser evidence collection for runtime validation.")
    lines.append("3. Review Medium findings for intentional fallback vs. missing copy.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")

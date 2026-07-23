import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_writes_json_and_markdown_reports(tmp_path):
    project_root = Path(__file__).resolve().parents[2]
    repo = tmp_path / "repo"
    (repo / "launcher/static").mkdir(parents=True)
    (repo / "launcher/static/index.html").write_text(
        '<div><span class="en">Run</span><span class="ko">실행</span></div>',
        encoding="utf-8",
    )
    json_out = tmp_path / "audit.json"
    md_out = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.i18n_audit",
            "--repo",
            str(repo),
            "--output-json",
            str(json_out),
            "--output-md",
            str(md_out),
        ],
        cwd=str(repo.parent),
        env={**os.environ, "PYTHONPATH": str(project_root)},
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["summary"]["record_count"] >= 1
    markdown = md_out.read_text(encoding="utf-8")
    assert "# Six-Language Copy Audit Report" in markdown
    for heading in (
        "## Findings by Severity",
        "## Findings by Module",
        "## Terminology Allowlist",
        "## Browser Coverage Matrix",
        "## Critical Findings",
        "## High Findings",
        "## Medium Findings",
        "## Low Findings",
        "## Next Implementation Scope",
    ):
        assert heading in markdown


def test_cli_merges_browser_evidence(tmp_path):
    project_root = Path(__file__).resolve().parents[2]
    repo = tmp_path / "repo"
    (repo / "launcher/static").mkdir(parents=True)
    (repo / "launcher/static/index.html").write_text(
        '<div><span class="en">Run</span><span class="ko">실행</span></div>',
        encoding="utf-8",
    )
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "launcher-home-es.json").write_text(
        json.dumps({
            "module": "launcher",
            "state": "home",
            "route": "/",
            "locale": "es",
            "document_lang": "en",
            "body_has_lang_class": False,
            "issue_type": "runtime-not-switching",
        }),
        encoding="utf-8",
    )
    json_out = tmp_path / "audit.json"
    md_out = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.i18n_audit",
            "--repo",
            str(repo),
            "--browser-evidence-dir",
            str(evidence_dir),
            "--output-json",
            str(json_out),
            "--output-md",
            str(md_out),
        ],
        cwd=str(repo.parent),
        env={**os.environ, "PYTHONPATH": str(project_root)},
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["coverage_states"][0]["issue_type"] == "runtime-not-switching"
    markdown = md_out.read_text(encoding="utf-8")
    # Table row must separate module/state/locale into distinct columns
    assert "| launcher | home | es | runtime-not-switching |" in markdown
    # The combined form must NOT appear inside the table Module column
    assert "| launcher / home / es |" not in markdown
    # Legacy human-readable evidence key preserved outside the table
    assert "launcher / home / es" in markdown

    # --- Regression: table must be structurally contiguous (no list items
    # between header and rows).  A stray "- Evidence key:" line before a
    # table row terminates the Markdown table.
    lines = markdown.splitlines()
    header_index = lines.index("| Module | State | Locale | Issue Type |")
    assert lines[header_index + 1] == "|--------|-------|--------|------------|"
    assert lines[header_index + 2] == "| launcher | home | es | runtime-not-switching |"
    assert "- Evidence key: launcher / home / es" in markdown
    assert lines.index("- Evidence key: launcher / home / es") > header_index + 2


def test_cli_strict_fail_on_integrity_issues(tmp_path):
    """--fail-on-integrity-issues exits 2 when placeholder drift is detected."""
    project_root = Path(__file__).resolve().parents[2]
    repo = tmp_path / "repo"
    (repo / "dx_app/static/js").mkdir(parents=True)
    # en has {0} but es translation omits it → placeholder mismatch
    (repo / "dx_app/static/js/i18n.js").write_text(
        '"model_label": { "en": "Model {0}", "es": "Modelo" }',
        encoding="utf-8",
    )
    json_out = tmp_path / "audit.json"
    md_out = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable, "-m", "tools.i18n_audit",
            "--repo", str(repo),
            "--output-json", str(json_out),
            "--output-md", str(md_out),
            "--fail-on-integrity-issues",
        ],
        cwd=str(repo.parent),
        env={**os.environ, "PYTHONPATH": str(project_root)},
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "placeholder mismatch" in result.stderr


def test_cli_strict_fail_on_findings(tmp_path):
    """--fail-on-findings exits 2 when missing-language findings exist."""
    project_root = Path(__file__).resolve().parents[2]
    repo = tmp_path / "repo"
    (repo / "launcher/static").mkdir(parents=True)
    (repo / "launcher/static/index.html").write_text(
        '<div><span class="en">Run</span><span class="ko">실행</span></div>',
        encoding="utf-8",
    )
    json_out = tmp_path / "audit.json"
    md_out = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable, "-m", "tools.i18n_audit",
            "--repo", str(repo),
            "--output-json", str(json_out),
            "--output-md", str(md_out),
            "--fail-on-findings",
        ],
        cwd=str(repo.parent),
        env={**os.environ, "PYTHONPATH": str(project_root)},
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "missing-language findings" in result.stderr


def test_cli_strict_fail_on_runtime_not_switching(tmp_path):
    """--fail-on-runtime-not-switching exits 2 when browser evidence has that issue."""
    project_root = Path(__file__).resolve().parents[2]
    repo = tmp_path / "repo"
    (repo / "launcher/static").mkdir(parents=True)
    (repo / "launcher/static/index.html").write_text(
        '<div><span class="en">Run</span><span class="ko">실행</span></div>',
        encoding="utf-8",
    )
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "launcher-home-es.json").write_text(
        json.dumps({
            "module": "launcher",
            "state": "home",
            "route": "/",
            "locale": "es",
            "document_lang": "en",
            "body_has_lang_class": False,
            "issue_type": "runtime-not-switching",
        }),
        encoding="utf-8",
    )
    json_out = tmp_path / "audit.json"
    md_out = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable, "-m", "tools.i18n_audit",
            "--repo", str(repo),
            "--browser-evidence-dir", str(evidence_dir),
            "--output-json", str(json_out),
            "--output-md", str(md_out),
            "--fail-on-runtime-not-switching",
        ],
        cwd=str(repo.parent),
        env={**os.environ, "PYTHONPATH": str(project_root)},
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "runtime-not-switching" in result.stderr


def test_module_counts_counts_findings_not_records():
    """summary.module_counts must count findings, not raw records."""
    from tools.i18n_audit.report import build_payload
    from tools.i18n_audit.schema import AuditRecord, Finding

    rec_a = AuditRecord(
        module="launcher", surface="static-html", route_or_state="source",
        source_file="launcher/static/index.html", selector_or_key=".title",
        text_role="body", texts={"en": "Hello", "ko": "안녕"},
    )
    rec_b = AuditRecord(
        module="launcher", surface="static-html", route_or_state="source",
        source_file="launcher/static/index.html", selector_or_key=".subtitle",
        text_role="body", texts={"en": "World", "ko": "세계", "ja": "世界",
                                  "es": "Mundo", "zh-CN": "世界", "zh-TW": "世界"},
    )
    # Only rec_a has a finding
    finding = Finding(
        record_id=rec_a.record_id,
        issue_type="missing-locale",
        severity="High",
        message="Missing ja, es, zh-CN, zh-TW",
    )

    payload = build_payload([rec_a, rec_b], [finding])

    assert payload["summary"]["module_counts"] == {"launcher": 1}
    assert sum(payload["summary"]["module_counts"].values()) == payload["summary"]["finding_count"]


def test_write_json_preserves_generated_at_when_report_content_is_unchanged(tmp_path):
    from tools.i18n_audit.report import write_json

    payload = {
        "generated_at": "new-timestamp",
        "summary": {"record_count": 0, "finding_count": 0},
        "records": [],
        "findings": [],
        "coverage_states": [],
        "brand_terms": [],
    }
    existing_payload = {**payload, "generated_at": "existing-timestamp"}
    report_path = tmp_path / "audit.json"
    report_path.write_text(json.dumps(existing_payload), encoding="utf-8")

    write_json(payload, report_path)

    written = json.loads(report_path.read_text(encoding="utf-8"))
    assert written["generated_at"] == "existing-timestamp"
    assert payload["generated_at"] == "existing-timestamp"

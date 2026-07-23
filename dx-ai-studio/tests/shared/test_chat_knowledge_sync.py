"""P5: SDK knowledge sync generator — generate from .deepx, hash manifest, lazy resync."""
import json

from shared.chat import knowledge_sync as ks


def _fake_suite(tmp_path):
    # .deepx/toolsets + memory under a submodule, plus docs/source
    ts = tmp_path / "dx-runtime" / "dx_app" / ".deepx" / "toolsets"
    ts.mkdir(parents=True)
    (ts / "dx-engine-api.md").write_text("# DX Engine API Reference\nInferenceEngine usage...")
    mem = tmp_path / "dx-compiler" / ".deepx" / "memory"
    mem.mkdir(parents=True)
    (mem / "common_pitfalls.md").write_text("# Common Pitfalls\nBatch size must be 1.")
    docs = tmp_path / "docs" / "source"
    docs.mkdir(parents=True)
    (docs / "faq.md").write_text("# FAQ\nQ: how to compile?")
    # excluded: agent-process docs
    ag = tmp_path / ".deepx" / "agents"
    ag.mkdir(parents=True)
    (ag / "process.md").write_text("# HARD GATE\nrules")
    return tmp_path


def test_generate_writes_sdk_md_and_manifest(tmp_path):
    suite = _fake_suite(tmp_path)
    out = tmp_path / "knowledge"
    n = ks.generate(suite, out)
    assert n == 2  # 1 .deepx/toolsets + 1 docs/source (memory + agents excluded)
    md = (out / "sdk_knowledge.md").read_text()
    assert "## [section:" in md
    assert "DX Engine API Reference" in md and "FAQ" in md
    assert "Common Pitfalls" not in md  # .deepx/memory excluded (internal dev notes)
    assert "HARD GATE" not in md  # agent-process docs excluded
    manifest = json.loads((out / "sdk_manifest.json").read_text())
    assert len(manifest) == 2


def test_section_tags_have_keywords(tmp_path):
    suite = _fake_suite(tmp_path)
    out = tmp_path / "knowledge"
    ks.generate(suite, out)
    md = (out / "sdk_knowledge.md").read_text()
    # filename/title-derived keywords present (e.g. 'engine', 'faq')
    assert "engine" in md and "faq" in md


def test_needs_resync_detects_change(tmp_path):
    suite = _fake_suite(tmp_path)
    out = tmp_path / "knowledge"
    ks.generate(suite, out)
    assert ks.needs_resync(suite, out) is False
    # modify a source → stale
    (suite / "docs" / "source" / "faq.md").write_text("# FAQ\nNEW CONTENT")
    assert ks.needs_resync(suite, out) is True


def test_sync_if_stale_regenerates_once(tmp_path):
    suite = _fake_suite(tmp_path)
    out = tmp_path / "knowledge"
    assert ks.sync_if_stale(suite, out) is True   # first time → generates
    assert ks.sync_if_stale(suite, out) is False  # unchanged → no work

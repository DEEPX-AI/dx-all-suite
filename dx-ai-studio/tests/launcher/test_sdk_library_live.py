"""SDK Library follows the md files in dx-all-suite.

Text is read from disk on every open, so it is always current. **Which files are listed, and their sizes,** must also
come from disk rather than a hand-edited sdk-library-data.json, which misses new documents and drifts on size.
dx_app's change log is a single pymdownx snippet line (`--8<--`) that must be resolved, not shown as is.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _mod():
    spec = importlib.util.spec_from_file_location("sdk_library_under_test", ROOT / "launcher" / "sdk_library.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _suite(tmp_path):
    s = tmp_path / "suite"
    d = s / "dx-runtime/dx_stream/docs/source/docs"
    d.mkdir(parents=True)
    (d / "01_Intro.md").write_text("# Intro\n\nhello\n")
    (d / "02_New_Guide.md").write_text("---\ntitle: x\n---\n\n# New Guide\n\nbody\n")
    (d / "CLAUDE.md").write_text("# not a doc\n")
    (d / "03_Guide_KO.md").write_text("# 가이드\n")
    (d / "RELEASE_NOTES.md").symlink_to('--8<-- "RELEASE_NOTES.md"')   # a broken link like the one in the real suite
    return s


def _data():
    return {"drawers": [{"id": "rt", "sections": [{"id": "stream", "files": [
        {"path": "dx-runtime/dx_stream/docs/source/docs/01_Intro.md", "title": "Intro", "size": 1, "type": "md"},
        {"path": "dx-runtime/dx_stream/docs/source/docs/01_Intro.md", "title": "Intro (dup)", "size": 2, "type": "md"},
        {"path": "pdfs/x.pdf", "title": "PDF", "size": 99, "type": "pdf"}]}]}]}


def test_sizes_come_from_the_disk_and_duplicates_go(tmp_path):
    m = _mod()
    out = m.augment(_data(), _suite(tmp_path))
    files = out["drawers"][0]["sections"][0]["files"]
    intro = [f for f in files if f["path"].endswith("01_Intro.md")]
    assert len(intro) == 1 and intro[0]["title"] == "Intro"
    assert intro[0]["size"] == len("# Intro\n\nhello\n")
    assert next(f for f in files if f["type"] == "pdf")["size"] == 99, "pdf 는 손대지 않는다"


def test_a_new_md_next_to_registered_docs_appears_by_itself(tmp_path):
    m = _mod()
    out = m.augment(_data(), _suite(tmp_path))
    paths = [f["path"] for f in out["drawers"][0]["sections"][0]["files"]]
    assert "dx-runtime/dx_stream/docs/source/docs/02_New_Guide.md" in paths
    new = next(f for f in out["drawers"][0]["sections"][0]["files"] if f["path"].endswith("02_New_Guide.md"))
    assert new["title"] == "New Guide" and new.get("auto") is True
    assert not any(p.endswith("CLAUDE.md") for p in paths), "agent 지시 파일은 문서가 아니다"
    assert not any(p.endswith("RELEASE_NOTES.md") for p in paths), "깨진 symlink 은 문서가 아니다"
    assert m.allowed_paths(out) >= {"dx-runtime/dx_stream/docs/source/docs/02_New_Guide.md"}


def test_a_pymdownx_snippet_is_expanded(tmp_path):
    m = _mod()
    s = tmp_path / "suite"
    app = s / "dx-runtime/dx_app"
    (app / "docs/source/docs").mkdir(parents=True)
    (app / "RELEASE_NOTES.md").write_text("# Release Notes\n\n## v3.2.2\n")
    text = '--8<-- "RELEASE_NOTES.md"\n'
    out = m.expand_snippets(text, "dx-runtime/dx_app/docs/source/docs/Appendix_Change_Log.md", s)
    assert out.startswith("# Release Notes") and "--8<--" not in out

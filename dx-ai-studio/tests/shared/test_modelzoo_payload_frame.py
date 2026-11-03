"""developer.deepx.ai/modelzoo/ now wraps the catalog in an iframe (wp-content/uploads/modelzoo.html).

The outer page carries no window.__MODEL_ZOO_DATA__, so both public readers (DX App's ModelZoo tab and the
Model Zoo module's public adapter) follow the same-host frame that does.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = (ROOT / "tests" / "dx_modelzoo" / "fixtures" / "public_modelzoo_payload.html").read_text(encoding="utf-8")
PAGE_URL = "https://developer.deepx.ai/modelzoo/"
FRAME_URL = "https://developer.deepx.ai/wp-content/uploads/modelzoo.html?v=1792140647"
WRAPPER = ('<html><body><div class="ct-code-block"><iframe id="dx-modelzoo-frame" '
           'src="https://developer.deepx.ai/wp-content/uploads/modelzoo.html?v=1792140647" '
           'title="DX Model Zoo"></iframe></div></body></html>')


def test_frame_url_is_found_on_the_wrapper_page():
    from shared.modelzoo_payload import payload_frame_url
    assert payload_frame_url(WRAPPER, PAGE_URL) == FRAME_URL


def test_relative_frame_src_is_resolved_against_the_page():
    from shared.modelzoo_payload import payload_frame_url
    html = '<iframe id="dx-modelzoo-frame" src="/wp-content/uploads/modelzoo.html?v=2"></iframe>'
    assert payload_frame_url(html, PAGE_URL) == "https://developer.deepx.ai/wp-content/uploads/modelzoo.html?v=2"


def test_a_frame_on_another_host_is_not_followed():
    from shared.modelzoo_payload import payload_frame_url
    html = '<iframe id="dx-modelzoo-frame" src="https://evil.example/modelzoo.html"></iframe>'
    assert payload_frame_url(html, PAGE_URL) is None


def test_a_page_that_carries_the_payload_needs_no_frame():
    from shared.modelzoo_payload import payload_frame_url
    assert payload_frame_url(PAYLOAD, PAGE_URL) is None


def test_dx_app_public_list_follows_the_frame(monkeypatch):
    from dx_app.core import modelzoo as M

    pages = {PAGE_URL: WRAPPER, FRAME_URL: PAYLOAD}
    monkeypatch.setattr(M, "_fetch_url", lambda source, url: (pages.get(url), None if url in pages else "404"))
    monkeypatch.setitem(M._cache, "models", None)
    r = M.modelzoo_list(M.SOURCE_PUBLIC)
    assert r["ok"], r
    assert len(r["models"]) == 8


def test_model_zoo_public_adapter_follows_the_frame(tmp_path):
    from dx_modelzoo.metadata.adapters import public_modelzoo_adapter

    pages = {PAGE_URL: WRAPPER, FRAME_URL: PAYLOAD}
    result = public_modelzoo_adapter(tmp_path, publish_url=PAGE_URL, fetch_text=lambda url: pages[url])
    assert result["ok"], result["errors"]
    assert len(result["models"]) == 8

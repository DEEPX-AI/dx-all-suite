"""--internal-html feeds a saved publish page to the internal adapter, keeping TLS verification on."""
from dx_modelzoo.tools import sync_metadata


def test_internal_html_is_read_from_the_file(tmp_path, monkeypatch):
    page = tmp_path / "publish.html"
    page.write_text("<table></table>", encoding="utf-8")
    seen = {}

    def fake_run_sync(**kwargs):
        seen.update(kwargs)
        return {"catalog": {"models": [1]}, "report": {"model_count": 1, "adapter_errors": []}}

    monkeypatch.setattr(sync_metadata, "run_sync", fake_run_sync)
    sync_metadata.main(["--source", "internal", "--internal-html", str(page), "--output", str(tmp_path / "o.json")])
    kwargs = seen["adapter_kwargs"]["internal_modelzoo"]
    assert kwargs["fetch_text"]("https://ignored") == "<table></table>"
    assert "verify_tls" not in kwargs

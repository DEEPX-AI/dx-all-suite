import pathlib

JS = (pathlib.Path(__file__).resolve().parents[2] / "dx_compiler" / "static" / "js" / "auto_compile.js").read_text()


def test_populates_from_status():
    assert "/agent/api/agent/status" in JS
    assert "authenticated" in JS


def test_disables_unauthenticated_and_buttons():
    assert "disabled" in JS
    # both buttons referenced for enable/disable control
    assert "auto-compile-noninteractive" in JS and "auto-compile-interactive" in JS

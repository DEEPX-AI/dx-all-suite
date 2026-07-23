from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
JS_DIR = ROOT / "dx_app/static/js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    paren = source.index("(", start)
    depth = 0
    close_paren = None
    for pos in range(paren, len(source)):
        if source[pos] == "(":
            depth += 1
        elif source[pos] == ")":
            depth -= 1
            if depth == 0:
                close_paren = pos
                break
    assert close_paren is not None
    brace = source.index("{", close_paren)
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1:pos]
    raise AssertionError(f"Could not parse function body for {signature}")


def test_compare_ab_run_has_inflight_guard_and_toast():
    source = _read(JS_DIR / "compare.js")
    body = _function_body(source, "async function doABRun(")

    assert "var _abInFlight=false;" in source or "let _abInFlight=false;" in source
    assert "if(_abInFlight)" in body or "if (_abInFlight)" in body
    assert "Run already in progress" in body
    assert "toast(T('Run already in progress'),'warn')" in body or \
           'toast(T("Run already in progress"),"warn")' in body


def test_compare_ab_run_disables_button_in_try_finally():
    source = _read(JS_DIR / "compare.js")
    body = _function_body(source, "async function doABRun(")

    assert "const btn=$('ab-run-btn');" in body or "var btn=$('ab-run-btn');" in body
    assert "btn.disabled=true" in body
    assert "finally" in body
    assert "btn.disabled=false" in body
    assert body.index("btn.disabled=true") < body.index("await postJ('/api/run_multi'")
    assert body.index("btn.disabled=false") > body.index("finally")


def test_quick_run_uses_pending_auto_select_after_init_run_page():
    """Models ▶ Run must survive initRunPage() dropdown rebuild (PENDING_AUTO_SELECT)."""
    source = _read(JS_DIR / "inference.js")
    quick_body = _function_body(source, "function quickRun(")

    assert "var PENDING_AUTO_SELECT=null;" in source
    assert "PENDING_AUTO_SELECT={name:name,category:cat" in quick_body
    assert "nav('run')" in quick_body
    assert "cs.value=cat" not in quick_body
    assert "function _applyPendingAutoSelect(" in source
    init_body = _function_body(source, "function initRunPage(")
    assert "_applyPendingAutoSelect()" in init_body


def test_run_params_loaded_from_model_config_bindings():
    source = _read(JS_DIR / "inference.js")
    assert "var RUN_PARAM_BINDINGS=" in source
    assert "function applyRunParamsFromModel(" in source
    assert "function collectRunConfigOverrides(" in source
    do_run = _function_body(source, "async function doRun(")
    assert "config_overrides:collectRunConfigOverrides()" in do_run
    assert "conf_threshold:parseFloat" not in do_run
    on_model = _function_body(source, "function onRModel(")
    assert "applyRunParamsFromModel(m)" in on_model


def test_inference_run_inflight_guard_warns_and_disables_run_button():
    source = _read(JS_DIR / "inference.js")
    body = _function_body(source, "async function doRun(")

    assert "var _runInFlight=false;" in source
    assert "if(_runInFlight)" in body or "if (_runInFlight)" in body
    assert "Run already in progress" in body
    assert "toast(T('Run already in progress'),'warn')" in body or \
           'toast(T("Run already in progress"),"warn")' in body
    assert "const runBtn=$('r-run-btn');" in body or "var runBtn=$('r-run-btn');" in body
    assert "runBtn.disabled=true" in body
    assert "finally" in body
    assert "runBtn.disabled=false" in body
    assert body.index("runBtn.disabled=true") < body.index("await postJ('/api/run'")
    assert body.index("runBtn.disabled=false") > body.index("finally")

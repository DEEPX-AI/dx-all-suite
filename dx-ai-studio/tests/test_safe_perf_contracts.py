from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def test_monitor_dashboard_skips_hidden_polling_and_unchanged_status_render():
    source = _read(ROOT / "dx_monitor/static/js/dashboard.js")
    apply_body = _function_body(source, "function _applyHWData(")
    poll_body = _function_body(source, "function _startHWPoll(")
    events_body = _function_body(source, "function pollEvents(")

    assert "function _isMonitorVisible(" in source
    assert "function _hwStatusSignature(" in source
    assert "if (statusSig !== S._lastStatusSig)" in apply_body
    assert "if (!_isMonitorVisible()) return;" in poll_body
    assert "if (!_isMonitorVisible()) return;" in events_body


def test_benchmark_hover_hit_testing_is_raf_throttled():
    source = _read(ROOT / "dx_benchmark/static/js/dashboard.js")

    assert "function scheduleBenchmarkHover(chart, event)" in source
    assert "chart._hoverRaf = requestAnimationFrame(function()" in source
    assert "_handleHover: function(e){scheduleBenchmarkHover(this,e);}" in source
    assert "chart._handleHover=function(e){scheduleBenchmarkHover(this,e);};" in source


def test_benchmark_canvas_resize_writes_only_on_dimension_changes():
    source = _read(ROOT / "dx_benchmark/static/js/dashboard.js")

    assert "function setBenchmarkCanvasSize(" in source
    assert "if (canvas.width !== nextW) canvas.width = nextW;" in source
    assert "if (canvas.height !== nextH) canvas.height = nextH;" in source
    assert "this._canvas.width=w*dpr" not in source
    assert "this._canvas.height=h*dpr" not in source
    assert "canvas.width=w*dpr" not in source
    assert "canvas.height=h*dpr" not in source


def test_safe_transition_contracts_avoid_transition_all_on_hot_controls():
    checks = [
        (ROOT / "launcher/static/style.css", ".dot", "transition: background-color 0.5s, box-shadow 0.5s"),
        (ROOT / "launcher/static/style.css", ".launch-card", "transition: background 0.3s cubic-bezier"),
        (ROOT / "dx_app/static/css/style.css", ".chat-model-btn", "transition: background-color .15s, color .15s, border-color .15s, box-shadow .15s"),
        (ROOT / "dx_stream/static/css/stream.css", ".palette-item", "transition: background-color .12s ease, color .12s ease"),
        (ROOT / "dx_benchmark/static/css/style.css", ".edgeguide-link", "transition: box-shadow .18s ease, transform .18s ease"),
    ]
    for path, selector, expected in checks:
        source = _read(path)
        start = source.index(selector)
        block = source[start:source.index("}", start)]
        assert expected in block
        assert "transition: all" not in block

"""dx_com 2.4 compat: html_export bridge must drop kwargs the installed dx_com
generate_summary_html no longer accepts (e.g. `enhanced_scheme`), instead of TypeError."""
from dx_compiler.core.html_export import _filter_kwargs


def test_filter_drops_unaccepted_kwargs():
    def fn(model_path, output_dir, *, use_q_pro=False, calibration_method=None):
        return "ok"
    filtered = _filter_kwargs(fn, {
        "model_path": "m", "output_dir": "o",
        "use_q_pro": True, "enhanced_scheme": {"DXQ-P0": {}},  # 2.3-only, gone in 2.4
        "calibration_method": "ema",
    })
    assert "enhanced_scheme" not in filtered
    assert filtered == {"model_path": "m", "output_dir": "o",
                        "use_q_pro": True, "calibration_method": "ema"}
    fn(**filtered)  # must not raise


def test_filter_keeps_all_when_varkw():
    def fn(model_path, **kwargs):
        return "ok"
    kw = {"model_path": "m", "enhanced_scheme": {}, "anything": 1}
    assert _filter_kwargs(fn, kw) == kw

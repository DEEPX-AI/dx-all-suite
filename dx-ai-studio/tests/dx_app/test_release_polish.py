"""Release polish contracts for DX App."""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_app"
JS_DIR = APP / "static" / "js"
CORE_DIR = APP / "core"
TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")

ERROR_KEYS = (
    "no_model_file",
    "model_not_found",
    "image_base64_too_large",
    "invalid_image_base64",
    "camera_not_found",
    "rtsp_required",
    "input_not_found",
    "path_outside_allowed_roots",
    "file_extension_not_allowed",
    "binary_not_found",
    "script_not_found",
    "process_exit",
    "inference_timeout",
    "inference_exception",
    "failed_camera_mux",
    "live_mode_unsupported",
    "live_cpp_only",
    "invalid_payload",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dict_keys() -> set[str]:
    return set(re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", _read(JS_DIR / "i18n.js")))


def _dict_entry(key: str) -> str:
    match = re.search(
        rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}}\s*(?:,|\n)",
        _read(JS_DIR / "i18n.js"),
        re.S,
    )
    return match.group(1) if match else ""


def _load_inference_module():
    sys.path.insert(0, str(APP))
    sys.path.insert(0, str(CORE_DIR))
    for name in ("inference", "config", "dx_app_security", "performance", "hardware"):
        sys.modules.pop(name, None)
    return importlib.import_module("inference")


def _extract_braced_body(source: str, anchor: str) -> str:
    start = source.find(anchor)
    assert start != -1, f"anchor {anchor!r} not found"
    brace_start = source.find("{", start)
    assert brace_start != -1, f"opening brace for {anchor!r} not found"
    depth = 0
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start + 1 : index]
    raise AssertionError(f"closing brace for {anchor!r} not found")


def test_inference_no_model_file_returns_translatable_error_key():
    inf = _load_inference_module()

    res = inf.run_inference("ghost", "classification", "")

    assert res["error_key"] == "no_model_file"
    assert "error" in res


def test_inference_missing_model_returns_translatable_error_key():
    inf = _load_inference_module()

    res = inf.run_inference("ghost", "classification", "assets/models/missing-release-polish.dxnn")

    assert res["error_key"] == "model_not_found"
    assert "missing-release-polish.dxnn" in res["error"]


def test_run_multi_executor_exception_returns_translatable_error_key():
    inf = _load_inference_module()
    original_run_inference = inf.run_inference

    def raise_from_worker(**_kwargs):
        raise RuntimeError("worker exploded")

    inf.run_inference = raise_from_worker
    try:
        res = inf.run_multi([{"model_name": "ghost"}])
    finally:
        inf.run_inference = original_run_inference

    assert res[0]["error_key"] == "inference_exception"
    assert res[0]["slot"] == 0
    assert "worker exploded" in res[0]["error"]


def test_server_extension_validation_uses_specific_error_key():
    source = _read(APP / "server.py")
    assert "file_extension_not_allowed" in source
    assert re.search(r'if "Extension" in message:.*?file_extension_not_allowed', source, re.S)


def test_dx_app_error_keys_exist_in_i18n_dictionary():
    keys = _dict_keys()
    missing = [key for key in ERROR_KEYS if key not in keys]
    assert not missing, f"Missing DX App error i18n keys: {missing}"


def test_dx_app_error_keys_cover_all_target_languages():
    incomplete = {}
    for key in ERROR_KEYS:
        entry = _dict_entry(key)
        missing_langs = [
            lang
            for lang in TARGET_LANGS
            if f"{lang}:" not in entry
            and f"'{lang}':" not in entry
            and f'"{lang}":' not in entry
        ]
        if missing_langs:
            incomplete[key] = missing_langs
    assert not incomplete, incomplete


def test_frontend_run_and_benchmark_translate_error_key_before_raw_error():
    for filename in ("inference.js", "benchmark.js"):
        source = _read(JS_DIR / filename)
        assert "error_key" in source, f"{filename} must read backend error_key"
        assert re.search(r"T\([^)]*error_key", source), (
            f"{filename} must translate error_key through T() before falling back to raw error"
        )


def test_benchmark_summary_does_not_merge_failed_and_errors():
    source = _read(JS_DIR / "benchmark.js")
    assert "failed+errors" not in source
    assert "(failed+errors)" not in source
    assert "T('Failed / Error')" not in source


def test_benchmark_treats_any_error_payload_as_error_status():
    source = _read(JS_DIR / "benchmark.js")
    assert "var isErr=!!res.error;" in source
    assert "var status=r.error?'ERROR':(r.exit_code===0?'PASS':'FAIL');" in source
    assert "res.error&&res.exit_code==null" not in source


def test_benchmark_summary_has_dedicated_failed_and_errors_cards():
    source = _read(JS_DIR / "benchmark.js")
    assert re.search(r'class="val red"\s*>\'\+failed\+', source), (
        "benchmark report must render failed count separately"
    )
    assert re.search(r"class=\"val [^\"]*amber|color:#D29922", source), (
        "benchmark report must render runtime error count with a separate visual treatment"
    )
    assert "T('Errors')" in source


def test_benchmark_category_summary_tracks_errors_separately():
    source = _read(JS_DIR / "benchmark.js")
    assert re.search(r"cats\[.*?\]\s*=\s*\{[^}]*errors\s*:\s*0", source)
    assert re.search(r"status\s*===\s*['\"]ERROR['\"].*?\.errors\+\+", source, re.S)
    assert "T('Errors')" in source


def test_benchmark_report_splits_runtime_errors_from_accuracy_failures():
    source = _read(JS_DIR / "benchmark.js")
    combined_filter = re.search(
        r"r\.error\s*\|\|\s*\(r\.exit_code\s*!=\s*null.*?r\.exit_code\s*!==\s*0\)",
        source,
        re.S,
    )
    assert not combined_filter, (
        "benchmark report must not mix runtime errors and FAIL exit codes in one details list"
    )
    assert "failModels" in source
    assert "errModels" in source


def test_continuous_grid_shows_waiting_copy_for_queued_slots():
    """Queued slots must be distinguishable from idle pre-start slots."""
    source = _read(JS_DIR / "inference.js")
    match = re.search(r"function contRenderGrid\(\)\{(.*?)\n\}", source, re.S)
    assert match, "contRenderGrid() not found"
    grid_body = match.group(1)

    assert "T('⏳ Waiting…')" in grid_body, (
        "contRenderGrid must show explicit Waiting copy while sequential inference is running"
    )
    assert "CONT.running" in grid_body, (
        "contRenderGrid must choose idle vs queued copy from the running state"
    )


def test_continuous_result_errors_use_translated_error_key():
    source = _read(JS_DIR / "inference.js")
    body = _extract_braced_body(source, "function contShowResult")

    assert "translatedError(res)" in body, (
        "continuous sequential slot errors must use translated error_key before raw error"
    )
    assert "esc(res.error)" not in body


def test_continuous_live_start_errors_use_translated_error_key():
    source = _read(JS_DIR / "inference.js")
    body = _extract_braced_body(source, "async function contStartLive")

    assert "translatedError(res)" in body, (
        "continuous live start errors must use translated error_key before raw error"
    )
    assert "+res.error" not in body

import json

from tools.i18n_audit.browser_evidence import (
    BrowserObservation,
    load_browser_evidence,
    stable_visible_text_sample,
    write_browser_observation,
)


def test_browser_observation_writes_stable_json(tmp_path):
    observation = BrowserObservation(
        module="dx_stream",
        state="entry",
        route="/",
        locale="es",
        document_lang="en",
        body_has_lang_class=False,
        visible_text_sample=("Run", "Pipeline"),
        issue_type="runtime-not-switching",
    )

    path = write_browser_observation(tmp_path, observation)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["module"] == "dx_stream"
    assert payload["locale"] == "es"
    assert payload["issue_type"] == "runtime-not-switching"
    assert path.name == "dx_stream-entry-es.json"


def test_load_browser_evidence_reads_all_json(tmp_path):
    write_browser_observation(
        tmp_path,
        BrowserObservation(
            module="launcher",
            state="home",
            route="/",
            locale="ko",
            document_lang="ko",
            body_has_lang_class=True,
            visible_text_sample=("홈",),
            issue_type="observed",
        ),
    )

    assert load_browser_evidence(tmp_path)[0]["module"] == "launcher"


def test_stable_visible_text_sample_filters_boot_animation_glyphs():
    sample = stable_visible_text_sample("E\nH\n2\nAI Studio\n전체 시스템 가동\n클릭하여 건너뛰기")

    assert sample == ("AI Studio", "전체 시스템 가동", "클릭하여 건너뛰기")


def test_stable_visible_text_sample_filters_symbol_only_controls():
    sample = stable_visible_text_sample("DX\nCompiler\n🌏\nEN\n▾\n🎓\n❓\nInput\nPrepared")

    assert sample == ("DX", "Compiler", "EN", "Input", "Prepared")


def test_stable_visible_text_sample_filters_volatile_telemetry_values():
    sample = stable_visible_text_sample("NPU Hardware Monitoring\nEN\nNPU 0\n36.1°C\n(Mock)\nDRAM")

    assert sample == ("NPU Hardware Monitoring", "EN", "NPU 0", "(Mock)", "DRAM")


def test_load_browser_evidence_returns_empty_for_none_or_missing(tmp_path):
    assert load_browser_evidence(None) == []
    assert load_browser_evidence(tmp_path / "missing") == []

"""AI Help knowledge pages must not repeat claims the code no longer backs.

Each phrase below contradicts the code and must stay out of shared/chat/knowledge/*.md; the
positive anchors are the correct wording. If a page brings a stale phrase back, the
in-app chat starts answering with it again.
"""
from pathlib import Path

import pytest

from shared.chat import module_fallbacks

KNOWLEDGE = Path(__file__).resolve().parents[2] / "shared" / "chat" / "knowledge"


def _page(name):
    return (KNOWLEDGE / name).read_text(encoding="utf-8")


STALE = {
    "base.md": [
        "~5 TOPS",                    # DX-M1 is 25 TOPS (dx_planner/data/npu.json)
        "PCIe/USB",
        "DX-AllSuite v2.3.0",         # pinned versions went stale; see release.ver
        "Runtime v3.3.0",
        "270+",                       # Model Zoo catalog has ~500 models
        "280+",
    ],
    "dx_app.md": [
        "(v3.1.0)",
        "DX App 내장 컴파일",           # no compile page in DX App
        "커뮤니티 포럼",                # forum.js is not loaded
        "NPU 하드웨어 모니터링 (온도, 전압, 클럭)",  # that is DX Monitor
        "18개 데모",                    # run_demo.sh list changes per release
        "YOLOV11N.dxnn",
        "| 6. Compiler |",              # setup has no compiler step
        "Setup → Compiler",
        "verify_inference_output.py",  # script does not exist
        "**Run** 클릭",                 # the button is "Run Inference"
    ],
    "dx_stream.md": [
        "(v3.0.0)",
        "10종 프리셋 데모",              # 12 demos in dx_stream/core/demos.py
        "**Validate**",                # toolbar is Run/Stop/Export/Import/Preset
        "P=일시정지",                   # no such shortcuts
        "`color-format`",              # property names from dx_stream/core/elements.py
        "`lib-path`",
        "`batch-size`",
        "`min-hits`",
        "3회 (1초/2초/4초 간격)",        # webrtc-client.js: 5 retries
        "(100ms 간격)",                 # ICE poll is 1 s
    ],
    "dx_modelzoo.md": [
        "dx_tool.sh eval",
        "dx_tool.sh compile",
        "info --model",
        "**Demo** 탭",
        "270+",
    ],
    "dx_compiler.md": [
        "DX-COM v2.3.0",
        "dxcom compile",
        "--quant",
        "--opt-level 3",
        "(0=없음 ~ 3=최대)",
        "weight_dtype",
        "activation_dtype",
        "`entropy`, `percentile`, `kl`",
        "Calculate Exclude",
        "Submit →",
        "`compiler_uploads/`",
    ],
    "dx_benchmark.md": [
        "benchmark.sh",
        "python -m dx_benchmark.core",
        "/dev/dxnn",
        "dxnn-driver",
        "i7-14700K",
        "바로 조회할 수 있습니다",
        "4개의 서브탭",
    ],
    "dx_monitor.md": [
        "스왑, 디스크",
        "메모리 / 스왑 / 디스크",
        "**Mock 텔레메트리**로 자동 대체",
    ],
    "dx_agent_dev.md": [
        "팀 내부 `copilot` 기반",
        "- `copilot` CLI가 PATH에 없음",
    ],
}

CURRENT = {
    "base.md": ["25 TOPS", "release.ver", "약 500개"],
    "dx_app.md": ["Run Inference", "Continuous", "DX-Runtime Build", "Sample Assets Setup",
                  "./run_demo.sh --help", "DX Compiler"],
    "dx_stream.md": ["12종 프리셋 데모", "Instance Segmentation", "`model-path`",
                     "`library-file-path`", "Remote (MJPEG)", "mpph264enc"],
    "dx_modelzoo.md": ["./scripts/dx_tool.sh info yolov8", "Upload Image", "Sample Image"],
    "dx_compiler.md": ["dxcom -m model.onnx -c config.json -o output/", "--opt_level 0",
                       "DXQ-P0", "`EMA`", "Calculate Range", "**Compile**", "var/compiler/uploads/"],
    "dx_benchmark.md": ["./run.sh preflight", "./run.sh run", "/dev/dxrt", "ORT ON/OFF"],
    "dx_monitor.md": ["DX_MONITOR_EXPLICIT_MOCK=1", "NPU telemetry unavailable"],
    "dx_agent_dev.md": ["cursor-agent", "opencode", "**Stop**"],
    "dx_edge.md": ["`/cloud/`", "**Check connection**", "**Upload and compile**", "**Register device**"],
}


@pytest.mark.parametrize("page,phrase", [(p, s) for p, items in STALE.items() for s in items])
def test_stale_phrase_absent(page, phrase):
    assert phrase not in _page(page), f"{page} still says {phrase!r}"


@pytest.mark.parametrize("page,phrase", [(p, s) for p, items in CURRENT.items() for s in items])
def test_current_phrase_present(page, phrase):
    assert phrase in _page(page), f"{page} lost {phrase!r}"


def test_section_headers_still_parse():
    for page in CURRENT:
        text = _page(page)
        assert "## [section:" in text, page


def test_monitor_fallback_does_not_mention_disk():
    disk_words = ("disk", "디스크", "ディスク", "磁盘", "磁碟", "disco")
    for _keys, answers in module_fallbacks.rules("dx_monitor"):
        for lang, text in answers.items():
            assert not any(w in text for w in disk_words), (lang, text)


def test_knowledge_does_not_pin_module_ports():
    """Module servers bind ephemeral ports behind the launcher; the pages quoted 8080/8093-8099 and a launcher on 8890."""
    import re
    from pathlib import Path

    kdir = Path(__file__).resolve().parents[2] / "shared/chat/knowledge"
    for f in kdir.glob("*.md"):
        if f.name.startswith("sdk_"):
            continue
        text = f.read_text(encoding="utf-8")
        assert not re.search(r"포트 80\d\d|\(80\d\d\)|포트\(80\d\d\)|localhost:8890|:8080\b", text), f.name


def test_monitor_tutorial_does_not_promise_automatic_mock_data():
    """The Monitor reference must not say it 'operates with mock data when no NPU is connected' or that disk is shown:
    mock needs DX_MONITOR_EXPLICIT_MOCK=1, otherwise the page says NPU telemetry unavailable."""
    from pathlib import Path

    tut = (Path(__file__).resolve().parents[2] / "dx_monitor/static/js/tutorial.js").read_text(encoding="utf-8")
    assert "Operates with <strong>simulated (mock) data</strong> when no NPU is connected" not in tut
    assert "DX_MONITOR_EXPLICIT_MOCK=1" in tut and "NPU telemetry unavailable" in tut
    assert "CPU, memory, and disk values are always real" not in tut


def test_nothing_points_users_at_workspace_agent_sessions():
    """The Agent Dev hint, tutorial and manual must not send outputs to workspace/agent-sessions/ — a folder that
    does not exist; the agent writes to dx-agent-dev/<session>/ in the project it works on."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for rel in ("dx_agent_dev/templates/index.html", "dx_agent_dev/static/js/i18n.js",
                "dx_agent_dev/static/js/tutorial.js", "docs/source/10_DX_Agent_Dev.md", "dx_agent_dev/README.md"):
        assert "workspace/agent-sessions" not in (root / rel).read_text(encoding="utf-8"), rel


def test_the_module_table_says_where_studio_opens_each_module():
    """Asked where the NPU temperature is, Chat must not answer "DX Monitor (port 8098)". Under the launcher every
    module opens at a path on :8899 (8098 is only the standalone default), and the rail's NPU Monitor
    button shows the temperature on every screen."""
    from launcher.launcher import _MODULE_PROXY_PATHS
    base = _page("base.md")
    table = base[base.index("### DX AI Studio 앱 구성"):base.index("### 에코시스템 파트너")]
    for path in _MODULE_PROXY_PATHS.values():
        assert f"`{path}`" in table, path
    assert "| 8098 |" not in table
    assert "NPU Monitor" in table
    from launcher.launcher import LAUNCHER_PORT
    assert f":{LAUNCHER_PORT}" in base and ":8899" not in base     # the default, not one PC's custom port

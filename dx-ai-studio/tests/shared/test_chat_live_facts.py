"""Chat gets this PC's dx_app example layout as a fact (2026-10-11 real-use audit).

Asked "DX-M1 에서 yolo26n 예제를 실행하는 명령" through the agent-cli provider, Chat answered
`python src/python_example/object_detection/yolo26n/yolo26n_sync.py --input ...`: the legacy path (this box has
the per-model layout, where that folder holds only factory/) and a flag that does not exist (`--image`/`-i`).
The knowledge page lists both layouts and the model picked the wrong one, so the prompt now carries the layout
Studio detected with a runnable example command.
"""
from __future__ import annotations

from pathlib import Path

from shared import dx_app_layout
from shared.chat import live_facts
from shared.chat.prompt_builder import build_system_prompt


def _touch(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")


def _facts(root: Path) -> str:
    dx_app_layout.clear_cache()
    live_facts.clear_cache()
    try:
        return live_facts.dx_app_facts(root)
    finally:
        dx_app_layout.clear_cache()
        live_facts.clear_cache()


def test_per_model_tree_gives_the_per_model_command(tmp_path):
    _touch(tmp_path / "src/python_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.py")
    _touch(tmp_path / "src/python_example/object_detection/yolo26n/factory/__init__.py")
    facts = _facts(tmp_path)
    assert "per-model" in facts
    assert ("python src/python_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.py"
            " -m assets/models/yolo26-n_640x640.dxnn -i sample/img/sample_dog.jpg") in facts
    assert "--image" in facts and "--input" not in facts
    assert "yolo26n/yolo26n_sync.py" not in facts


def test_legacy_tree_gives_the_legacy_command(tmp_path):
    _touch(tmp_path / "src/python_example/object_detection/yolo26n/yolo26n_sync.py")
    facts = _facts(tmp_path)
    assert "legacy" in facts
    assert "python src/python_example/object_detection/yolo26n/yolo26n_sync.py" in facts


def test_cpp_binaries_are_reported_only_when_built(tmp_path):
    _touch(tmp_path / "src/python_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.py")
    assert "./build.sh" in _facts(tmp_path)
    (tmp_path / "bin").mkdir()
    exe = tmp_path / "bin/yolo26-n_640x640_sync"
    _touch(exe)
    exe.chmod(0o755)
    facts = _facts(tmp_path)
    assert "./bin/yolo26-n_640x640_sync -m assets/models/yolo26-n_640x640.dxnn -i sample/img/sample_dog.jpg" in facts


def test_no_dx_app_gives_no_facts(tmp_path):
    assert _facts(tmp_path / "missing") == ""


def test_the_system_prompt_carries_the_facts(tmp_path, monkeypatch):
    monkeypatch.setattr(live_facts, "system_facts", lambda: "## 이 PC 의 dx_app\n- marker-fact")
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    prompt = build_system_prompt(knowledge, "launcher", "yolo26n 실행 명령")
    assert "marker-fact" in prompt

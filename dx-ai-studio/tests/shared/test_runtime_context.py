"""Tests for resolving Studio's active runtime launch context."""
from pathlib import Path

import pytest


def test_resolve_active_context_supplies_profile_environment_facts(tmp_path):
    from shared.runtime_context import resolve_active_runtime_context
    from shared.runtime_state import RuntimePhase, RuntimeState, RuntimeStateStore

    state = RuntimeStateStore(tmp_path / "state.json")
    state.save(RuntimeState(active_version="2.4.1", phase=RuntimePhase.ACTIVE))
    interpreter = tmp_path / "infer" / "bin" / "python3"
    interpreter.parent.mkdir(parents=True)
    interpreter.touch()
    library = tmp_path / "runtime" / "lib"
    plugin = tmp_path / "runtime" / "gst"
    postprocess = tmp_path / "runtime" / "postprocess"
    for path in (library, plugin, postprocess):
        path.mkdir(parents=True)

    context = resolve_active_runtime_context(
        state_store=state,
        python_executable=interpreter,
        library_dirs=(library,),
        plugin_dir=plugin,
        postprocess_lib_dir=postprocess,
    )

    assert context.version == "2.4.1"
    assert context.venv_root == interpreter.parent.parent
    assert context.library_dirs == (library,)
    assert context.plugin_dir == plugin


def test_resolve_active_context_rejects_non_active_journal(tmp_path):
    from shared.runtime_context import RuntimeContextError, resolve_active_runtime_context
    from shared.runtime_state import RuntimeStateStore

    with pytest.raises(RuntimeContextError, match="not active"):
        resolve_active_runtime_context(state_store=RuntimeStateStore(tmp_path / "state.json"))


def test_resolve_active_context_excludes_checkout_library_dirs(tmp_path, monkeypatch):
    import shared.runtime_context as context_api
    from shared.paths import DX_RUNTIME_ROOT
    from shared.runtime_state import RuntimePhase, RuntimeState, RuntimeStateStore

    state = RuntimeStateStore(tmp_path / "state.json")
    state.save(RuntimeState(active_version="2.4.1", phase=RuntimePhase.ACTIVE))
    interpreter = tmp_path / "infer" / "bin" / "python3"
    interpreter.parent.mkdir(parents=True)
    interpreter.touch()
    monkeypatch.setattr(context_api, "runtime_python", lambda: str(interpreter))

    context = context_api.resolve_active_runtime_context(state_store=state)

    assert all(
        not path.resolve().is_relative_to(DX_RUNTIME_ROOT.resolve())
        for path in context.library_dirs
    )
"""App/Stream launch-contract split in the runtime launch gate."""
from shared.runtime_contract import ContractResult
from shared.runtime_profile import ContractCheck
from shared.runtime_gate import module_start_policy
from shared.runtime_state import RuntimePhase, RuntimeState, RuntimeStateStore


def _check(cid, passed):
    return ContractCheck(check_id=cid, required="", observed="", passed=passed, remediation="")


_ALL = ("app.python", "gst.plugin", "gst.dxinfer", "gst.postprocess_directory")


def _store(tmp_path, phase, version=None):
    s = RuntimeStateStore(tmp_path / "state.json")
    s.save(RuntimeState(active_version=version, candidate_version=None, phase=phase, reason=""))
    return s


def test_validate_module_contracts_returns_only_relevant_checks(monkeypatch):
    import shared.runtime_validation as rv

    monkeypatch.setattr(rv, "validate_base_runtime",
                        lambda **_: ContractResult(tuple(_check(c, True) for c in _ALL)))
    stream = {c.check_id for c in rv.validate_module_contracts("dx_stream").checks}
    app = {c.check_id for c in rv.validate_module_contracts("dx_app").checks}
    assert stream == {"gst.plugin", "gst.dxinfer", "gst.postprocess_directory"}
    assert app == {"app.python"}


def test_active_profile_allows_without_live_check(tmp_path, monkeypatch):
    import shared.runtime_validation as rv
    # If the fast path is used, validate_module_contracts must NOT be called.
    monkeypatch.setattr(rv, "validate_module_contracts",
                        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("should not run")))
    store = _store(tmp_path, RuntimePhase.ACTIVE, "2.4.0")
    assert module_start_policy("dx_stream", store).allowed is True


def test_degraded_allows_module_whose_own_contracts_pass(tmp_path, monkeypatch):
    # Runtime not globally active, but dx_stream's own contracts pass while dx_app's fail:
    # dx_stream is allowed, dx_app is blocked — one broken half doesn't gate the other.
    import shared.runtime_validation as rv

    def fake(module, **_):
        ok = module != "dx_app"  # app.python broken, stream fine
        ids = {"dx_stream": ("gst.plugin", "gst.dxinfer", "gst.postprocess_directory"),
               "dx_app": ("app.python",)}[module]
        return ContractResult(tuple(_check(c, ok) for c in ids))

    monkeypatch.setattr(rv, "validate_module_contracts", fake)
    store = _store(tmp_path, RuntimePhase.FAILED, None)
    assert module_start_policy("dx_stream", store).allowed is True
    blocked = module_start_policy("dx_app", store)
    assert blocked.allowed is False
    assert blocked.reason.check_id == "profile.active"


def test_degraded_blocks_when_module_contracts_fail(tmp_path, monkeypatch):
    import shared.runtime_validation as rv
    monkeypatch.setattr(rv, "validate_module_contracts",
                        lambda module, **_: ContractResult((_check("gst.plugin", False),)))
    store = _store(tmp_path, RuntimePhase.FAILED, None)
    assert module_start_policy("dx_stream", store).allowed is False


def test_non_inference_module_always_allowed(tmp_path):
    store = _store(tmp_path, RuntimePhase.FAILED, None)
    assert module_start_policy("dx_modelzoo", store).allowed is True

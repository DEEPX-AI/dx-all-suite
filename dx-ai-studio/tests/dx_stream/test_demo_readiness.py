"""Demo readiness must use launch admission, without activating the runtime."""
from types import SimpleNamespace

from shared.runtime_context import RuntimeContextError
from shared.runtime_contract import ContractResult
from shared.runtime_profile import ContractCheck


def _list_demos(server):
    responses = []
    handler = object.__new__(server.DXStreamHandler)
    handler.handle_chat_routes = lambda *_: False
    handler.route_common = lambda: False
    handler.command = "GET"
    handler.url_path = "/api/demos"
    handler.send_json = lambda body: responses.append(body)
    handler.route()
    return responses[0]


def _legacy_assets_ready(monkeypatch, server):
    monkeypatch.setattr(
        server.demos, "check_demo_available",
        lambda demo_id: {"available": True, "reason": "Ready to run",
                         "reason_items": [], "demo_id": demo_id},
    )


def test_listing_rejects_missing_interpreter_even_when_legacy_assets_are_ready(monkeypatch):
    from dx_stream import server

    _legacy_assets_ready(monkeypatch, server)
    monkeypatch.setattr(server, "module_start_policy",
                        lambda *_: SimpleNamespace(allowed=True, degraded=False))
    calls = []

    def unresolved(**kwargs):
        calls.append(kwargs)
        raise RuntimeContextError("No complete active runtime interpreter")

    monkeypatch.setattr(server, "resolve_active_runtime_context", unresolved)
    entries = _list_demos(server)

    assert all(not entry["available"] for entry in entries)
    assert calls == [{"allow_unjournaled": False}]
    availability = entries[0]["availability"]
    assert availability["demo_id"] == entries[0]["id"]
    assert "profile.context" in availability["reason"]
    assert "No complete active runtime interpreter" in availability["reason"]
    assert "DX-Runtime Dependencies" in availability["reason"]
    assert availability["reason_items"][0]["code"] == "contract_failed"


def test_listing_reuses_one_context_and_the_exact_selected_demo_contract(monkeypatch):
    from dx_stream import server

    _legacy_assets_ready(monkeypatch, server)
    context = object()
    context_calls, selected_calls = [], []
    monkeypatch.setattr(server, "_active_stream_context",
                        lambda: (context_calls.append(True) or ContractResult(()), context))
    blocked = server.demos.DEMOS[0]["id"]

    def selected_contract(actual_context, demo, **directories):
        assert actual_context is context
        selected_calls.append(demo)
        assert directories["models_dir"] == server.config.MODELS_DIR
        if demo["id"] != blocked:
            return ContractResult(())
        return ContractResult((ContractCheck(
            check_id="gst.postprocess_library", required="libpostprocess.so",
            observed="missing", passed=False, remediation="Install the postprocess library in Setup.",
        ),))

    monkeypatch.setattr(server, "validate_stream_contract", selected_contract)
    entries = _list_demos(server)

    assert context_calls == [True]
    assert len(selected_calls) == len(server.demos.DEMOS)
    assert selected_calls[0]["model_file"] == server.demos._model_file(selected_calls[0]["model"])
    assert not entries[0]["available"]
    assert "gst.postprocess_library" in entries[0]["availability"]["reason"]
    assert all(entry["available"] for entry in entries[1:])
    assert all("default_video" in entry and "thumbnail" in entry for entry in entries)

    # No listing cache or admission bypass: launch must resolve the context again.
    contract, actual_context = server._stream_launch_contract(server.demos.DEMOS[0])
    assert not contract.passed and actual_context is context
    assert context_calls == [True, True]


def test_reopening_listing_rechecks_runtime_after_setup(monkeypatch):
    from dx_stream import server

    _legacy_assets_ready(monkeypatch, server)
    failure = ContractResult((ContractCheck(
        check_id="profile.context", required="active runtime", observed="missing", passed=False,
        remediation="Run Setup.",
    ),))
    contexts = iter([(failure, None), (ContractResult(()), object())])
    monkeypatch.setattr(server, "_active_stream_context", lambda: next(contexts))
    monkeypatch.setattr(server, "validate_stream_contract", lambda *_args, **_kwargs: ContractResult(()))

    assert all(not entry["available"] for entry in _list_demos(server))
    assert all(entry["available"] for entry in _list_demos(server))


def test_contract_failure_sends_observed_and_remediation_as_separate_fields(monkeypatch):
    """SR-843: the start refusal carries what was observed and what to do as separate fields.

    Joined with " — " into one detail string, neither anchored pattern in
    shared/static/server-error-i18n.js matched, so a Korean UI showed the detail in English.
    """
    import re

    from dx_stream import server
    from tests.test_server_error_i18n import TestThePatternsActuallyMatchWhatTheServerSends as P

    monkeypatch.setattr(server, "module_start_policy",
                        lambda *_: SimpleNamespace(allowed=True, degraded=False))

    def unresolved(**_kwargs):
        raise RuntimeContextError("Active runtime profile has no complete inference Python.")

    monkeypatch.setattr(server, "resolve_active_runtime_context", unresolved)
    monkeypatch.setattr(server, "_pipeline_mgr", object())
    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler._safe_read_json = lambda: {}
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)

    handler._handle_demo_start("/api/demos/0/start")

    payload = sent["payload"]
    assert sent["code"] == 424
    assert payload["error"] == "contract_failed"
    assert payload["message"] == "Runtime contract failed: profile.context"
    assert payload["detail"] == "Active runtime profile has no complete inference Python."
    assert payload["remediation"] == "Run the DX-Runtime Dependencies step in Setup, then try again."
    patterns = P._py_patterns()
    for field in ("message", "detail", "remediation"):
        assert any(p.match(payload[field]) for p in patterns), (field, payload[field])

    _legacy_assets_ready(monkeypatch, server)
    item = _list_demos(server)[0]["availability"]["reason_items"][0]
    assert item["detail"] == payload["detail"]
    assert item["remediation"] == payload["remediation"]
    assert not re.search(r" — ", item["detail"])

"""Lab experiment pipeline run-state contract tests — Tasks 4.1 & 4.2."""

import copy
import sys
import types
import pytest
from pathlib import Path

_STUDIO_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_STUDIO_DIR / "shared"))



@pytest.fixture(autouse=True)
def _clear_experiment_runs(tmp_path, monkeypatch):
    """Reset experiment run store and monkeypatch path roots for each test."""
    import lab_portal

    lab_portal._experiment_runs.clear()

    # Create fake outputs dir with .dxnn files for source validation
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "model.dxnn").write_text("fake")
    (outputs / "a.dxnn").write_text("fake")
    (outputs / "b.dxnn").write_text("fake")

    # Monkeypatch path constants so source validation works
    # monkeypatch automatically restores originals after the test
    monkeypatch.setattr(lab_portal, "SCRIPT_DIR", tmp_path)
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", tmp_path)

    yield

    lab_portal._experiment_runs.clear()



def test_start_experiment_run_returns_safe_run_id():
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code == 200
    assert res["id"].startswith("run_")
    assert res["current_step"] in {"compile", "register", "smoke", "benchmark", "package"}


def test_start_experiment_run_status_is_pending():
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code == 200
    assert res["status"] == "pending"
    assert res["current_step"] == "compile"


def test_start_experiment_run_has_required_fields():
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code == 200
    for field in ("id", "status", "current_step", "steps", "inputs", "blockers", "log_tail", "created_at", "updated_at"):
        assert field in res, f"Missing field: {field}"


def test_start_experiment_run_steps_structure():
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code == 200
    step_ids = [s["id"] for s in res["steps"]]
    assert step_ids == ["compile", "register", "smoke", "benchmark", "package"]
    # First step should be current, rest pending
    assert res["steps"][0]["status"] == "current"
    for s in res["steps"][1:]:
        assert s["status"] == "pending"



def test_start_experiment_rejects_missing_source_path():
    """Empty or absent source_path → 400 with error_code missing_source_path, no run created."""
    from lab_portal import start_experiment_run, _experiment_runs
    count_before = len(_experiment_runs)

    res_empty, code_empty = start_experiment_run({"source_path": "", "model_name": "demo"})
    assert code_empty == 400
    assert res_empty["error_code"] == "missing_source_path"

    res_missing, code_missing = start_experiment_run({})
    assert code_missing == 400
    assert res_missing["error_code"] == "missing_source_path"

    assert len(_experiment_runs) == count_before


def test_start_experiment_rejects_source_path_traversal():
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "../../etc/passwd", "model_name": "demo"})
    assert code == 400


def test_start_experiment_rejects_non_dxnn_source():
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "outputs/model.txt", "model_name": "demo"})
    assert code == 400


def test_start_experiment_rejects_missing_source_file(tmp_path):
    from lab_portal import start_experiment_run
    res, code = start_experiment_run({"source_path": "outputs/nonexistent.dxnn", "model_name": "demo"})
    assert code == 400



def test_experiment_rejects_bad_run_id():
    from lab_portal import get_experiment_run
    res, code = get_experiment_run("../bad")
    assert code == 400


def test_experiment_rejects_empty_run_id():
    from lab_portal import get_experiment_run
    res, code = get_experiment_run("")
    assert code == 400


def test_experiment_rejects_dot_in_run_id():
    from lab_portal import get_experiment_run
    res, code = get_experiment_run("run_foo.bar")
    assert code == 400


def test_experiment_unknown_safe_run_id_returns_404():
    from lab_portal import get_experiment_run
    res, code = get_experiment_run("run_nonexistent_abc123")
    assert code == 404
    assert res["error_code"] == "run_not_found"



def test_cancel_only_affects_active_run():
    from lab_portal import start_experiment_run, cancel_experiment_run, get_experiment_run
    run1, _ = start_experiment_run({"source_path": "outputs/a.dxnn", "model_name": "a"})
    run2, _ = start_experiment_run({"source_path": "outputs/b.dxnn", "model_name": "b"})
    cancel_experiment_run(run1["id"])
    assert get_experiment_run(run1["id"])[0]["status"] == "cancelled"
    assert get_experiment_run(run2["id"])[0]["status"] != "cancelled"


def test_cancel_bad_run_id_returns_400():
    from lab_portal import cancel_experiment_run
    res, code = cancel_experiment_run("../bad")
    assert code == 400


def test_cancel_unknown_safe_run_id_returns_404():
    from lab_portal import cancel_experiment_run
    res, code = cancel_experiment_run("run_nonexistent_abc123")
    assert code == 404
    assert res["error_code"] == "run_not_found"



def test_experiment_rejects_invalid_step_transition():
    from lab_portal import start_experiment_run, advance_experiment_step
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    # Skip from compile to smoke (should fail — must go compile -> register)
    res, code = advance_experiment_step(run["id"], "smoke")
    assert code == 400
    assert res["error_code"] == "invalid_step_transition"


def test_valid_step_transition_compile_to_register():
    from lab_portal import start_experiment_run, advance_experiment_step
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    res, code = advance_experiment_step(run["id"], "register")
    assert code == 200
    assert res["current_step"] == "register"


def test_advance_bad_run_id_returns_400():
    from lab_portal import advance_experiment_step
    res, code = advance_experiment_step("../bad", "register")
    assert code == 400


def test_advance_unknown_safe_run_id_returns_404():
    from lab_portal import advance_experiment_step
    res, code = advance_experiment_step("run_nonexistent_abc123", "register")
    assert code == 404
    assert res["error_code"] == "run_not_found"



def test_pipeline_stops_at_compile_failure_with_blocker():
    from lab_portal import start_experiment_run, mark_experiment_step_failed
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    res, code = mark_experiment_step_failed(run["id"], "compile", "dxcom missing")
    assert code == 200
    assert res["status"] == "failed"
    assert res["blockers"][0]["code"] == "compile_failed"


def test_mark_step_failed_bad_run_id_returns_400():
    from lab_portal import mark_experiment_step_failed
    res, code = mark_experiment_step_failed("../bad", "compile", "err")
    assert code == 400


def test_mark_step_failed_unknown_safe_run_id_returns_404():
    from lab_portal import mark_experiment_step_failed
    res, code = mark_experiment_step_failed("run_nonexistent_abc123", "compile", "err")
    assert code == 404
    assert res["error_code"] == "run_not_found"



def test_experiment_logs_are_bounded():
    from lab_portal import start_experiment_run, append_experiment_log, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    append_experiment_log(run["id"], "x" * 20000)
    current, _ = get_experiment_run(run["id"])
    assert len("\n".join(current["log_tail"])) <= 4096


def test_experiment_log_bounding_preserves_newest_evicts_oldest():
    """Many lines appended; newest lines must survive, oldest must be evicted."""
    from lab_portal import start_experiment_run, append_experiment_log, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    num_lines = 500
    for i in range(num_lines):
        append_experiment_log(run["id"], f"LINE-{i:04d}")
    current, _ = get_experiment_run(run["id"])
    joined = "\n".join(current["log_tail"])
    assert len(joined) <= 4096
    # Newest line must be present
    assert current["log_tail"][-1] == f"LINE-{num_lines - 1:04d}"
    # Oldest line must have been evicted (500 x ~9 chars + newlines > 4096)
    assert "LINE-0000" not in current["log_tail"]


def test_append_log_bad_run_id_returns_400():
    from lab_portal import append_experiment_log
    res, code = append_experiment_log("../bad", "some log")
    assert code == 400


def test_append_log_unknown_safe_run_id_returns_404():
    from lab_portal import append_experiment_log
    res, code = append_experiment_log("run_nonexistent_abc123", "some log")
    assert code == 404
    assert res["error_code"] == "run_not_found"


def test_oversized_single_log_line_preserves_truncated_entry():
    """A single log line larger than _LOG_MAX_CHARS should be truncated, not dropped."""
    from lab_portal import start_experiment_run, append_experiment_log, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    huge_line = "Z" * 20000
    append_experiment_log(run["id"], huge_line)
    current, _ = get_experiment_run(run["id"])
    # log_tail must not be empty — it should contain a truncated version
    assert len(current["log_tail"]) >= 1
    assert len(current["log_tail"][-1]) > 0
    assert len("\n".join(current["log_tail"])) <= 4096



def test_advance_cancelled_run_returns_409_and_state_unchanged():
    """Advancing a cancelled run must return 409 run_terminal; state must not change."""
    from lab_portal import start_experiment_run, cancel_experiment_run, advance_experiment_step, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    cancel_experiment_run(run["id"])

    snapshot_before, _ = get_experiment_run(run["id"])
    res, code = advance_experiment_step(run["id"], "register")
    snapshot_after, _ = get_experiment_run(run["id"])

    assert code == 409
    assert res["error_code"] == "run_terminal"
    assert snapshot_after["current_step"] == snapshot_before["current_step"]
    assert snapshot_after["steps"] == snapshot_before["steps"]


def test_advance_failed_run_returns_409_and_state_unchanged():
    """Advancing a failed run must return 409 run_terminal; state must not change."""
    from lab_portal import start_experiment_run, mark_experiment_step_failed, advance_experiment_step, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    mark_experiment_step_failed(run["id"], "compile", "broken")

    snapshot_before, _ = get_experiment_run(run["id"])
    res, code = advance_experiment_step(run["id"], "register")
    snapshot_after, _ = get_experiment_run(run["id"])

    assert code == 409
    assert res["error_code"] == "run_terminal"
    assert snapshot_after["current_step"] == snapshot_before["current_step"]
    assert snapshot_after["steps"] == snapshot_before["steps"]



def test_fail_non_current_step_returns_400_invalid_step():
    """Failing a step that is not the current step must return 400 invalid_step."""
    from lab_portal import start_experiment_run, mark_experiment_step_failed, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    # current_step is "compile"; trying to fail "benchmark" must be rejected
    snapshot_before, _ = get_experiment_run(run["id"])
    res, code = mark_experiment_step_failed(run["id"], "benchmark", "shouldn't work")
    snapshot_after, _ = get_experiment_run(run["id"])

    assert code == 400
    assert res["error_code"] == "invalid_step"
    assert snapshot_after["status"] == snapshot_before["status"]
    assert snapshot_after["current_step"] == snapshot_before["current_step"]



def test_double_fail_current_step_rejected_no_duplicate_blockers():
    """Second failure of the same step must be rejected (409); blockers must not duplicate."""
    from lab_portal import start_experiment_run, mark_experiment_step_failed, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    mark_experiment_step_failed(run["id"], "compile", "first failure")

    res, code = mark_experiment_step_failed(run["id"], "compile", "second failure")
    assert code == 409
    assert res["error_code"] == "run_terminal"

    final, _ = get_experiment_run(run["id"])
    compile_blockers = [b for b in final["blockers"] if b["code"] == "compile_failed"]
    assert len(compile_blockers) == 1



def test_cancel_failed_run_returns_409_and_preserves_state():
    """Cancelling a failed run must return 409 run_terminal; status and blockers unchanged."""
    from lab_portal import start_experiment_run, mark_experiment_step_failed, cancel_experiment_run, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    mark_experiment_step_failed(run["id"], "compile", "dxcom missing")

    snapshot_before, _ = get_experiment_run(run["id"])
    res, code = cancel_experiment_run(run["id"])
    snapshot_after, _ = get_experiment_run(run["id"])

    assert code == 409
    assert res["error_code"] == "run_terminal"
    assert snapshot_after["status"] == "failed"
    assert snapshot_after["blockers"] == snapshot_before["blockers"]


def test_cancel_already_cancelled_run_returns_409_and_state_unchanged():
    """Cancelling an already-cancelled run must return 409 run_terminal; no state change."""
    from lab_portal import start_experiment_run, cancel_experiment_run, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    cancel_experiment_run(run["id"])

    snapshot_before, _ = get_experiment_run(run["id"])
    res, code = cancel_experiment_run(run["id"])
    snapshot_after, _ = get_experiment_run(run["id"])

    assert code == 409
    assert res["error_code"] == "run_terminal"
    assert snapshot_after["status"] == "cancelled"
    assert snapshot_after["updated_at"] == snapshot_before["updated_at"]



def test_log_trimming_many_lines_preserves_newest_and_bounded():
    """Appending many short lines: newest preserved, total ≤ 4096, oldest evicted."""
    from lab_portal import start_experiment_run, append_experiment_log, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    # Append 1000 short lines to stress log trimming
    for i in range(1000):
        append_experiment_log(run["id"], f"L{i:05d}")
    current, _ = get_experiment_run(run["id"])
    joined = "\n".join(current["log_tail"])
    assert len(joined) <= 4096
    # Newest line must be present
    assert current["log_tail"][-1] == "L00999"
    # Oldest line must have been evicted
    assert "L00000" not in current["log_tail"]
    # Verify all remaining lines are contiguous and in order
    indices = [int(line[1:]) for line in current["log_tail"]]
    assert indices == sorted(indices)
    assert indices[-1] == 999



def test_get_experiment_run_returns_copy_not_reference():
    from lab_portal import start_experiment_run, get_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    fetched, _ = get_experiment_run(run["id"])
    fetched["status"] = "MUTATED"
    fetched["blockers"].append({"code": "injected"})
    original, _ = get_experiment_run(run["id"])
    assert original["status"] != "MUTATED"
    assert not any(b.get("code") == "injected" for b in original["blockers"])



def _make_handler(method, path, headers=None, body=None, server_obj=None):
    """Build a minimal mock Handler for route testing."""
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = method
    handler.url_path = path
    handler.query = {}
    handler.headers = headers or {}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: (body or {})
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    if server_obj:
        handler.server = server_obj
    return handler, captured



def test_experiment_start_route_valid_returns_run_id():
    """Valid start request returns 200 with run id starting 'run_'."""
    from developer import lab_session
    tok = lab_session()["token"]
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/start",
        headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
        body={"source_path": "outputs/model.dxnn", "model_name": "demo"},
    )
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["id"].startswith("run_")


def test_experiment_start_route_invalid_token_returns_403_no_status():
    """Invalid token on start returns 403, body has 'error' but no 'status' key."""
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/start",
        headers={"X-Lab-Token": "bad_token", "Origin": "http://localhost:8080"},
        body={"source_path": "outputs/model.dxnn", "model_name": "demo"},
    )
    handler.route()
    assert captured["code"] == 403
    assert "error" in captured["data"]
    assert "status" not in captured["data"]


def test_experiment_start_route_missing_token_returns_403():
    """Missing token on start returns 403."""
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/start",
        headers={"Origin": "http://localhost:8080"},
        body={"source_path": "outputs/model.dxnn", "model_name": "demo"},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_start_rejects_hostile_origin():
    """Hostile Origin on start returns 403."""
    from developer import lab_session
    tok = lab_session()["token"]
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/start",
        headers={"X-Lab-Token": tok, "Origin": "https://evil.example.com"},
        body={"source_path": "outputs/model.dxnn", "model_name": "demo"},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_start_does_not_accept_dev_token():
    """X-Dev-Token must NOT be accepted as alias for experiment routes."""
    from developer import lab_session
    tok = lab_session()["token"]
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/start",
        headers={"X-Dev-Token": tok, "Origin": "http://localhost:8080"},
        body={"source_path": "outputs/model.dxnn", "model_name": "demo"},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_start_rejects_duplicate_active_source():
    """Second start for same active source_path returns 409 run_in_progress."""
    from developer import lab_session
    tok = lab_session()["token"]

    def post_start(source_path):
        h, c = _make_handler(
            "POST", "/api/lab/experiment/start",
            headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
            body={"source_path": source_path, "model_name": "demo"},
        )
        h.route()
        return c

    first = post_start("outputs/model.dxnn")
    second = post_start("outputs/model.dxnn")
    assert first["code"] == 200
    assert second["code"] == 409
    assert second["data"]["error_code"] == "run_in_progress"


def test_experiment_start_allows_same_source_after_cancel():
    """Cancelled run should not block a new start for same source."""
    from developer import lab_session
    import lab_portal
    tok = lab_session()["token"]

    def post_start(source_path):
        h, c = _make_handler(
            "POST", "/api/lab/experiment/start",
            headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
            body={"source_path": source_path, "model_name": "demo"},
        )
        h.route()
        return c

    first = post_start("outputs/model.dxnn")
    assert first["code"] == 200
    lab_portal.cancel_experiment_run(first["data"]["id"])

    second = post_start("outputs/model.dxnn")
    assert second["code"] == 200



def test_experiment_get_route_valid_returns_run_state():
    """GET with valid token returns the run state."""
    from developer import lab_session
    from lab_portal import start_experiment_run
    tok = lab_session()["token"]
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "GET", f"/api/lab/experiment/{run['id']}",
        headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
    )
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["id"] == run["id"]
    assert captured["data"]["status"] == "pending"


def test_experiment_get_route_missing_token_returns_403():
    """GET without token returns 403."""
    from lab_portal import start_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "GET", f"/api/lab/experiment/{run['id']}",
        headers={"Origin": "http://localhost:8080"},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_get_route_invalid_token_returns_403():
    """GET with bad token returns 403."""
    from lab_portal import start_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "GET", f"/api/lab/experiment/{run['id']}",
        headers={"X-Lab-Token": "bad_token", "Origin": "http://localhost:8080"},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_get_route_hostile_origin_returns_403():
    """GET from hostile origin returns 403."""
    from developer import lab_session
    from lab_portal import start_experiment_run
    tok = lab_session()["token"]
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "GET", f"/api/lab/experiment/{run['id']}",
        headers={"X-Lab-Token": tok, "Origin": "https://evil.example.com"},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_get_route_unsafe_id_returns_400():
    """GET with unsafe run ID (dotted / traversal) returns 400."""
    from developer import lab_session
    tok = lab_session()["token"]
    for bad_id in ["../bad", "run_foo.bar", "", "../../etc/passwd"]:
        handler, captured = _make_handler(
            "GET", f"/api/lab/experiment/{bad_id}",
            headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
        )
        handler.route()
        assert captured["code"] == 400, f"Expected 400 for id={bad_id!r}, got {captured['code']}"


def test_experiment_get_route_checks_origin_before_run_id_validation():
    """Hostile origin must be rejected before exposing run-id validation."""
    handler, captured = _make_handler(
        "GET", "/api/lab/experiment/../bad",
        headers={"Origin": "https://evil.example.com"},
    )
    handler.route()
    assert captured["code"] == 403
    assert captured["data"].get("error_code") != "invalid_run_id"


def test_experiment_get_route_checks_token_before_run_id_validation():
    """Missing token must be rejected before exposing run-id validation."""
    handler, captured = _make_handler(
        "GET", "/api/lab/experiment/../bad",
        headers={"Origin": "http://localhost:8080"},
    )
    handler.route()
    assert captured["code"] == 403
    assert captured["data"].get("error_code") != "invalid_run_id"



def test_experiment_cancel_route_valid_changes_state():
    """Cancel via route changes run state to 'cancelled'."""
    from developer import lab_session
    from lab_portal import start_experiment_run, get_experiment_run
    tok = lab_session()["token"]
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "POST", f"/api/lab/experiment/{run['id']}/cancel",
        headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
        body={},
    )
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["status"] == "cancelled"
    state, _ = get_experiment_run(run["id"])
    assert state["status"] == "cancelled"


def test_experiment_cancel_route_invalid_token_returns_403():
    """Cancel with bad token returns 403."""
    from lab_portal import start_experiment_run
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "POST", f"/api/lab/experiment/{run['id']}/cancel",
        headers={"X-Lab-Token": "bad_token", "Origin": "http://localhost:8080"},
        body={},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_cancel_route_hostile_origin_returns_403():
    """Cancel from hostile origin returns 403."""
    from developer import lab_session
    from lab_portal import start_experiment_run
    tok = lab_session()["token"]
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    handler, captured = _make_handler(
        "POST", f"/api/lab/experiment/{run['id']}/cancel",
        headers={"X-Lab-Token": tok, "Origin": "https://evil.example.com"},
        body={},
    )
    handler.route()
    assert captured["code"] == 403


def test_experiment_cancel_route_unsafe_id_returns_400():
    """Cancel with unsafe run ID returns 400."""
    from developer import lab_session
    tok = lab_session()["token"]
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/../bad/cancel",
        headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
        body={},
    )
    handler.route()
    assert captured["code"] == 400


def test_experiment_cancel_route_unknown_safe_id_returns_404():
    """Cancel unknown but safe run ID returns 404 run_not_found."""
    from developer import lab_session
    tok = lab_session()["token"]
    handler, captured = _make_handler(
        "POST", "/api/lab/experiment/run_nonexistent_abc123/cancel",
        headers={"X-Lab-Token": tok, "Origin": "http://localhost:8080"},
        body={},
    )
    handler.route()
    assert captured["code"] == 404
    assert captured["data"]["error_code"] == "run_not_found"



def test_active_run_for_source_returns_none_when_no_active():
    """No active run → helper returns None."""
    from lab_portal import active_experiment_run_for_source
    assert active_experiment_run_for_source("outputs/model.dxnn") is None


def test_active_run_for_source_returns_id_when_active():
    """Active run → helper returns run id."""
    from lab_portal import start_experiment_run, active_experiment_run_for_source
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert active_experiment_run_for_source("outputs/model.dxnn") == run["id"]


def test_active_run_for_source_ignores_terminal():
    """Terminal runs (cancelled/failed/completed) are not considered active."""
    from lab_portal import start_experiment_run, cancel_experiment_run, active_experiment_run_for_source
    run, _ = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    cancel_experiment_run(run["id"])
    assert active_experiment_run_for_source("outputs/model.dxnn") is None



def test_start_experiment_run_rejects_duplicate_active_source():
    """Calling start_experiment_run twice with same active source_path returns 409."""
    from lab_portal import start_experiment_run
    first, code1 = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code1 == 200
    second, code2 = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code2 == 409
    assert second["error_code"] == "run_in_progress"


def test_start_experiment_run_allows_same_source_after_cancel():
    """After cancelling a run, same source_path can start a new run."""
    from lab_portal import start_experiment_run, cancel_experiment_run
    first, code1 = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code1 == 200
    cancel_experiment_run(first["id"])
    second, code2 = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code2 == 200


def test_start_experiment_run_allows_same_source_after_failure():
    """After a run fails, same source_path can start a new run."""
    from lab_portal import start_experiment_run, mark_experiment_step_failed
    first, code1 = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code1 == 200
    mark_experiment_step_failed(first["id"], "compile", "build error")
    second, code2 = start_experiment_run({"source_path": "outputs/model.dxnn", "model_name": "demo"})
    assert code2 == 200

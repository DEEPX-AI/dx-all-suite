"""DX Cloud compile — core logic against stubbed AWS (botocore Stubber, no network).

The flow under test is the DEEPX Compiler Solution stack's: upload <model>.onnx and <model>.json
to the same prefix of the stack's ModelBucketName, a Lambda starts the Step Functions workflow,
and <model>.dxnn shows up under that prefix.
"""
from __future__ import annotations

import datetime
import io
import json
import sys

import boto3
import pytest
from botocore.response import StreamingBody
from botocore.stub import ANY, Stubber

from dx_edge.core import aws_compile as ac

ORIGINAL_CLIENT = ac._client

REGION = "ap-northeast-2"
STACK = "dx-compiler-stack"
BUCKET = "dx-models-bucket-123"
SM_ARN = f"arn:aws:states:{REGION}:111122223333:stateMachine:dx-compile"
EXEC_ARN = f"arn:aws:states:{REGION}:111122223333:execution:dx-compile:abc123"
NOW = datetime.datetime(2026, 10, 14, 9, 30, 0)
PREFIX = "models/yolov5s-20261014-093000/"
FAKE_KEY_ID = "AKIAFAKEFAKEFAKE0000"
FAKE_SECRET = "fakeSecretKeyThatMustNeverLeak0000000000"


def _stack(name=STACK, status="CREATE_COMPLETE", outputs=None):
    if outputs is None:
        outputs = [
            {"OutputKey": "ModelBucketName", "OutputValue": BUCKET},
            {"OutputKey": "StateMachineArn", "OutputValue": SM_ARN},
        ]
    return {
        "StackName": name,
        "StackStatus": status,
        "CreationTime": NOW,
        "Outputs": outputs,
    }


@pytest.fixture()
def aws(monkeypatch, tmp_path):
    """Real boto3 clients with fake keys, each wrapped in a Stubber; ac._client hands them out."""
    # Never read the developer's ~/.aws
    cfg = tmp_path / "config"
    cfg.write_text("[default]\nregion = us-east-1\n[profile dev]\nregion = ap-northeast-2\n")
    creds = tmp_path / "credentials"
    creds.write_text("")
    monkeypatch.setenv("AWS_CONFIG_FILE", str(cfg))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(creds))
    for var in ("AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.delenv(var, raising=False)

    clients = {
        svc: boto3.client(
            svc,
            region_name=REGION,
            aws_access_key_id=FAKE_KEY_ID,
            aws_secret_access_key=FAKE_SECRET,
        )
        for svc in ("cloudformation", "s3", "stepfunctions", "sts", "ec2", "logs")
    }
    stubs = {svc: Stubber(c) for svc, c in clients.items()}
    calls = []

    def fake_client(service, profile, region):
        calls.append((service, profile, region))
        return clients[service]

    monkeypatch.setattr(ac, "_client", fake_client)
    for s in stubs.values():
        s.activate()
    yield stubs, calls
    for s in stubs.values():
        s.assert_no_pending_responses()
        s.deactivate()


def _describe(stubs, stack=STACK, outputs=None):
    stubs["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [_stack(stack, outputs=outputs)]},
        {"StackName": stack},
    )


# ── status / missing boto3 ──────────────────────────────────────────────────

def test_status_lists_profiles_and_default_region(aws):
    st = ac.status()
    assert st["boto3"] is True
    assert st["default_region"] == "us-east-1"  # the default profile's region in the fixture config
    assert set(st["profiles"]) == {"default", "dev"}


def test_missing_boto3_is_a_clear_error_with_an_install_hint(monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)
    st = ac.status()
    assert st["boto3"] is False
    assert st["profiles"] == []
    assert "pip install" in st["install_hint"]
    with pytest.raises(ac.AwsError) as exc:
        ac.list_stacks("", REGION)
    assert exc.value.status == 503
    assert "boto3" in exc.value.message


# ── identity (Check connection) ─────────────────────────────────────────────

def test_identity_returns_account_and_arn_without_the_user_id(aws):
    stubs, calls = aws
    stubs["sts"].add_response("get_caller_identity", {
        "UserId": "AIDAFAKEUSERID000000", "Account": "111122223333",
        "Arn": "arn:aws:iam::111122223333:user/dev"}, {})
    assert ac.identity("dev", REGION) == {"account": "111122223333", "arn": "arn:aws:iam::111122223333:user/dev"}
    assert calls == [("sts", "dev", REGION)]


def test_identity_without_credentials_is_401(aws, monkeypatch):
    from botocore.exceptions import NoCredentialsError

    class NoCreds:
        def get_caller_identity(self):
            raise NoCredentialsError()

    monkeypatch.setattr(ac, "_client", lambda *a: NoCreds())
    with pytest.raises(ac.AwsError) as exc:
        ac.identity("", REGION)
    assert exc.value.status == 401
    assert "aws configure" in exc.value.message


def test_identity_unknown_profile_is_400(aws):
    with pytest.raises(ac.AwsError) as exc:
        ac.identity("nope", REGION)
    assert exc.value.status == 400


# ── regions (Region picker) ─────────────────────────────────────────────────

def test_regions_are_the_accounts_enabled_regions_with_names(aws):
    stubs, calls = aws
    stubs["ec2"].add_response("describe_regions", {"Regions": [
        {"RegionName": "us-east-1"}, {"RegionName": "ap-northeast-2"}, {"RegionName": "xx-test-9"}]}, {})
    out = ac.regions("dev")
    assert out["regions"] == [
        {"code": "ap-northeast-2", "name": "Asia Pacific (Seoul)"},
        {"code": "us-east-1", "name": "US East (N. Virginia)"},
        {"code": "xx-test-9", "name": ""},
    ]
    assert out["source"] == "account"
    assert calls == [("ec2", "dev", ac.DEFAULT_REGION)]


def test_regions_fall_back_to_the_known_list_when_aws_cannot_answer(aws):
    stubs, _ = aws
    stubs["ec2"].add_client_error("describe_regions", "UnauthorizedOperation", "no")
    out = ac.regions("")
    assert out["source"] == "builtin"
    codes = [r["code"] for r in out["regions"]]
    assert "ap-northeast-2" in codes and "us-east-1" in codes and codes == sorted(codes)


def test_status_default_region_follows_the_profile_config(aws):
    # the fixture's ~/.aws/config: default → us-east-1, profile dev → ap-northeast-2
    assert ac.status()["default_region"] == "us-east-1"
    assert ac.status("dev")["default_region"] == "ap-northeast-2"

# ── stack discovery ─────────────────────────────────────────────────────────

def test_list_stacks_keeps_only_complete_stacks_with_a_model_bucket(aws):
    stubs, _ = aws
    stubs["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [
            _stack("good"),
            _stack("updated", status="UPDATE_COMPLETE"),
            _stack("rolling", status="ROLLBACK_COMPLETE"),
            _stack("other", outputs=[{"OutputKey": "Foo", "OutputValue": "x"}]),
            _stack("no-outputs", outputs=[]),
        ]},
        {},
    )
    stacks = ac.list_stacks("", REGION)
    assert [s["name"] for s in stacks] == ["good", "updated"]
    assert stacks[0]["bucket"] == BUCKET
    assert stacks[0]["state_machine"] is True


def test_profile_must_be_a_configured_profile(aws):
    with pytest.raises(ac.AwsError) as exc:
        ac.list_stacks("nope", REGION)
    assert exc.value.status == 400


@pytest.mark.parametrize("env_profile", ["", "gone"])
def test_a_bad_aws_profile_env_var_is_a_client_error_not_a_crash(aws, monkeypatch, env_profile):
    # boto3 raises ProfileNotFound while building the Session itself when AWS_PROFILE is
    # empty or names a missing profile — that happens before any API call, on a real shell.
    monkeypatch.setattr(ac, "_client", ORIGINAL_CLIENT)
    monkeypatch.setenv("AWS_PROFILE", env_profile)
    st = ac.status()
    assert st["boto3"] is True
    assert "AWS_PROFILE" in st["error"]
    with pytest.raises(ac.AwsError) as exc:
        ac.list_stacks("", REGION)
    assert exc.value.status == 400
    assert "AWS_PROFILE" in exc.value.message


@pytest.mark.parametrize("region", ["", "ap-northeast-2; rm", "../x", "AP-NORTHEAST-2"])
def test_region_is_validated(aws, region):
    with pytest.raises(ac.AwsError):
        ac.list_stacks("", region)


# ── compile start ───────────────────────────────────────────────────────────

def _start(**over):
    args = dict(
        profile="dev", region=REGION, stack=STACK,
        onnx_name="yolov5s.onnx", onnx_data=b"onnx-bytes",
        json_name="yolov5s.json", json_data=b'{"inputs": {"images": [1, 3, 640, 640]}}',
        now=NOW,
    )
    args.update(over)
    return ac.start_compile(**args)


def test_start_resolves_the_bucket_from_the_stack_and_uploads_both_files_to_one_prefix(aws):
    stubs, calls = aws
    _describe(stubs)
    stubs["s3"].add_response(
        "put_object", {}, {"Bucket": BUCKET, "Key": PREFIX + "yolov5s.onnx", "Body": ANY})
    stubs["s3"].add_response(
        "put_object", {}, {"Bucket": BUCKET, "Key": PREFIX + "yolov5s.json", "Body": ANY})
    job = _start()
    assert job["prefix"] == PREFIX
    assert job["stack"] == STACK
    assert all(c[1:] == ("dev", REGION) for c in calls)


def test_start_ignores_any_bucket_the_client_sends(aws):
    """There is no bucket parameter at all — the bucket only ever comes from the stack outputs."""
    with pytest.raises(TypeError):
        _start(bucket="attacker-bucket")


def test_start_stem_is_sanitised(aws):
    """The stem goes into both the prefix and the file names the trigger pairs up."""
    stubs, _ = aws
    _describe(stubs)
    prefix = "models/my_model_v2-20261014-093000/"
    stubs["s3"].add_response("put_object", {}, {"Bucket": BUCKET, "Key": prefix + "my_model_v2.onnx", "Body": ANY})
    stubs["s3"].add_response("put_object", {}, {"Bucket": BUCKET, "Key": prefix + "my_model_v2.json", "Body": ANY})
    job = _start(onnx_name="../../my model v2.onnx")
    assert job["prefix"] == prefix


@pytest.mark.parametrize("over", [
    {"onnx_name": "model.pt"},
    {"json_name": "config.yaml"},
    {"json_data": b"{not json"},
    {"json_data": b"[1, 2]"},
    {"onnx_data": b""},
    {"stack": "bad stack;name"},
])
def test_start_rejects_bad_input_before_touching_aws(aws, over):
    with pytest.raises(ac.AwsError) as exc:
        _start(**over)
    assert exc.value.status == 400


def test_start_rejects_oversized_onnx(aws, monkeypatch):
    monkeypatch.setattr(ac, "MAX_ONNX_BYTES", 4)
    with pytest.raises(ac.AwsError) as exc:
        _start()
    assert exc.value.status == 413


def test_start_fails_when_the_stack_has_no_model_bucket(aws):
    stubs, _ = aws
    _describe(stubs, outputs=[{"OutputKey": "Foo", "OutputValue": "x"}])
    with pytest.raises(ac.AwsError) as exc:
        _start()
    assert exc.value.status == 400


def test_aws_errors_become_aws_error(aws):
    stubs, _ = aws
    stubs["cloudformation"].add_client_error(
        "describe_stacks", service_error_code="ValidationError",
        service_message="Stack with id x does not exist", http_status_code=400)
    with pytest.raises(ac.AwsError) as exc:
        _start()
    assert "does not exist" in exc.value.message


# ── prefix validation ───────────────────────────────────────────────────────

@pytest.mark.parametrize("prefix", [
    "", "models/", "other/x/", "models/../secret/", "models/a/../b/", "/models/x/",
    "models/x/y/", "models/x y/", "models/x\\y/", "models/..", "models/x;rm/",
    "models/.hidden-20261014-093000/", "models/-x/",
])
def test_bad_prefixes_are_rejected(prefix):
    with pytest.raises(ac.AwsError) as exc:
        ac.validate_prefix(prefix)
    assert exc.value.status == 400


@pytest.mark.parametrize("prefix", [PREFIX, PREFIX.rstrip("/")])
def test_good_prefix_is_normalised(prefix):
    assert ac.validate_prefix(prefix) == PREFIX


@pytest.mark.parametrize("prefix", ["models/yolov5s/", "models/yolov5s", "models/my_model-v2.1/"])
def test_a_folder_made_in_the_s3_console_is_a_job_too(prefix):
    assert ac.validate_prefix(prefix) == prefix.rstrip("/") + "/"


def test_status_rejects_traversal_without_calling_aws(aws):
    with pytest.raises(ac.AwsError):
        ac.compile_status("dev", REGION, STACK, "models/../../etc/")


# ── status transitions ──────────────────────────────────────────────────────

def _list(stubs, keys):
    stubs["s3"].add_response(
        "list_objects_v2",
        {"Contents": [{"Key": k, "Size": 1} for k in keys], "KeyCount": len(keys)},
        {"Bucket": BUCKET, "Prefix": PREFIX},
    )


# The real trigger names a run dx-compile-<onnx stem>-<12 hex> (verified on a live stack).
STARTED = NOW.astimezone() + datetime.timedelta(seconds=20)


def _run(name, status, start=STARTED, arn=EXEC_ARN):
    return {"executionArn": arn, "stateMachineArn": SM_ARN, "name": name,
            "status": status, "startDate": start}


def _executions(stubs, status=None, runs=None):
    if runs is None:
        runs = [] if status is None else [_run("dx-compile-yolov5s-81e638714de2", status)]
    stubs["stepfunctions"].add_response(
        "list_executions", {"executions": runs}, {"stateMachineArn": SM_ARN, "maxResults": ANY})


def test_status_pending_when_nothing_started_yet(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx", PREFIX + "yolov5s.json"])
    _executions(stubs, None)
    st = ac.compile_status("dev", REGION, STACK, PREFIX)
    assert st["state"] == "pending"
    assert st["execution"] is None


def test_status_running_while_the_execution_runs(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx", PREFIX + "yolov5s.json"])
    _executions(stubs, "RUNNING")
    st = ac.compile_status("dev", REGION, STACK, PREFIX)
    assert st["state"] == "running"
    assert st["execution"]["arn"] == EXEC_ARN
    assert EXEC_ARN in st["links"]["execution"]


def test_status_ignores_other_models_and_runs_older_than_the_upload(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx", PREFIX + "yolov5s.json"])
    other = f"arn:aws:states:{REGION}:111122223333:execution:dx-compile:other"
    _executions(stubs, runs=[
        _run("dx-compile-resnet50-0123456789ab", "RUNNING", arn=other),
        _run("dx-compile-yolov5s-0123456789ab", "FAILED", start=STARTED - datetime.timedelta(hours=1), arn=other),
        _run("dx-compile-yolov5s_v2-0123456789ab", "RUNNING", arn=other),
    ])
    st = ac.compile_status("dev", REGION, STACK, PREFIX)
    assert st["state"] == "pending"


def test_status_failed_when_the_execution_failed(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx", PREFIX + "yolov5s.json"])
    _executions(stubs, "FAILED")
    assert ac.compile_status("dev", REGION, STACK, PREFIX)["state"] == "failed"


def test_status_succeeded_once_the_dxnn_exists(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx", PREFIX + "yolov5s.json", PREFIX + "yolov5s.dxnn"])
    st = ac.compile_status("dev", REGION, STACK, PREFIX)
    assert st["state"] == "succeeded"
    assert st["dxnn"] == "yolov5s.dxnn"
    links = st["links"]
    assert "/dx-compiler/" + STACK + "/execution" in links["log_group_name"]
    assert "cloudwatch" in links["logs"] and REGION in links["logs"]
    assert BUCKET in links["s3"] and "prefix=" in links["s3"]
    assert "states" in links["state_machine"]


def test_status_without_a_state_machine_output_skips_step_functions(aws):
    stubs, _ = aws
    _describe(stubs, outputs=[{"OutputKey": "ModelBucketName", "OutputValue": BUCKET}])
    _list(stubs, [PREFIX + "yolov5s.onnx"])
    st = ac.compile_status("dev", REGION, STACK, PREFIX)
    assert st["state"] == "pending"
    assert "state_machine" not in st["links"]


# ── download / save ─────────────────────────────────────────────────────────

def _get_dxnn(stubs, body=b"DXNN-BINARY"):
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx", PREFIX + "yolov5s.dxnn"])
    stubs["s3"].add_response(
        "get_object",
        {"Body": StreamingBody(io.BytesIO(body), len(body)), "ContentLength": len(body)},
        {"Bucket": BUCKET, "Key": PREFIX + "yolov5s.dxnn"},
    )


def test_open_dxnn_streams_name_size_and_chunks(aws):
    stubs, _ = aws
    _get_dxnn(stubs)
    name, size, body = ac.open_dxnn("dev", REGION, STACK, PREFIX)
    assert (name, size) == ("yolov5s.dxnn", len(b"DXNN-BINARY"))
    assert b"".join(ac.iter_body(body)) == b"DXNN-BINARY"


def test_open_dxnn_before_it_exists_is_404(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.onnx"])
    with pytest.raises(ac.AwsError) as exc:
        ac.open_dxnn("dev", REGION, STACK, PREFIX)
    assert exc.value.status == 404


def test_save_dxnn_writes_into_the_models_dir(aws, tmp_path):
    stubs, _ = aws
    _get_dxnn(stubs)
    out = ac.save_dxnn("dev", REGION, STACK, PREFIX, tmp_path / "models")
    assert out == tmp_path / "models" / "yolov5s.dxnn"
    assert out.read_bytes() == b"DXNN-BINARY"
    assert [p.name for p in out.parent.iterdir()] == ["yolov5s.dxnn"]  # no temp file left


def test_saved_dxnn_is_readable_like_any_other_model(aws, tmp_path):
    # mkstemp creates 0600; a runtime running as another user (Docker) must still read it.
    stubs, _ = aws
    _get_dxnn(stubs)
    out = ac.save_dxnn("dev", REGION, STACK, PREFIX, tmp_path / "models")
    assert out.stat().st_mode & 0o777 == 0o644


# ── no credential leakage ───────────────────────────────────────────────────

def test_nothing_returned_carries_credentials(aws):
    stubs, _ = aws
    _describe(stubs)
    _list(stubs, [PREFIX + "yolov5s.dxnn"])
    blob = json.dumps([ac.status(), ac.compile_status("dev", REGION, STACK, PREFIX)])
    assert FAKE_KEY_ID not in blob and FAKE_SECRET not in blob
    assert "aws_access_key_id" not in blob.lower() and "secret" not in blob.lower()


def test_no_credentials_error_message_has_no_secret(monkeypatch, aws):
    from botocore.exceptions import NoCredentialsError

    def boom(service, profile, region):
        raise NoCredentialsError()

    monkeypatch.setattr(ac, "_client", boom)
    with pytest.raises(ac.AwsError) as exc:
        ac.list_stacks("", REGION)
    assert exc.value.status == 401
    assert "credentials" in exc.value.message.lower()


# ── compile log (workflow steps + dxcom output) ─────────────────────────────

LOG_GROUP = f"/dx-compiler/{STACK}/execution"
INSTANCE = "i-0123456789abcdef0"
COMMAND = "c60b347d-fb00-4f76-b824-7a12833c6f06"


def _ev(i, typ, sec, **details):
    return {"id": i, "type": typ, "timestamp": NOW + datetime.timedelta(seconds=60 + sec), **details}


def _history(stubs, events):
    stubs["stepfunctions"].add_response("get_execution_history", {"events": events},
                                        {"executionArn": EXEC_ARN, "maxResults": ANY})


def _stream(stubs, kind, events):
    stubs["logs"].add_response(
        "get_log_events", {"events": events, "nextForwardToken": "f/1", "nextBackwardToken": "b/1"},
        {"logGroupName": LOG_GROUP, "logStreamName": f"{COMMAND}/{INSTANCE}/CompileModel/{kind}",
         "startFromHead": True, "limit": ANY})
    stubs["logs"].add_response(
        "get_log_events", {"events": [], "nextForwardToken": "f/1", "nextBackwardToken": "b/1"},
        {"logGroupName": LOG_GROUP, "logStreamName": f"{COMMAND}/{INSTANCE}/CompileModel/{kind}",
         "startFromHead": True, "limit": ANY, "nextToken": "f/1"})


def _entered(i, name, sec):
    return _ev(i, "TaskStateEntered", sec, stateEnteredEventDetails={"name": name})


def test_compile_log_has_the_workflow_steps_and_the_dxcom_output(aws):
    stubs, _ = aws
    _describe(stubs, outputs=[{"OutputKey": "ModelBucketName", "OutputValue": BUCKET},
                              {"OutputKey": "StateMachineArn", "OutputValue": SM_ARN},
                              {"OutputKey": "CompilerExecutionLogGroupName", "OutputValue": LOG_GROUP}])
    _executions(stubs, "RUNNING")
    _history(stubs, [
        _ev(1, "ExecutionStarted", 0, executionStartedEventDetails={"input": "{}"}),
        _entered(2, "StartEC2Instance", 0),
        _ev(3, "TaskSucceeded", 2, taskSucceededEventDetails={
            "resourceType": "aws-sdk:ec2", "resource": "runInstances",
            "output": json.dumps({"Instances": [{"InstanceId": INSTANCE}]})}),
        _entered(4, "RunCompilationCommand", 62),
        _ev(5, "TaskSucceeded", 62, taskSucceededEventDetails={
            "resourceType": "aws-sdk:ssm", "resource": "sendCommand",
            "output": json.dumps({"Command": {"CommandId": COMMAND}})}),
        _entered(6, "CheckCommandStatus", 92),
        _entered(7, "CheckCommandStatus", 122),
        _entered(8, "CheckCommandStatus", 152),
    ])
    ms = int((NOW + datetime.timedelta(seconds=100)).timestamp() * 1000)
    _stream(stubs, "stdout", [{"timestamp": ms, "message": "Compiling...\nlayer 1/3"},
                              {"timestamp": ms + 2000, "message": "done"}])
    _stream(stubs, "stderr", [{"timestamp": ms + 1000, "message": "WARN calib"}])

    log = ac.compile_log("dev", REGION, STACK, PREFIX)
    assert log["instance_id"] == INSTANCE and log["command_id"] == COMMAND
    assert [s["name"] for s in log["steps"]] == ["ExecutionStarted", "StartEC2Instance",
                                                 "RunCompilationCommand", "CheckCommandStatus"]
    assert log["steps"][-1]["count"] == 3  # the 30-second poll loop is one row
    assert [(l["stream"], l["text"]) for l in log["lines"]] == [
        ("stdout", "Compiling..."), ("stdout", "layer 1/3"), ("stderr", "WARN calib"), ("stdout", "done")]


def test_compile_log_before_the_workflow_starts_is_empty(aws):
    stubs, _ = aws
    _describe(stubs)
    _executions(stubs, None)
    log = ac.compile_log("dev", REGION, STACK, PREFIX)
    assert log == {"execution": None, "steps": [], "lines": [], "instance_id": None, "command_id": None}


def test_compile_log_reports_a_failed_task_cause(aws):
    stubs, _ = aws
    _describe(stubs)
    _executions(stubs, "FAILED")
    _history(stubs, [
        _entered(1, "StartEC2Instance", 0),
        _ev(2, "TaskFailed", 1, taskFailedEventDetails={"resourceType": "aws-sdk:ec2", "resource": "runInstances",
                                                       "error": "EC2.InsufficientInstanceCapacity",
                                                       "cause": "No capacity"}),
        _ev(3, "ExecutionFailed", 2, executionFailedEventDetails={"error": "States.TaskFailed"}),
    ])
    log = ac.compile_log("dev", REGION, STACK, PREFIX)
    failed = [s for s in log["steps"] if s["status"] == "failed"]
    assert failed and "No capacity" in failed[0]["detail"]
    assert log["lines"] == []


def test_compile_log_rejects_a_bad_prefix(aws):
    with pytest.raises(ac.AwsError) as exc:
        ac.compile_log("dev", REGION, STACK, "../etc/")
    assert exc.value.status == 400


def test_compile_log_keeps_one_row_for_the_poll_loop_and_hides_its_inner_states():
    t = NOW
    events = [{"id": i, "type": "TaskStateEntered" if n == "CheckCommandStatus" else
               ("WaitStateEntered" if n == "WaitForCompletion" else "ChoiceStateEntered"),
               "timestamp": t, "stateEnteredEventDetails": {"name": n}}
              for i, n in enumerate(["WaitForCompletion", "CheckCommandStatus", "EvaluateCommandResult"] * 3)]
    steps = ac._history_steps(events)[0]
    assert [(s["name"], s["count"]) for s in steps] == [("CheckCommandStatus", 3)]


def test_compile_log_strips_terminal_codes_and_keeps_only_the_latest_progress_bar():
    raw = [
        {"ts": 1, "stream": "stdout", "text": "DX-COM 2.3.0"},
        {"ts": 2, "stream": "stdout", "text": "Calibration:  57%|█████▋    | 57/100 [02:44<02:07]\x1b[A\x1b[A"},
        {"ts": 3, "stream": "stdout", "text": "Calibration:  58%|█████▊    | 58/100 [02:47<02:03]\x1b[A\x1b[A"},
        {"ts": 4, "stream": "stdout", "text": "Optimizing:  10%|█         | 1/10"},
        {"ts": 5, "stream": "stdout", "text": "Optimizing:  20%|██        | 2/10"},
        {"ts": 6, "stream": "stdout", "text": "done"},
    ]
    assert [l["text"] for l in ac._tidy_lines(raw)] == [
        "DX-COM 2.3.0", "Calibration:  58%|█████▊    | 58/100 [02:47<02:03]",
        "Optimizing:  20%|██        | 2/10", "done"]


def test_compile_log_shows_completion_once():
    events = [{"id": 1, "type": "SucceedStateEntered", "timestamp": NOW,
               "stateEnteredEventDetails": {"name": "WorkflowComplete"}},
              {"id": 2, "type": "ExecutionSucceeded", "timestamp": NOW, "executionSucceededEventDetails": {}}]
    assert [s["name"] for s in ac._history_steps(events)[0]] == ["WorkflowComplete"]


# ── job list (every models/<folder>/ in the stack's bucket) ──────────────────

def _objects(stubs, objs):
    stubs["s3"].add_response("list_objects_v2", {"Contents": [
        {"Key": k, "Size": size, "LastModified": NOW + datetime.timedelta(minutes=m)} for k, size, m in objs],
        "IsTruncated": False}, {"Bucket": BUCKET, "Prefix": "models/"})


def test_jobs_lists_every_model_folder_newest_first_with_its_state(aws):
    stubs, _ = aws
    _describe(stubs)
    old, new, run, manual = ("models/yolov5s-20261014-093000/", "models/yolov5s-20261014-103000/",
                             "models/resnet-20261014-110000/", "models/console_model/")
    _objects(stubs, [
        (old + "yolov5s.onnx", 100, 0), (old + "yolov5s.json", 1, 0), (old + "yolov5s.dxnn", 17504739, 9),
        (new + "yolov5s.onnx", 100, 60), (new + "yolov5s.json", 1, 60),
        (run + "resnet.onnx", 100, 90), (run + "resnet.json", 1, 90),
        (manual + "m.onnx", 5, 30), (manual + "m.json", 1, 30), (manual + "m.dxnn", 7, 40),
        ("models/stray.txt", 1, 0),
    ])
    _executions(stubs, runs=[
        _run("dx-compile-resnet-aaaa", "RUNNING", start=STARTED + datetime.timedelta(minutes=90)),
        _run("dx-compile-yolov5s-bbbb", "FAILED", start=STARTED + datetime.timedelta(minutes=60)),
    ])
    jobs = ac.list_jobs("dev", REGION, STACK)
    by = {j["prefix"]: j for j in jobs}
    assert [j["prefix"] for j in jobs] == [run, new, manual, old]
    assert by[old]["state"] == "succeeded" and by[old]["dxnn"] == "yolov5s.dxnn"
    assert by[old]["dxnn_size"] == 17504739 and by[old]["model"] == "yolov5s"
    assert by[new]["state"] == "failed"
    assert by[run]["state"] == "running"
    assert by[manual]["state"] == "succeeded" and by[manual]["model"] == "console_model"


def test_status_of_a_console_folder_without_a_dxnn_is_unknown(aws):
    stubs, _ = aws
    _describe(stubs)
    stubs["s3"].add_response("list_objects_v2", {"Contents": [
        {"Key": "models/console_model/m.onnx", "Size": 1}, {"Key": "models/console_model/m.json", "Size": 1}]},
        {"Bucket": BUCKET, "Prefix": "models/console_model/"})
    st = ac.compile_status("dev", REGION, STACK, "models/console_model/")
    assert st["state"] == "unknown" and st["execution"] is None

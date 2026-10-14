"""DX Edge cloud compile — core logic against stubbed AWS (botocore Stubber, no network).

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
        for svc in ("cloudformation", "s3", "stepfunctions")
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
    assert st["default_region"] == "ap-northeast-2"
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
    "models/yolov5s/", "models/yolov5s-2026-1014/", "models/.hidden-20261014-093000/",
])
def test_bad_prefixes_are_rejected(prefix):
    with pytest.raises(ac.AwsError) as exc:
        ac.validate_prefix(prefix)
    assert exc.value.status == 400


@pytest.mark.parametrize("prefix", [PREFIX, PREFIX.rstrip("/")])
def test_good_prefix_is_normalised(prefix):
    assert ac.validate_prefix(prefix) == PREFIX


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

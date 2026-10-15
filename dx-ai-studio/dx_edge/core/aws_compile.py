"""Cloud ONNX → DXNN compile on a DEEPX Compiler Solution CloudFormation stack.

The stack's pipeline (dx-edge/docs/source/02_DEEPX_Compiler_Solution.md): <model>.onnx and
<model>.json uploaded to the same prefix of the stack's ModelBucketName start a Lambda trigger →
Step Functions (StateMachineArn) → an EC2 compiler instance, which writes <model>.dxnn next to them.
Logs land in the CloudWatch log group /dx-compiler/<stack-name>/execution.

Credentials: boto3's default chain, optionally narrowed to a named profile. Nothing here accepts,
stores, logs or returns an access key. The bucket is always read from the stack outputs on the
server — a client never names it.

boto3 is optional (the studio itself is standard library only); without it every call raises
AwsError(503) with an install hint.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote

DEFAULT_REGION = "ap-northeast-2"
INSTALL_HINT = "pip install boto3  (or: pip install -e '.[aws]')"
MAX_ONNX_BYTES = 500 * 1024 * 1024
MAX_JSON_BYTES = 1024 * 1024

_READY = ("CREATE_COMPLETE", "UPDATE_COMPLETE")
_FAILED = ("FAILED", "TIMED_OUT", "ABORTED")
_REGION_RE = re.compile(r"^[a-z]{2}(-[a-z]+)+-\d$")
_STACK_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,127}$")
# models/<stem>-<YYYYmmdd-HHMMSS>/ — exactly what start_compile creates.
_PREFIX_RE = re.compile(r"^models/([A-Za-z0-9_][A-Za-z0-9_.-]{0,79})-(\d{8}-\d{6})/$")
_CHUNK = 1024 * 1024


class AwsError(Exception):
    """A failure to report to the client as {"error": message} with HTTP status."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def _boto3():
    try:
        import boto3
    except ImportError:
        raise AwsError(503, f"boto3 is not installed — {INSTALL_HINT}") from None
    return boto3


def _session(profile: str = "", region: str | None = None):
    """A boto3 Session; a bad AWS_PROFILE env var fails here, before any API call."""
    from botocore.exceptions import ProfileNotFound
    try:
        return _boto3().session.Session(profile_name=profile or None, region_name=region)
    except ProfileNotFound:
        if profile:
            raise AwsError(400, "Unknown AWS profile") from None
        raise AwsError(400, f"AWS_PROFILE={os.environ.get('AWS_PROFILE', '')!r} is not a configured "
                            "profile — unset it or fix ~/.aws/config") from None


def _client(service: str, profile: str, region: str):
    return _session(profile, region).client(service)


def _profiles() -> list[str]:
    return list(_session().available_profiles)


def _check(profile: str, region: str, stack: str | None = None) -> None:
    if not _REGION_RE.match(region or ""):
        raise AwsError(400, "Invalid region")
    if stack is not None and not _STACK_RE.match(stack or ""):
        raise AwsError(400, "Invalid stack name")
    if profile and profile not in _profiles():
        raise AwsError(400, "Unknown AWS profile")


def _call(fn, *args, **kwargs):
    """Run a boto3 call; botocore errors become AwsError without echoing request data."""
    from botocore.exceptions import (BotoCoreError, ClientError, NoCredentialsError,
                                     NoRegionError, PartialCredentialsError, ProfileNotFound)
    try:
        return fn(*args, **kwargs)
    except (NoCredentialsError, PartialCredentialsError):
        raise AwsError(401, "AWS credentials not found — run `aws configure` or `aws sso login`") from None
    except ProfileNotFound:
        raise AwsError(400, "Unknown AWS profile") from None
    except NoRegionError:
        raise AwsError(400, "Invalid region") from None
    except ClientError as exc:
        err = exc.response.get("Error", {})
        raise AwsError(502, f"{err.get('Code', 'AWS error')}: {err.get('Message', '')}".strip()) from None
    except BotoCoreError as exc:
        raise AwsError(502, type(exc).__name__) from None


def validate_prefix(prefix: str) -> str:
    """A job prefix this module created: models/<one safe segment>/ (normalised with the slash)."""
    p = (prefix or "").strip()
    if p and not p.endswith("/"):
        p += "/"
    if ".." in p or not _PREFIX_RE.match(p):
        raise AwsError(400, "Invalid job prefix")
    return p


def _safe_stem(filename: str) -> str:
    stem = PurePosixPath((filename or "").replace("\\", "/")).stem
    stem = re.sub(r"\.{2,}", ".", re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)).strip("._-")
    return stem[:80] or "model"


# ── Public API ─────────────────────────────────────────────────────────────

def status() -> dict:
    try:
        profiles = _profiles()
    except AwsError as exc:
        if exc.status == 503:
            return {"boto3": False, "profiles": [], "default_region": DEFAULT_REGION,
                    "install_hint": INSTALL_HINT}
        return {"boto3": True, "profiles": [], "default_region": DEFAULT_REGION,
                "error": exc.message}
    return {"boto3": True, "profiles": profiles, "default_region": DEFAULT_REGION}


def identity(profile: str, region: str) -> dict:
    """Who the credentials belong to (sts get-caller-identity) — the page's Check connection."""
    _boto3()
    _check(profile, region)
    me = _call(_client("sts", profile, region).get_caller_identity)
    return {"account": me["Account"], "arn": me["Arn"]}


def _outputs(profile: str, region: str, stack: str) -> dict:
    cf = _client("cloudformation", profile, region)
    stacks = _call(cf.describe_stacks, StackName=stack)["Stacks"]
    outputs = {o["OutputKey"]: o["OutputValue"] for o in (stacks[0].get("Outputs") or [])} if stacks else {}
    if not outputs.get("ModelBucketName"):
        raise AwsError(400, "Stack has no ModelBucketName output — not a DEEPX Compiler stack")
    return outputs


def stack_row(s: dict) -> dict | None:
    """A describe_stacks entry as the page shows it, or None when it is not a compiler stack.

    Ready = complete with a ModelBucketName output. Stacks this page created (tag ManagedBy) are kept
    in any state — in progress, or failed so they can still be deleted from here. Their outputs only
    exist on success, so the bucket comes from the parameters. kind is "greengrass" for a DEEPX
    Greengrass stack (ThingGroupName output, or the Template tag this page sets), else "compiler".
    """
    outputs = {o["OutputKey"]: o["OutputValue"] for o in (s.get("Outputs") or [])}
    params = {p["ParameterKey"]: p.get("ParameterValue") for p in (s.get("Parameters") or [])}
    status = s.get("StackStatus", "")
    ready = status in _READY and bool(outputs.get("ModelBucketName"))
    tags = s.get("Tags") or []
    ours = {"Key": "ManagedBy", "Value": "dx-ai-studio"} in tags
    if not (ready or ours):
        return None
    greengrass = bool(outputs.get("ThingGroupName")) or {"Key": "Template", "Value": "greengrass"} in tags
    return {
        "name": s["StackName"],
        "kind": "greengrass" if greengrass else "compiler",
        "status": status,
        "bucket": outputs.get("ModelBucketName") or params.get("ModelBucketName", ""),
        "state_machine": bool(outputs.get("StateMachineArn")),
        "created": s["CreationTime"].isoformat(),
        "ready": ready,
        "deletable": ready or not status.endswith("_IN_PROGRESS"),
    }


def list_stacks(profile: str, region: str) -> list[dict]:
    """Compiler stacks: ready ones, plus those this page created in any state."""
    _boto3()
    _check(profile, region)

    def _all():
        cf = _client("cloudformation", profile, region)
        return [s for page in cf.get_paginator("describe_stacks").paginate() for s in page["Stacks"]]

    return [row for row in map(stack_row, _call(_all)) if row]


def start_compile(*, profile: str, region: str, stack: str, onnx_name: str, onnx_data: bytes,
                  json_name: str, json_data: bytes, now: datetime.datetime | None = None) -> dict:
    """Upload the pair to models/<stem>-<YYYYmmdd-HHMMSS>/ in the stack's bucket."""
    _boto3()
    if not (onnx_name or "").lower().endswith(".onnx"):
        raise AwsError(400, "Model file must be .onnx")
    if not (json_name or "").lower().endswith(".json"):
        raise AwsError(400, "Config file must be .json")
    if not onnx_data:
        raise AwsError(400, "Model file is empty")
    if len(onnx_data) > MAX_ONNX_BYTES or len(json_data) > MAX_JSON_BYTES:
        raise AwsError(413, "File too large")
    try:
        cfg = json.loads(json_data)
    except (ValueError, UnicodeDecodeError):
        raise AwsError(400, "Config file is not valid JSON") from None
    if not isinstance(cfg, dict):
        raise AwsError(400, "Config file must be a JSON object")
    _check(profile, region, stack)

    bucket = _outputs(profile, region, stack)["ModelBucketName"]
    stem = _safe_stem(onnx_name)
    prefix = f"models/{stem}-{(now or datetime.datetime.now()).strftime('%Y%m%d-%H%M%S')}/"
    s3 = _client("s3", profile, region)
    # The trigger fires once both files exist, so the order does not matter.
    _call(s3.put_object, Bucket=bucket, Key=prefix + stem + ".onnx", Body=onnx_data)
    _call(s3.put_object, Bucket=bucket, Key=prefix + stem + ".json", Body=json_data)
    return {"prefix": prefix, "stack": stack, "region": region, "model": stem}


def _keys(profile, region, bucket, prefix) -> list[str]:
    s3 = _client("s3", profile, region)
    resp = _call(s3.list_objects_v2, Bucket=bucket, Prefix=prefix)
    return [o["Key"] for o in resp.get("Contents", [])]


def _execution(profile, region, sm_arn, prefix) -> dict | None:
    """The run for this upload: the trigger names it dx-compile-<stem>-<hash>, started after the upload."""
    stem, stamp = _PREFIX_RE.match(prefix).groups()
    # The prefix stamp is local time (start_compile's datetime.now()); a minute of slack for clock skew.
    uploaded = (datetime.datetime.strptime(stamp, "%Y%m%d-%H%M%S").astimezone()
                - datetime.timedelta(minutes=1))
    sfn = _client("stepfunctions", profile, region)
    # ponytail: newest 100 executions (list_executions is newest-first); page further if a stack is that busy.
    for ex in _call(sfn.list_executions, stateMachineArn=sm_arn, maxResults=100)["executions"]:
        if ex["name"].startswith(f"dx-compile-{stem}-") and ex["startDate"] >= uploaded:
            return {"arn": ex["executionArn"], "status": ex["status"]}
    return None


def _links(region, stack, bucket, prefix, sm_arn, execution) -> dict:
    console = f"https://{region}.console.aws.amazon.com"
    group = f"/dx-compiler/{stack}/execution"
    links = {
        "log_group_name": group,
        "logs": f"{console}/cloudwatch/home?region={region}#logsV2:log-groups/log-group/"
                + group.replace("/", "$252F"),
        "s3": f"https://s3.console.aws.amazon.com/s3/buckets/{quote(bucket)}"
              f"?region={region}&prefix={quote(prefix, safe='')}",
    }
    if sm_arn:
        links["state_machine"] = f"{console}/states/home?region={region}#/statemachines/view/{sm_arn}"
    if execution:
        links["execution"] = (f"{console}/states/home?region={region}#/v2/executions/details/"
                              f"{execution['arn']}")
    return links


def compile_status(profile: str, region: str, stack: str, prefix: str) -> dict:
    """pending → running → succeeded | failed, plus console links."""
    prefix = validate_prefix(prefix)
    _boto3()
    _check(profile, region, stack)
    outputs = _outputs(profile, region, stack)
    bucket, sm_arn = outputs["ModelBucketName"], outputs.get("StateMachineArn")
    keys = _keys(profile, region, bucket, prefix)
    dxnn = next((k for k in keys if k.endswith(".dxnn")), None)

    execution = None
    if dxnn:
        state = "succeeded"
    else:
        execution = _execution(profile, region, sm_arn, prefix) if sm_arn else None
        if execution is None:
            state = "pending"
        elif execution["status"] in _FAILED:
            state = "failed"
        else:
            state = "running"  # SUCCEEDED but the .dxnn not listed yet is still "almost there"
    return {
        "state": state,
        "prefix": prefix,
        "files": [k[len(prefix):] for k in keys],
        "dxnn": dxnn[len(prefix):] if dxnn else None,
        "execution": execution,
        "links": _links(region, stack, bucket, prefix, sm_arn, execution),
    }


def open_dxnn(profile: str, region: str, stack: str, prefix: str) -> tuple[str, int, object]:
    """(file name, size, streaming body) of the compiled .dxnn — read it with body.iter_chunks()."""
    prefix = validate_prefix(prefix)
    _boto3()
    _check(profile, region, stack)
    bucket = _outputs(profile, region, stack)["ModelBucketName"]
    dxnn = next((k for k in _keys(profile, region, bucket, prefix) if k.endswith(".dxnn")), None)
    if dxnn is None:
        raise AwsError(404, "No .dxnn under this prefix yet")
    s3 = _client("s3", profile, region)
    obj = _call(s3.get_object, Bucket=bucket, Key=dxnn)
    return PurePosixPath(dxnn).name, obj["ContentLength"], obj["Body"]


def iter_body(body):
    """Chunks of a streaming body; a dropped AWS connection mid-stream becomes AwsError."""
    it = body.iter_chunks(_CHUNK)
    while True:
        chunk = _call(next, it, None)
        if chunk is None:
            return
        yield chunk


def save_dxnn(profile: str, region: str, stack: str, prefix: str, models_dir) -> Path:
    """Download the .dxnn into the Studio models directory (atomic replace)."""
    name, _size, body = open_dxnn(profile, region, stack, prefix)
    target_dir = Path(models_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / name
    fd, tmp = tempfile.mkstemp(dir=target_dir, prefix=".dx-edge-", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            for chunk in iter_body(body):
                f.write(chunk)
        os.chmod(tmp, 0o644)  # mkstemp makes it 0600
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return target

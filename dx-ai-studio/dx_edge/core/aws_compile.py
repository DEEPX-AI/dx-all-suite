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
# Any one-level folder under models/ — also folders made by hand in the S3 console.
_JOB_RE = re.compile(r"^models/([A-Za-z0-9_][A-Za-z0-9_.-]{0,99})/$")
MAX_JOBS = 200
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
    boto3 = _boto3()    # first: without the aws extra there is no botocore either, and that must read as 503
    from botocore.exceptions import ProfileNotFound
    try:
        return boto3.session.Session(profile_name=profile or None, region_name=region)
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
    """A job folder: models/<one safe segment>/ (normalised with the slash)."""
    p = (prefix or "").strip()
    if p and not p.endswith("/"):
        p += "/"
    if ".." in p or not _JOB_RE.match(p):
        raise AwsError(400, "Invalid job prefix")
    return p


def _safe_stem(filename: str) -> str:
    stem = PurePosixPath((filename or "").replace("\\", "/")).stem
    stem = re.sub(r"\.{2,}", ".", re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)).strip("._-")
    return stem[:80] or "model"


# ── Public API ─────────────────────────────────────────────────────────────

# Commercial regions and their console names; the picker's list when the account cannot be asked.
REGION_NAMES = {
    "af-south-1": "Africa (Cape Town)",
    "ap-east-1": "Asia Pacific (Hong Kong)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "ap-northeast-2": "Asia Pacific (Seoul)",
    "ap-northeast-3": "Asia Pacific (Osaka)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "ap-south-2": "Asia Pacific (Hyderabad)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ap-southeast-3": "Asia Pacific (Jakarta)",
    "ap-southeast-4": "Asia Pacific (Melbourne)",
    "ca-central-1": "Canada (Central)",
    "eu-central-1": "Europe (Frankfurt)",
    "eu-central-2": "Europe (Zurich)",
    "eu-north-1": "Europe (Stockholm)",
    "eu-south-1": "Europe (Milan)",
    "eu-south-2": "Europe (Spain)",
    "eu-west-1": "Europe (Ireland)",
    "eu-west-2": "Europe (London)",
    "eu-west-3": "Europe (Paris)",
    "il-central-1": "Israel (Tel Aviv)",
    "me-central-1": "Middle East (UAE)",
    "me-south-1": "Middle East (Bahrain)",
    "sa-east-1": "South America (São Paulo)",
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
}


def status(profile: str = "") -> dict:
    """boto3 present, configured profiles, and the region the picker starts on (the profile's own)."""
    try:
        profiles = _profiles()
    except AwsError as exc:
        if exc.status == 503:
            return {"boto3": False, "profiles": [], "default_region": DEFAULT_REGION,
                    "install_hint": INSTALL_HINT}
        return {"boto3": True, "profiles": [], "default_region": DEFAULT_REGION,
                "error": exc.message}
    try:
        region = _session(profile if profile in profiles else "").region_name or DEFAULT_REGION
    except AwsError:
        region = DEFAULT_REGION
    return {"boto3": True, "profiles": profiles, "default_region": region}


def regions(profile: str) -> dict:
    """Regions enabled for the account (ec2 describe-regions); the known list if AWS cannot answer."""
    _boto3()
    _check(profile, DEFAULT_REGION)
    try:
        names = [r["RegionName"] for r in
                 _call(_client("ec2", profile, DEFAULT_REGION).describe_regions)["Regions"]]
        source = "account"
    except AwsError:
        names, source = list(REGION_NAMES), "builtin"
    return {"regions": [{"code": c, "name": REGION_NAMES.get(c, "")} for c in sorted(names)],
            "source": source}


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
    """The run for this upload: the trigger names it dx-compile-<stem>-<hash>, started after the upload.

    Only Studio uploads (models/<stem>-<YYYYmmdd-HHMMSS>/) carry the time needed to tell runs apart.
    """
    m = _PREFIX_RE.match(prefix)
    if not m:
        return None
    stem, stamp = m.groups()
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
            # A folder made outside Studio cannot be matched to a run.
            state = "pending" if _PREFIX_RE.match(prefix) else "unknown"
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


MAX_LOG_LINES = 2000
# While dxcom runs the workflow loops Wait → Check → Evaluate every 30 seconds: one row for
# CheckCommandStatus with a count, and the loop's two bookkeeping states are not shown.
_POLL_STATE = "CheckCommandStatus"
_HIDDEN_STATES = {"WaitForCompletion", "EvaluateCommandResult"}
_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
_PROGRESS = re.compile(r"^\s*([^:|]{1,60}):\s*\d{1,3}%\|")


def _history_steps(events) -> tuple[list[dict], str | None, str | None, str | None]:
    """(steps, instance id, command id, log group) from a Step Functions execution history."""
    steps, instance, command, group = [], None, None, None
    for e in events:
        typ, t = e["type"], e["timestamp"].isoformat()
        if typ.endswith("StateEntered"):
            name = e["stateEnteredEventDetails"]["name"]
            if name in _HIDDEN_STATES:
                continue
            poll = next((s for s in steps if s["name"] == name), None) if name == _POLL_STATE else None
            if poll:
                poll["count"] += 1
            else:
                steps.append({"time": t, "name": name, "status": "ok", "detail": "", "count": 1})
        elif typ == "ExecutionSucceeded" and steps and steps[-1]["name"] == "WorkflowComplete":
            continue  # the template's own success state already says so
        elif typ in ("ExecutionStarted", "ExecutionSucceeded"):
            steps.append({"time": t, "name": typ, "status": "ok", "detail": "", "count": 1})
        elif typ in ("TaskFailed", "ExecutionFailed", "ExecutionTimedOut", "ExecutionAborted"):
            d = next((v for k, v in e.items() if k.endswith("EventDetails")), {}) or {}
            detail = " — ".join(x for x in (d.get("error", ""), d.get("cause", "")[:300]) if x)
            steps.append({"time": t, "name": typ, "status": "failed", "detail": detail, "count": 1})
        elif typ == "TaskSucceeded":
            d = e["taskSucceededEventDetails"]
            try:
                out = json.loads(d.get("output") or "{}")
            except ValueError:
                continue
            if d.get("resource") == "runInstances" and out.get("Instances"):
                instance = out["Instances"][0].get("InstanceId")
                if steps:
                    steps[-1]["detail"] = instance or ""
            elif d.get("resource") == "sendCommand" and out.get("Command"):
                command = out["Command"].get("CommandId")
                group = (out["Command"].get("CloudWatchOutputConfig") or {}).get("CloudWatchLogGroupName")
    return steps, instance, command, group


def _stream_lines(logs, group: str, stream: str, kind: str) -> list[dict]:
    lines, token = [], None
    while True:
        kwargs = {"logGroupName": group, "logStreamName": stream, "startFromHead": True, "limit": 1000}
        if token:
            kwargs["nextToken"] = token
        try:
            resp = _call(logs.get_log_events, **kwargs)
        except AwsError as exc:
            if exc.message.startswith("ResourceNotFoundException"):
                return lines  # dxcom has not written to this stream yet
            raise
        for ev in resp.get("events", []):
            for text in ev["message"].rstrip("\n").split("\n"):
                lines.append({"ts": ev["timestamp"], "stream": kind, "text": text})
        if not resp.get("events") or resp.get("nextForwardToken") == token:
            return lines
        token = resp.get("nextForwardToken")


def _tidy_lines(lines: list[dict]) -> list[dict]:
    """Drop terminal control codes, and keep only the newest line of each tqdm progress bar."""
    out = []
    for line in lines:
        text = _ANSI.sub("", line["text"]).strip()
        if not text:
            continue
        bar = _PROGRESS.match(text)
        if bar and out and out[-1].get("_bar") == bar.group(1):
            out[-1] = {**line, "text": text, "_bar": bar.group(1)}
        else:
            out.append({**line, "text": text, "_bar": bar.group(1) if bar else None})
    return [{k: v for k, v in l.items() if k != "_bar"} for l in out]


def compile_log(profile: str, region: str, stack: str, prefix: str) -> dict:
    """The run's workflow steps (Step Functions history) and dxcom's output (CloudWatch Logs)."""
    prefix = validate_prefix(prefix)
    _boto3()
    _check(profile, region, stack)
    outputs = _outputs(profile, region, stack)
    sm_arn = outputs.get("StateMachineArn")
    execution = _execution(profile, region, sm_arn, prefix) if sm_arn else None
    empty = {"execution": execution, "steps": [], "lines": [], "instance_id": None, "command_id": None}
    if execution is None:
        return empty

    sfn = _client("stepfunctions", profile, region)

    def _events():
        events, token = [], None
        while True:
            kwargs = {"executionArn": execution["arn"], "maxResults": 1000}
            if token:
                kwargs["nextToken"] = token
            resp = sfn.get_execution_history(**kwargs)
            events += resp["events"]
            token = resp.get("nextToken")
            if not token:
                return events

    steps, instance, command, group = _history_steps(_call(_events))
    lines = []
    if instance and command:
        group = group or outputs.get("CompilerExecutionLogGroupName") or f"/dx-compiler/{stack}/execution"
        logs = _client("logs", profile, region)
        for kind in ("stdout", "stderr"):
            lines += _stream_lines(logs, group, f"{command}/{instance}/CompileModel/{kind}", kind)
        lines.sort(key=lambda l: l["ts"])  # stable: lines of one event keep their order
        lines = _tidy_lines(lines)
        lines = [{"time": datetime.datetime.fromtimestamp(l["ts"] / 1000, datetime.timezone.utc).isoformat(),
                  "stream": l["stream"], "text": l["text"]} for l in lines[-MAX_LOG_LINES:]]
    return {**empty, "steps": steps, "lines": lines, "instance_id": instance, "command_id": command}


def list_jobs(profile: str, region: str, stack: str) -> list[dict]:
    """Every models/<folder>/ in the stack's bucket, newest first, with its state and .dxnn.

    One S3 listing gives the files; one list_executions call gives the runs of folders that have no
    .dxnn yet. Folders from another Studio session or the S3 console show up too.
    """
    _boto3()
    _check(profile, region, stack)
    outputs = _outputs(profile, region, stack)
    bucket, sm_arn = outputs["ModelBucketName"], outputs.get("StateMachineArn")
    s3 = _client("s3", profile, region)

    def _objects():
        return [o for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix="models/")
                for o in page.get("Contents", [])]

    folders: dict[str, list] = {}
    for obj in _call(_objects):
        prefix, _, name = obj["Key"].rpartition("/")
        prefix += "/"
        if name and _JOB_RE.match(prefix):
            folders.setdefault(prefix, []).append(obj)

    runs = []
    if sm_arn and any(not any(o["Key"].endswith(".dxnn") for o in objs) for objs in folders.values()):
        sfn = _client("stepfunctions", profile, region)
        runs = _call(sfn.list_executions, stateMachineArn=sm_arn, maxResults=100)["executions"]

    jobs = []
    for prefix, objs in folders.items():
        dxnn = next((o for o in objs if o["Key"].endswith(".dxnn")), None)
        studio = _PREFIX_RE.match(prefix)
        if studio:
            stem, stamp = studio.groups()
            uploaded = datetime.datetime.strptime(stamp, "%Y%m%d-%H%M%S").astimezone()
        else:
            stem = _JOB_RE.match(prefix).group(1)
            uploaded = min(o["LastModified"] for o in objs).astimezone()
        if dxnn:
            state = "succeeded"
        elif not studio:
            state = "unknown"
        else:
            since = uploaded - datetime.timedelta(minutes=1)
            run = next((r for r in runs if r["name"].startswith(f"dx-compile-{stem}-")
                        and r["startDate"] >= since), None)
            state = ("pending" if run is None else "failed" if run["status"] in _FAILED else "running")
        jobs.append({
            "prefix": prefix,
            "model": stem,
            "uploaded": uploaded.isoformat(),
            "state": state,
            "dxnn": dxnn["Key"][len(prefix):] if dxnn else None,
            "dxnn_size": dxnn["Size"] if dxnn else None,
            "files": sorted(o["Key"][len(prefix):] for o in objs),
        })
    jobs.sort(key=lambda j: j["uploaded"], reverse=True)
    return jobs[:MAX_JOBS]


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

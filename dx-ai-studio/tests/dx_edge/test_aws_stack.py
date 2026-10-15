"""DX Cloud stack setup — Marketplace subscription check and CloudFormation create/delete.

AWS is botocore Stubber only (no network); nothing here creates or deletes real resources.
"""
from __future__ import annotations

import datetime
import json
import re

import boto3
import pytest
from botocore.stub import ANY, Stubber

from dx_edge.core import aws_compile as ac
from dx_edge.core import aws_stack as st

REGION = "ap-northeast-2"
NAME = "dx-cloud-261015093000"
BUCKET = "dx-models-bucket-123"
NOW = datetime.datetime(2026, 10, 15, 9, 30, 0)
COMPILER_SSM = "/aws/service/marketplace/prod-ei6ws54bjw7to/dx-compiler-automation-2.3.0"


@pytest.fixture()
def aws(monkeypatch, tmp_path):
    cfg = tmp_path / "config"
    cfg.write_text("[default]\nregion = us-east-1\n[profile dev]\nregion = ap-northeast-2\n")
    (tmp_path / "credentials").write_text("")
    monkeypatch.setenv("AWS_CONFIG_FILE", str(cfg))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(tmp_path / "credentials"))
    for var in ("AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.delenv(var, raising=False)
    clients = {
        svc: boto3.client(svc, region_name=REGION, aws_access_key_id="AKIAFAKEFAKEFAKE0000",
                          aws_secret_access_key="fake")
        for svc in ("cloudformation", "ssm", "ec2")
    }
    stubs = {svc: Stubber(c) for svc, c in clients.items()}
    monkeypatch.setattr(ac, "_client", lambda service, profile, region: clients[service])
    for s in stubs.values():
        s.activate()
    yield stubs
    for s in stubs.values():
        s.assert_no_pending_responses()
        s.deactivate()


def _ssm(stubs, name, ami="ami-0123456789abcdef0"):
    if ami:
        stubs["ssm"].add_response(
            "get_parameter", {"Parameter": {"Name": name, "Type": "String", "Value": ami}}, {"Name": name})
    else:
        stubs["ssm"].add_client_error("get_parameter", "ParameterNotFound", expected_params={"Name": name})


def _vpc(stubs, vpcs=("vpc-1",), subnets=("subnet-1",)):
    stubs["ec2"].add_response(
        "describe_vpcs", {"Vpcs": [{"VpcId": v} for v in vpcs]},
        {"Filters": [{"Name": "isDefault", "Values": ["true"]}]})
    if vpcs:
        stubs["ec2"].add_response(
            "describe_subnets", {"Subnets": [{"SubnetId": s} for s in subnets]},
            {"Filters": [{"Name": "vpc-id", "Values": [vpcs[0]]},
                         {"Name": "default-for-az", "Values": ["true"]}]})


# ── vendored templates ──────────────────────────────────────────────────────

def test_templates_fit_template_body_limit():
    for t in st.templates():
        body = st._body(t["id"])
        assert len(body.encode("utf-8")) <= 51_200, t["id"]
        tpl = json.loads(body)
        assert tpl["Parameters"]["ImageId"]["Default"].startswith("/aws/service/marketplace/")
        assert tpl["Parameters"]["ImageId"]["Default"] == t["ssm"]
        for p in ("ModelBucketName", "VpcId", "SubnetId"):
            assert p in tpl["Parameters"], (t["id"], p)
        assert "ModelBucketName" in tpl["Outputs"]


def test_templates_lists_both_with_marketplace_links():
    ids = {t["id"]: t for t in st.templates()}
    assert set(ids) == {"compiler", "greengrass"}
    assert ids["compiler"]["ssm"] == COMPILER_SSM
    assert "prodview-ev6ed5omu4ulo" in ids["compiler"]["marketplace"]
    assert ids["greengrass"]["marketplace"].startswith("https://aws.amazon.com/marketplace/")


# ── subscription ────────────────────────────────────────────────────────────

def test_subscription_reports_each_template(aws):
    ts = st.templates()
    _ssm(aws, ts[0]["ssm"])
    _ssm(aws, ts[1]["ssm"], ami=None)
    rows = st.subscription("dev", REGION)
    assert [r["subscribed"] for r in rows] == [True, False]
    assert rows[0]["ami_id"] == "ami-0123456789abcdef0" and rows[1]["ami_id"] is None
    assert rows[0]["label"] and rows[0]["marketplace"]


def test_subscription_other_errors_are_aws_errors(aws):
    aws["ssm"].add_client_error("get_parameter", "AccessDeniedException")
    with pytest.raises(ac.AwsError) as exc:
        st.subscription("", REGION)
    assert exc.value.status == 502


# ── create ──────────────────────────────────────────────────────────────────

def test_create_passes_bucket_network_capabilities_and_tags(aws):
    _ssm(aws, COMPILER_SSM)
    _vpc(aws)
    aws["cloudformation"].add_response(
        "create_stack", {"StackId": "arn:stack"},
        {"StackName": NAME, "TemplateBody": st._body("compiler"),
         "Parameters": ANY, "Capabilities": ["CAPABILITY_IAM"], "Tags": ANY})
    seen = {}
    real = aws["cloudformation"].client.create_stack

    def spy(**kw):
        seen.update(kw)
        return real(**kw)

    aws["cloudformation"].client.create_stack = spy
    out = st.create_stack("dev", REGION, "compiler", NAME)
    params = {p["ParameterKey"]: p["ParameterValue"] for p in seen["Parameters"]}
    assert set(params) == {"ModelBucketName", "VpcId", "SubnetId"}
    assert params["VpcId"] == "vpc-1" and params["SubnetId"] == "subnet-1"
    assert re.fullmatch(re.escape(NAME) + r"-[0-9a-f]{8}", params["ModelBucketName"])
    assert {"Key": "ManagedBy", "Value": "dx-ai-studio"} in seen["Tags"]
    assert {"Key": "Template", "Value": "compiler"} in seen["Tags"]
    assert out == {"name": NAME, "bucket": params["ModelBucketName"], "template": "compiler"}


def test_bucket_name_is_a_valid_s3_name_even_for_long_stack_names():
    b = st._bucket_name("A" + "b-" * 60 + "c")
    assert len(b) <= 63
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]*[a-z0-9]", b)


def test_create_refuses_when_not_subscribed(aws):
    _ssm(aws, COMPILER_SSM, ami=None)
    with pytest.raises(ac.AwsError) as exc:
        st.create_stack("", REGION, "compiler", NAME)
    assert exc.value.status == 400
    assert "Marketplace" in exc.value.message


@pytest.mark.parametrize("vpcs,subnets", [((), ()), (("vpc-1",), ())])
def test_create_needs_a_default_vpc_and_subnet(aws, vpcs, subnets):
    _ssm(aws, COMPILER_SSM)
    _vpc(aws, vpcs, subnets)
    with pytest.raises(ac.AwsError) as exc:
        st.create_stack("", REGION, "compiler", NAME)
    assert exc.value.status == 400
    assert "default" in exc.value.message.lower()


@pytest.mark.parametrize("template,name", [("compiler", "1bad"), ("compiler", "a b"),
                                           ("compiler", ""), ("ubuntu", NAME), ("", NAME)])
def test_create_rejects_bad_input_before_touching_aws(aws, template, name):
    with pytest.raises(ac.AwsError) as exc:
        st.create_stack("", REGION, template, name)
    assert exc.value.status == 400


# ── progress ────────────────────────────────────────────────────────────────

def test_progress_returns_status_and_last_events(aws):
    aws["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [{"StackName": NAME, "StackStatus": "CREATE_IN_PROGRESS", "CreationTime": NOW}]},
        {"StackName": NAME})
    events = [{"StackId": "s", "EventId": str(i), "StackName": NAME, "Timestamp": NOW,
               "LogicalResourceId": f"R{i}", "ResourceStatus": "CREATE_IN_PROGRESS"} for i in range(15)]
    events[0]["ResourceStatusReason"] = "Resource creation Initiated"
    aws["cloudformation"].add_response("describe_stack_events", {"StackEvents": events}, {"StackName": NAME})
    out = st.stack_progress("", REGION, NAME)
    assert out["status"] == "CREATE_IN_PROGRESS"
    assert len(out["events"]) == 10
    assert out["events"][0] == {"resource": "R0", "status": "CREATE_IN_PROGRESS",
                                "reason": "Resource creation Initiated", "time": NOW.isoformat()}


def test_progress_of_a_deleted_stack_is_delete_complete(aws):
    aws["cloudformation"].add_client_error(
        "describe_stacks", "ValidationError", f"Stack with id {NAME} does not exist")
    assert st.stack_progress("", REGION, NAME) == {"name": NAME, "status": "DELETE_COMPLETE", "events": []}


# ── delete ──────────────────────────────────────────────────────────────────

def test_delete_requires_the_typed_name(aws):
    with pytest.raises(ac.AwsError) as exc:
        st.delete_stack("", REGION, NAME, NAME + "x")
    assert exc.value.status == 400


def test_delete_refuses_a_stack_without_a_model_bucket(aws):
    aws["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [{"StackName": NAME, "StackStatus": "CREATE_COMPLETE", "CreationTime": NOW,
                     "Outputs": [{"OutputKey": "Foo", "OutputValue": "x"}]}]},
        {"StackName": NAME})
    with pytest.raises(ac.AwsError) as exc:
        st.delete_stack("", REGION, NAME, NAME)
    assert exc.value.status == 400


def test_delete_starts_deletion_and_says_the_bucket_stays(aws):
    aws["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [{"StackName": NAME, "StackStatus": "CREATE_COMPLETE", "CreationTime": NOW,
                     "Outputs": [{"OutputKey": "ModelBucketName", "OutputValue": BUCKET}]}]},
        {"StackName": NAME})
    aws["cloudformation"].add_response("delete_stack", {}, {"StackName": NAME})
    out = st.delete_stack("", REGION, NAME, NAME)
    assert out == {"name": NAME, "status": "DELETE_IN_PROGRESS", "bucket": BUCKET, "bucket_retained": True}


# ── list_stacks additions ───────────────────────────────────────────────────

def test_list_stacks_adds_created_and_in_progress_studio_stacks(aws):
    aws["cloudformation"].add_response("describe_stacks", {"Stacks": [
        {"StackName": "ready", "StackStatus": "CREATE_COMPLETE", "CreationTime": NOW,
         "Outputs": [{"OutputKey": "ModelBucketName", "OutputValue": BUCKET}]},
        {"StackName": "mine", "StackStatus": "CREATE_IN_PROGRESS", "CreationTime": NOW,
         "Parameters": [{"ParameterKey": "ModelBucketName", "ParameterValue": "mine-0a1b2c3d"}],
         "Tags": [{"Key": "ManagedBy", "Value": "dx-ai-studio"}]},
        {"StackName": "foreign", "StackStatus": "CREATE_IN_PROGRESS", "CreationTime": NOW},
    ]}, {})
    stacks = ac.list_stacks("", REGION)
    assert [(s["name"], s["ready"]) for s in stacks] == [("ready", True), ("mine", False)]
    assert stacks[0]["created"] == NOW.isoformat()
    assert stacks[1]["bucket"] == "mine-0a1b2c3d"


def test_list_stacks_keeps_failed_studio_stacks_so_they_can_be_deleted(aws):
    ours = [{"Key": "ManagedBy", "Value": "dx-ai-studio"}]
    aws["cloudformation"].add_response("describe_stacks", {"Stacks": [
        {"StackName": "ready", "StackStatus": "CREATE_COMPLETE", "CreationTime": NOW,
         "Outputs": [{"OutputKey": "ModelBucketName", "OutputValue": BUCKET}]},
        {"StackName": "busy", "StackStatus": "CREATE_IN_PROGRESS", "CreationTime": NOW, "Tags": ours},
        {"StackName": "broken", "StackStatus": "ROLLBACK_COMPLETE", "CreationTime": NOW, "Tags": ours},
        {"StackName": "foreign-broken", "StackStatus": "ROLLBACK_COMPLETE", "CreationTime": NOW},
    ]}, {})
    stacks = ac.list_stacks("", REGION)
    assert [(s["name"], s["ready"], s["deletable"]) for s in stacks] == [
        ("ready", True, True), ("busy", False, False), ("broken", False, True)]


def test_delete_accepts_a_failed_studio_stack(aws):
    aws["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [{"StackName": NAME, "StackStatus": "ROLLBACK_COMPLETE", "CreationTime": NOW,
                     "Parameters": [{"ParameterKey": "ModelBucketName", "ParameterValue": BUCKET}],
                     "Tags": [{"Key": "ManagedBy", "Value": "dx-ai-studio"}]}]},
        {"StackName": NAME})
    aws["cloudformation"].add_response("delete_stack", {}, {"StackName": NAME})
    assert st.delete_stack("", REGION, NAME, NAME)["bucket"] == BUCKET


def test_delete_refuses_a_stack_still_in_progress(aws):
    aws["cloudformation"].add_response(
        "describe_stacks",
        {"Stacks": [{"StackName": NAME, "StackStatus": "CREATE_IN_PROGRESS", "CreationTime": NOW,
                     "Tags": [{"Key": "ManagedBy", "Value": "dx-ai-studio"}]}]},
        {"StackName": NAME})
    with pytest.raises(ac.AwsError) as exc:
        st.delete_stack("", REGION, NAME, NAME)
    assert exc.value.status == 400


# ── stack kind ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("outputs,tags,kind", [
    ({"ModelBucketName": BUCKET}, [], "compiler"),
    ({"ModelBucketName": BUCKET, "ThingGroupName": "g"}, [], "greengrass"),
    ({}, [{"Key": "ManagedBy", "Value": "dx-ai-studio"}, {"Key": "Template", "Value": "greengrass"}],
     "greengrass"),
    ({}, [{"Key": "ManagedBy", "Value": "dx-ai-studio"}, {"Key": "Template", "Value": "compiler"}],
     "compiler"),
])
def test_stack_row_reports_its_kind(outputs, tags, kind):
    row = ac.stack_row({"StackName": NAME, "StackStatus": "CREATE_COMPLETE", "CreationTime": NOW,
                        "Outputs": [{"OutputKey": k, "OutputValue": v} for k, v in outputs.items()],
                        "Tags": tags})
    assert row["kind"] == kind
    assert {"name", "status", "bucket", "state_machine", "created", "ready", "deletable"} <= set(row)

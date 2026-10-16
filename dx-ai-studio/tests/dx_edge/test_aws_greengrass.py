"""DX Cloud Greengrass tab — dx-runtime core devices, their components, and the install script.

AWS is botocore Stubber only (no network); nothing here creates or deletes real resources.
"""
from __future__ import annotations

import datetime
import subprocess

import pytest
# boto3 is the optional `aws` extra (pyproject.toml): without it these files skip instead of
# breaking the collection gate of a studio installed without DX Cloud compile.
boto3 = pytest.importorskip("boto3", reason="boto3 (the optional aws extra) is not installed")
from botocore.stub import Stubber

from dx_edge.core import aws_compile as ac
from dx_edge.core import aws_greengrass as gg

REGION = "ap-northeast-2"
STACK = "ggstack1"
GROUP = "ggstack1-CoreDevices"
ROLE = "ggstack1-GreengrassTokenExchangeRole-ABC123"
DEPLOYMENT = "0f5e2d4c-1111-2222-3333-444455556666"
NOW = datetime.datetime(2026, 10, 15, 9, 30, 0, tzinfo=datetime.timezone.utc)
GG_OUTPUTS = {"ModelBucketName": "gg-bucket", "StateMachineArn": "arn:sm", "ThingGroupName": GROUP,
              "TokenExchangeRoleName": ROLE, "GreengrassDeploymentId": DEPLOYMENT, "ProjectName": "dx"}


@pytest.fixture()
def aws(monkeypatch, tmp_path):
    (tmp_path / "config").write_text("[default]\nregion = us-east-1\n")
    (tmp_path / "credentials").write_text("")
    monkeypatch.setenv("AWS_CONFIG_FILE", str(tmp_path / "config"))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(tmp_path / "credentials"))
    for var in ("AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.delenv(var, raising=False)
    clients = {
        svc: boto3.client(svc, region_name=REGION, aws_access_key_id="AKIAFAKEFAKEFAKE0000",
                          aws_secret_access_key="fake")
        for svc in ("cloudformation", "iot", "greengrassv2")
    }
    stubs = {svc: Stubber(c) for svc, c in clients.items()}
    monkeypatch.setattr(ac, "_client", lambda service, profile, region: clients[service])
    for s in stubs.values():
        s.activate()
    yield stubs
    for s in stubs.values():
        s.assert_no_pending_responses()
        s.deactivate()


def _stack(stubs, outputs=GG_OUTPUTS):
    stubs["cloudformation"].add_response("describe_stacks", {"Stacks": [{
        "StackName": STACK, "StackStatus": "CREATE_COMPLETE", "CreationTime": NOW,
        "Outputs": [{"OutputKey": k, "OutputValue": v} for k, v in outputs.items()]}]},
        {"StackName": STACK})


# ── devices ─────────────────────────────────────────────────────────────────

def test_devices_are_core_devices_that_are_in_the_thing_group(aws):
    _stack(aws)
    aws["iot"].add_response("list_things_in_thing_group", {"things": ["dev-b", "dev-a", "plain-thing"]},
                            {"thingGroupName": GROUP})
    aws["greengrassv2"].add_response("list_core_devices", {"coreDevices": [
        {"coreDeviceThingName": "dev-a", "status": "HEALTHY", "lastStatusUpdateTimestamp": NOW},
        {"coreDeviceThingName": "dev-b", "status": "UNHEALTHY", "lastStatusUpdateTimestamp": NOW},
        {"coreDeviceThingName": "other-group-dev", "status": "HEALTHY", "lastStatusUpdateTimestamp": NOW},
    ]}, {})
    aws["greengrassv2"].add_response("get_deployment", {"deploymentId": DEPLOYMENT,
                                                        "deploymentStatus": "ACTIVE"},
                                     {"deploymentId": DEPLOYMENT})
    out = gg.devices("", REGION, STACK)
    assert out["thing_group"] == GROUP
    assert out["deployment"] == {"id": DEPLOYMENT, "status": "ACTIVE"}
    assert out["devices"] == [
        {"name": "dev-a", "status": "HEALTHY", "last_update": NOW.isoformat()},
        {"name": "dev-b", "status": "UNHEALTHY", "last_update": NOW.isoformat()},
    ]


def test_devices_still_lists_devices_when_the_deployment_lookup_fails(aws):
    _stack(aws)
    aws["iot"].add_response("list_things_in_thing_group", {"things": ["dev-a"]}, {"thingGroupName": GROUP})
    aws["greengrassv2"].add_response("list_core_devices", {"coreDevices": [
        {"coreDeviceThingName": "dev-a", "status": "HEALTHY", "lastStatusUpdateTimestamp": NOW}]}, {})
    aws["greengrassv2"].add_client_error("get_deployment", "ResourceNotFoundException", "gone")
    out = gg.devices("", REGION, STACK)
    assert out["deployment"]["status"] == "UNKNOWN"
    assert "ResourceNotFoundException" in out["deployment"]["error"]
    assert [d["name"] for d in out["devices"]] == ["dev-a"]

def test_devices_refuses_a_compiler_stack(aws):
    _stack(aws, {"ModelBucketName": "b", "StateMachineArn": "arn:sm"})
    with pytest.raises(ac.AwsError) as exc:
        gg.devices("", REGION, STACK)
    assert exc.value.status == 400
    assert "Greengrass" in exc.value.message


def test_devices_validates_before_touching_aws(aws):
    with pytest.raises(ac.AwsError) as exc:
        gg.devices("", REGION, "1bad")
    assert exc.value.status == 400


# ── components ──────────────────────────────────────────────────────────────

def test_components_lists_deepx_and_greengrass_components_only(aws):
    aws["greengrassv2"].add_response("list_installed_components", {"installedComponents": [
        {"componentName": "com.deepx.dx-runtime", "componentVersion": "1.2.0", "lifecycleState": "RUNNING"},
        {"componentName": "aws.greengrass.Nucleus", "componentVersion": "2.14.0", "lifecycleState": "FINISHED"},
        {"componentName": "aws.greengrass.Cli", "componentVersion": "2.14.0", "lifecycleState": "RUNNING"},
        {"componentName": "com.example.Other", "componentVersion": "1.0.0", "lifecycleState": "RUNNING"},
    ]}, {"coreDeviceThingName": "dev-a"})
    assert gg.components("", REGION, "dev-a") == [
        {"name": "com.deepx.dx-runtime", "version": "1.2.0", "state": "RUNNING"},
        {"name": "aws.greengrass.Nucleus", "version": "2.14.0", "state": "FINISHED"},
        {"name": "aws.greengrass.Cli", "version": "2.14.0", "state": "RUNNING"},
    ]


@pytest.mark.parametrize("device", ["", "a b", "x;rm -rf /", "a" * 129])
def test_components_rejects_bad_device_names(aws, device):
    with pytest.raises(ac.AwsError) as exc:
        gg.components("", REGION, device)
    assert exc.value.status == 400


# ── install script ──────────────────────────────────────────────────────────

def test_install_script_provisions_into_the_stack_group_without_credentials(aws):
    _stack(aws)
    out = gg.install_script("", REGION, STACK, "dx-device-01")
    assert out["thing"] == "dx-device-01" and out["thing_group"] == GROUP
    s = out["script"]
    assert s.startswith("#!/usr/bin/env bash")
    for part in ("command -v java", "greengrass-nucleus-latest.zip",
                 "sudo -E java -Droot=/greengrass/v2 -Dlog.store=FILE",
                 "-jar ./GreengrassInstaller/lib/Greengrass.jar",
                 f"--aws-region {REGION}", "--thing-name dx-device-01", f"--thing-group-name {GROUP}",
                 f"--tes-role-name {ROLE}", "--component-default-user ggc_user:ggc_group",
                 "--provision true", "--setup-system-service true", "--deploy-dev-tools true",
                 "sleep 10", "-ge 5", "sudo systemctl status greengrass.service --no-pager"):
        assert part in s, part
    for secret in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        assert secret not in s
    assert "credentials" in s.lower() and "Java 11" in s
    subprocess.run(["bash", "-n"], input=s, text=True, check=True)


def test_install_script_quotes_thing_names(aws):
    _stack(aws)
    s = gg.install_script("", REGION, STACK, "thing:with:colons")["script"]
    assert "--thing-name thing:with:colons" in s  # shlex leaves a safe name bare
    _stack(aws, {**GG_OUTPUTS, "TokenExchangeRoleName": "role+name=x"})
    s = gg.install_script("", REGION, STACK, "dev")["script"]
    assert "--tes-role-name role+name=x" in s


@pytest.mark.parametrize("thing", ["", "a b", "dev;reboot", "$(id)", "a" * 129])
def test_install_script_rejects_bad_thing_names_before_aws(aws, thing):
    with pytest.raises(ac.AwsError) as exc:
        gg.install_script("", REGION, STACK, thing)
    assert exc.value.status == 400


def test_install_script_refuses_a_compiler_stack(aws):
    _stack(aws, {"ModelBucketName": "b"})
    with pytest.raises(ac.AwsError) as exc:
        gg.install_script("", REGION, STACK, "dev")
    assert exc.value.status == 400

"""DX Cloud Greengrass tab: dx-runtime core devices of a DEEPX Greengrass stack, and the script that
registers a new one.

The stack (dx_edge/cfn/greengrass.json) creates a Thing Group (ThingGroupName output), a token
exchange role (TokenExchangeRoleName) and a Greengrass deployment of com.deepx.dx-runtime to the
group (GreengrassDeploymentId). A device joins by running the install script with its own AWS
credentials; the script carries none, and this module never handles any.

Same rules as aws_compile: boto3's default credential chain, and every AWS failure is an AwsError.
"""
from __future__ import annotations

import re
import shlex

from dx_edge.core import aws_compile as ac
from dx_edge.core.aws_compile import AwsError

NUCLEUS_URL = "https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip"
COMPONENT_PREFIXES = ("com.deepx.", "aws.greengrass.")
_IOT_NAME_RE = re.compile(r"^[A-Za-z0-9:_-]{1,128}$")
_ROLE_RE = re.compile(r"^[A-Za-z0-9+=,.@_-]{1,64}$")


def _iot_name(value: str, what: str) -> str:
    if not _IOT_NAME_RE.match(value or ""):
        raise AwsError(400, f"Invalid {what} — letters, digits, ':', '_' or '-', up to 128")
    return value


def _greengrass_outputs(profile: str, region: str, stack: str) -> dict:
    ac._boto3()
    ac._check(profile, region, stack)
    outputs = ac._outputs(profile, region, stack)
    if not outputs.get("ThingGroupName"):
        raise AwsError(400, "Stack has no ThingGroupName output — not a DEEPX Greengrass stack")
    return outputs


def devices(profile: str, region: str, stack: str) -> dict:
    """Thing group, deployment status and the Greengrass core devices in the group."""
    outputs = _greengrass_outputs(profile, region, stack)
    group = outputs["ThingGroupName"]
    iot = ac._client("iot", profile, region)
    gg = ac._client("greengrassv2", profile, region)

    def _members():
        pages = iot.get_paginator("list_things_in_thing_group").paginate(thingGroupName=group)
        return {t for page in pages for t in page.get("things", [])}

    def _cores():
        # Unfiltered, as in the PoC: list_core_devices(thingGroupArn=…) only returns devices whose
        # deployment for the group succeeded, which would hide a freshly registered or failing one.
        return [d for page in gg.get_paginator("list_core_devices").paginate()
                for d in page.get("coreDevices", [])]

    members = ac._call(_members)
    rows = sorted(({
        "name": d["coreDeviceThingName"],
        "status": d.get("status", ""),
        "last_update": d["lastStatusUpdateTimestamp"].isoformat() if d.get("lastStatusUpdateTimestamp") else "",
    } for d in ac._call(_cores) if d.get("coreDeviceThingName") in members), key=lambda r: r["name"])

    deployment = None
    if outputs.get("GreengrassDeploymentId"):
        dep_id = outputs["GreengrassDeploymentId"]
        try:
            dep = ac._call(gg.get_deployment, deploymentId=dep_id)
            deployment = {"id": dep_id, "status": dep.get("deploymentStatus", "")}
        except AwsError as exc:
            # A stale or removed deployment must not hide the device list.
            deployment = {"id": dep_id, "status": "UNKNOWN", "error": exc.message}
    return {"thing_group": group, "deployment": deployment, "devices": rows}


def components(profile: str, region: str, device: str) -> list[dict]:
    """DEEPX and Greengrass components installed on a core device."""
    _iot_name(device, "device name")
    ac._boto3()
    ac._check(profile, region)
    gg = ac._client("greengrassv2", profile, region)

    def _all():
        pages = gg.get_paginator("list_installed_components").paginate(coreDeviceThingName=device)
        return [c for page in pages for c in page.get("installedComponents", [])]

    return [{"name": c["componentName"], "version": c.get("componentVersion", ""),
             "state": c.get("lifecycleState", "")}
            for c in ac._call(_all) if c.get("componentName", "").startswith(COMPONENT_PREFIXES)]


def install_script(profile: str, region: str, stack: str, thing: str) -> dict:
    """A bash script that provisions this device into the stack's Thing Group as a core device."""
    _iot_name(thing, "thing name")
    outputs = _greengrass_outputs(profile, region, stack)
    group = _iot_name(outputs["ThingGroupName"], "Thing Group name")
    role = outputs.get("TokenExchangeRoleName", "")
    if not _ROLE_RE.match(role):
        raise AwsError(400, "Stack has no valid TokenExchangeRoleName output")
    q = shlex.quote
    # Region, stack and group passed the patterns above, so they are safe inside the comments.
    script = f"""#!/usr/bin/env bash
# Registers this device as an AWS IoT Greengrass core device of DEEPX Greengrass stack {stack}
# ({region}). The stack's deployment to Thing Group {group} then installs dx-runtime.
#
# Before running it, the device needs:
#   - Java 11 or later (for example: sudo apt install -y openjdk-17-jre-headless)
#   - AWS credentials allowed to provision Greengrass (IoT thing, certificate and policy, IAM role
#     alias), in the environment or in ~/.aws. This script contains no credentials.
set -euo pipefail

if ! command -v java >/dev/null 2>&1; then
  echo "Java 11 or later is required before installing AWS IoT Greengrass Core." >&2
  exit 1
fi

curl -fsSL {NUCLEUS_URL} -o greengrass-nucleus-latest.zip
rm -rf GreengrassInstaller
unzip -q greengrass-nucleus-latest.zip -d GreengrassInstaller

# Provisioning can fail on a transient network reset, so it is retried.
DX_PROVISION_ATTEMPT=0
until sudo -E java -Droot=/greengrass/v2 -Dlog.store=FILE \\
  -jar ./GreengrassInstaller/lib/Greengrass.jar \\
  --aws-region {q(region)} \\
  --thing-name {q(thing)} \\
  --thing-group-name {q(group)} \\
  --tes-role-name {q(role)} \\
  --component-default-user ggc_user:ggc_group \\
  --provision true \\
  --setup-system-service true \\
  --deploy-dev-tools true; do
  DX_PROVISION_ATTEMPT=$((DX_PROVISION_ATTEMPT + 1))
  if [ "$DX_PROVISION_ATTEMPT" -ge 5 ]; then
    echo "Greengrass provisioning failed after 5 attempts." >&2
    exit 1
  fi
  echo "Provisioning attempt failed, retrying in 10s... ($DX_PROVISION_ATTEMPT/5)" >&2
  sleep 10
done

sudo systemctl status greengrass.service --no-pager
"""
    return {"script": script, "thing": thing, "thing_group": group}

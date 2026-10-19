"""DX Cloud stack setup: Marketplace subscription check and DEEPX Compiler stack create/delete.

Templates are vendored as compact JSON in dx_edge/cfn/ (see its README). A template is
"subscribed" when the SSM parameter its ImageId defaults to resolves in the region — AWS publishes
/aws/service/marketplace/<product>/... only to accounts subscribed to that Marketplace product.

Same rules as aws_compile: boto3's default credential chain, no access keys in or out, and every
AWS failure surfaces as AwsError.
"""
from __future__ import annotations

import json
import secrets
from pathlib import Path

from dx_edge.core import aws_compile as ac
from dx_edge.core.aws_compile import AwsError

CFN_DIR = Path(__file__).resolve().parent.parent / "cfn"
TEMPLATES = {
    "compiler": {
        "label": "DEEPX Compiler (Marketplace 2.3.0)",
        "marketplace": "https://aws.amazon.com/marketplace/pp/prodview-ev6ed5omu4ulo",
    },
    "greengrass": {
        "label": "DEEPX Greengrass Solution (Compiler + edge deploy)",
        "marketplace": "https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34",
    },
}
MAX_EVENTS = 10


def _body(template_id: str) -> str:
    return (CFN_DIR / f"{template_id}.json").read_text(encoding="utf-8")


def templates() -> list[dict]:
    return [{"id": tid, **meta,
             "ssm": json.loads(_body(tid))["Parameters"]["ImageId"]["Default"]}
            for tid, meta in TEMPLATES.items()]


def _ami(ssm, name: str) -> str | None:
    try:
        return ac._call(ssm.get_parameter, Name=name)["Parameter"]["Value"]
    except AwsError as exc:
        if exc.message.startswith("ParameterNotFound"):
            return None
        raise


def subscription(profile: str, region: str) -> list[dict]:
    ac._boto3()
    ac._check(profile, region)
    ssm = ac._client("ssm", profile, region)
    rows = []
    for t in templates():
        ami = _ami(ssm, t["ssm"])
        rows.append({**t, "subscribed": ami is not None, "ami_id": ami})
    return rows


def _bucket_name(stack: str) -> str:
    # The stack name is letters, digits and hyphens starting with a letter, so lowercased it is a
    # valid S3 name; 54 + "-" + 8 hex = 63, the S3 maximum.
    return f"{stack.lower()[:54].rstrip('-')}-{secrets.token_hex(4)}"


def _default_network(profile: str, region: str) -> tuple[str, str]:
    ec2 = ac._client("ec2", profile, region)
    vpcs = ac._call(ec2.describe_vpcs, Filters=[{"Name": "isDefault", "Values": ["true"]}])["Vpcs"]
    if not vpcs:
        raise AwsError(400, f"No default VPC in {region} — create one (VPC console → Create default VPC)")
    vpc = vpcs[0]["VpcId"]
    subnets = ac._call(ec2.describe_subnets, Filters=[
        {"Name": "vpc-id", "Values": [vpc]},
        {"Name": "default-for-az", "Values": ["true"]},
    ])["Subnets"]
    if not subnets:
        raise AwsError(400, f"Default VPC {vpc} has no default subnet")
    return vpc, subnets[0]["SubnetId"]


def create_stack(profile: str, region: str, template: str, name: str) -> dict:
    """Start creating a stack from a vendored template on the default VPC; returns at once."""
    ac._boto3()
    if template not in TEMPLATES:
        raise AwsError(400, "Unknown template")
    ac._check(profile, region, name)
    body = _body(template)
    ssm_name = json.loads(body)["Parameters"]["ImageId"]["Default"]
    if _ami(ac._client("ssm", profile, region), ssm_name) is None:
        raise AwsError(400, f"Not subscribed to the AWS Marketplace product for this template in {region}")
    vpc, subnet = _default_network(profile, region)
    bucket = _bucket_name(name)
    cf = ac._client("cloudformation", profile, region)
    ac._call(
        cf.create_stack,
        StackName=name,
        TemplateBody=body,
        Parameters=[
            {"ParameterKey": "ModelBucketName", "ParameterValue": bucket},
            {"ParameterKey": "VpcId", "ParameterValue": vpc},
            {"ParameterKey": "SubnetId", "ParameterValue": subnet},
        ],
        Capabilities=["CAPABILITY_IAM"],
        Tags=[{"Key": "ManagedBy", "Value": "dx-ai-studio"}, {"Key": "Template", "Value": template}],
    )
    return {"name": name, "bucket": bucket, "template": template}


def stack_progress(profile: str, region: str, name: str) -> dict:
    """Stack status and its newest events (describe_stack_events is newest-first)."""
    ac._boto3()
    ac._check(profile, region, name)
    cf = ac._client("cloudformation", profile, region)
    try:
        stack = ac._call(cf.describe_stacks, StackName=name)["Stacks"][0]
    except AwsError as exc:
        # describe_stacks by name stops finding a stack once its deletion completes.
        if "does not exist" in exc.message:
            return {"name": name, "status": "DELETE_COMPLETE", "events": []}
        raise
    # ponytail: first page of events only; the UI shows the newest few.
    events = ac._call(cf.describe_stack_events, StackName=name)["StackEvents"][:MAX_EVENTS]
    return {
        "name": name,
        "status": stack["StackStatus"],
        "events": [{
            "resource": e.get("LogicalResourceId", ""),
            "status": e.get("ResourceStatus", ""),
            "reason": e.get("ResourceStatusReason", ""),
            "time": e["Timestamp"].isoformat(),
        } for e in events],
    }


def delete_stack(profile: str, region: str, name: str, confirm: str) -> dict:
    """Delete a compiler stack (ready, or one this page created that is not mid-operation) once the
    caller typed its exact name. The bucket is retained."""
    if not name or confirm != name:
        raise AwsError(400, "Type the stack name exactly to confirm deletion")
    ac._boto3()
    ac._check(profile, region, name)
    cf = ac._client("cloudformation", profile, region)
    row = ac.stack_row(ac._call(cf.describe_stacks, StackName=name)["Stacks"][0])
    if not row:
        raise AwsError(400, "Not a DEEPX Compiler stack")
    if not row["deletable"]:
        raise AwsError(400, f"Stack is {row['status']} — wait until it finishes")
    bucket = row["bucket"]
    ac._call(cf.delete_stack, StackName=name)
    return {"name": name, "status": "DELETE_IN_PROGRESS", "bucket": bucket, "bucket_retained": True}

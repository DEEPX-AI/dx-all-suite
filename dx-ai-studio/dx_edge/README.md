# DX Cloud

DEEPX on AWS from Studio: account connection, separate Compiler/Greengrass Marketplace
checks, CloudFormation stack create/select/progress/delete, **Cloud Compile**
(ONNX → `.dxnn`), and Greengrass device/component status and registration scripts.
Open `/cloud/` in Studio. `dx_edge` is the internal package name, not the suite's
separate `dx-edge` product or DX EdgeGuide recommendation tool. User manual:
[docs/source/13_DX_Edge_AWS.md](../docs/source/13_DX_Edge_AWS.md).

## Requirements and connection

The base Studio web runtime is Python 3.8+ with no mandatory third-party packages.
Actual AWS API calls need optional `boto3` in the Studio Python environment:

```bash
# From dx-ai-studio/ in the environment used to launch Studio
python3 -m pip install -e '.[aws]'
# For an SSO profile already configured on this host
aws sso login --profile <name>
aws sts get-caller-identity --profile <name>
```

Without boto3 the page/guide load, but AWS operations do not run. AWS CLI is a
setup/SSO helper; the backend uses boto3, not CLI subprocesses. Credentials come from
the **Studio host's** boto3 credential chain, optionally a named profile; there is no
access-key entry, upload or storage UI. Select that profile/region and **Check
connection**; renew expired SSO on the host and check again. Region follows the
profile initially, falling back to `ap-northeast-2`.

## Example workflow

1. Choose a product tab, accept that product's Marketplace terms as an account admin,
   then refresh its subscription status. Studio checks the template AMI's SSM
   parameter in the selected region; this is not a billing or universal availability
   guarantee.
2. Select an existing ready compatible stack, or create one and follow its status and
   recent events. Studio creation uses a generated bucket name, the **default VPC /
   first returned default subnet**, other template defaults and `CAPABILITY_IAM`.
   Use a Console-created compatible stack when custom networking/parameters are
   needed. Missing default networking, IAM or subscription errors must be resolved
   before retrying.
3. On **Cloud Compile**, upload ONNX (up to **500 MiB**) and JSON (up to **1 MiB**,
   a JSON **object**). The pair goes to a timestamped model prefix in the bucket read
   from stack outputs; S3 → Lambda → Step Functions runs `dxcom` on EC2.
4. Follow status, **Compile jobs** and **Show log**, or open the AWS Console links.
   Re-select the same stack and refresh jobs after reconnecting. A `.dxnn` marks
   compile success, **not proof of EC2 cleanup**; verify the workflow/instance too.
   No fixed compile duration is guaranteed.
5. **Download .dxnn** downloads through the browser. **Save to Studio models** writes
   into the **server's** DX App models directory (`DX_APP_MODELS_DIR`) and
   **overwrites the same filename**. It does not save on a remote browser host or
   deploy to a device.

For Greengrass, select its stack, inspect **Devices (dx-runtime)** and component
states, then generate/Copy/Download a registration script for a Thing name. Review
and run it yourself on the target device with Java 11+, sudo, network access,
provisioning credentials and runtime prerequisites. Studio does not SSH or execute
the script. Automatic deployment is the stack's `com.deepx.dx-runtime` component,
not automatic model deployment or inference.

## Cost, errors and cleanup

Creating stacks and compiling use real, potentially chargeable AWS resources.
Check CloudFormation events for stack failures and workflow/CloudWatch logs for
compile failures before resubmitting. Identity success alone does not establish all
required service permissions.

Stack deletion requires typing its exact name and waiting for any in-progress
operation to finish. The model S3 bucket is **Retain** (including versions); remove
it separately only after reviewing the data. Review EC2/EBS leftovers, Greengrass
devices/IoT credentials/local software and Marketplace subscriptions separately.
Stack deletion is not a full data, device or billing cleanup.

## Code

- `server.py` — routes only.
- `core/aws_compile.py` — connection, compile jobs/logs/results and input validation.
- `core/aws_stack.py` / `cfn/` — subscription checks and vendored stack lifecycle.
- `core/aws_greengrass.py` — device/component queries and registration script generation.
- Tests: `tests/dx_edge/` (botocore `Stubber`, no network).

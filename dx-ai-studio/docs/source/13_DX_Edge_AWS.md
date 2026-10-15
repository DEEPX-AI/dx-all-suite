# DX Cloud (AWS)

DEEPX on AWS from inside the studio: the two AWS Marketplace products, and a **Cloud
Compile** panel that turns an `.onnx` model into a `.dxnn` on a DEEPX Compiler stack you
have already deployed — no local `dxcom` needed. Open it from the hub tile or with
`Alt`+`9`.

## AWS Marketplace

- **AWS Compiler** — the [DEEPX Compiler Solution](https://aws.amazon.com/marketplace/pp/prodview-ev6ed5omu4ulo)
  runs `dxcom` on an Amazon EC2 instance. Deployed as a CloudFormation stack it becomes an
  event-driven pipeline: an `.onnx` and its `.json` uploaded to the stack's model bucket
  start a Lambda trigger → Step Functions → a compiler instance, which writes the `.dxnn`
  next to them and terminates.
- **AWS Greengrass** — the [DEEPX Greengrass Solution](https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34)
  deploys the NPU driver, firmware, `dx_rt` and `dx_stream` to every device in an IoT Thing
  Group (Zero-Touch Provisioning), with the same compile pipeline in its stack.

The full walkthrough — stack parameters, ZTP checks, cost and cleanup — is in the
[DX-Edge guides](https://github.com/DEEPX-AI/dx-all-suite/blob/main/dx-edge/README.md).

## AWS CLI setup

DX Cloud reads the AWS CLI configuration (`~/.aws`) of the Linux machine that runs the
studio; it never asks for access keys. The same guide is in step ① of the page, with a
copy button on every command.

**1. Install AWS CLI v2.** One script for Linux `x86_64` and `aarch64` — it picks the
package for this machine (install `unzip` and `curl` first if they are missing:
`sudo apt install -y unzip curl`):

```bash
ARCH="$(uname -m)"   # x86_64 or aarch64
case "$ARCH" in
  x86_64|aarch64)
    curl "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" -o awscliv2.zip
    unzip -q awscliv2.zip
    sudo ./aws/install --update
    aws --version ;;
  *) echo "AWS CLI v2 for Linux supports x86_64 and aarch64 only (this machine: $ARCH)" ;;
esac
```

See the [AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

**2. Configure credentials** ([AWS CLI configuration guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)).

- *Option A — access key:* create one in the IAM console (Users → Security credentials →
  Create access key), then run `aws configure`:

    ```text
    $ aws configure
    AWS Access Key ID [None]: AKIA****************
    AWS Secret Access Key [None]: ****************************************
    Default region name [None]: ap-northeast-2
    Default output format [None]: json
    ```

- *Option B — IAM Identity Center (SSO):* `aws configure sso` once to create a named
  profile, then `aws sso login --profile <name>` whenever the session expires.

**3. Verify** with `aws sts get-caller-identity`.

**4. Permissions.** The identity needs CloudFormation, S3, Step Functions, SSM
`GetParameter`, EC2, IAM (stacks are created with `CAPABILITY_IAM`), CloudWatch Logs and
Lambda; the Greengrass tab also needs Greengrass V2 and IoT. An account admin accepts the
Marketplace subscription.

**5. Check connection.** Press **Check connection** in step ①: the profile list reloads
(no restart needed) and the account and ARN of the credentials appear. If the check fails,
the guide opens with the error.

## Cloud Compile

Step 1. Pick an **AWS profile** and a **region** (default `ap-northeast-2`). DX Cloud uses the
   AWS CLI credentials on this machine (`aws configure` or `aws sso login`); it never asks
   for, stores or returns access keys.  

Step 2. Pick the **compiler stack**. The list shows stacks in `CREATE_COMPLETE` /
   `UPDATE_COMPLETE` whose outputs include `ModelBucketName`. The bucket is always read from
   the stack on the studio side.  

Step 3. Choose the **ONNX model** and its **compile config (.json)** and press **Upload and
   compile**. Both go to a fresh prefix `models/<model>-<YYYYmmdd-HHMMSS>/`, so configs of
   different models never mix.  

Step 4. Wait. The panel polls every 15 s and shows *pending* → *running* → *succeeded* /
   *failed*; a compile usually takes 10–15 minutes and the panel keeps polling. Links open the
   Step Functions execution, the CloudWatch log group `/dx-compiler/<stack-name>/execution`
   and the S3 folder.  

Step 5. **Download .dxnn**, or **Save to Studio models** — that writes it into the models
   directory DX App uses (`DX_APP_MODELS_DIR`, default `dx-runtime/dx_app/assets/models`).  

!!! note "boto3"
    Cloud Compile needs `boto3` (`pip install boto3`, or `pip install -e '.[aws]'`). Without
    it the page still loads, shows the Marketplace cards and an install hint; the rest of
    the studio does not need it.

!!! note "Related"
    To compile locally instead, see **[DX Compiler](04_DX_Compiler.md)**.

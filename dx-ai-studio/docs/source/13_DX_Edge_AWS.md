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

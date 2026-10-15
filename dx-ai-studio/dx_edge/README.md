# DX Cloud

DEEPX on AWS: links to the two AWS Marketplace products (DEEPX Compiler Solution, DEEPX
Greengrass Solution) and **Cloud Compile** — ONNX → `.dxnn` on a DEEPX Compiler
CloudFormation stack you have already deployed. User manual:
[docs/source/13_DX_Edge_AWS.md](../docs/source/13_DX_Edge_AWS.md).

## How cloud compile works

1. `GET /api/aws/stacks` lists `CREATE_COMPLETE` / `UPDATE_COMPLETE` stacks whose outputs
   include `ModelBucketName`.
2. `POST /api/aws/compile` (multipart: `onnx`, `json`, `profile`, `region`, `stack`)
   uploads both files to `models/<stem>-<YYYYmmdd-HHMMSS>/` in the bucket read from the
   stack outputs — the client never names a bucket. The stack's Lambda trigger starts
   Step Functions (`StateMachineArn`), which runs `dxcom` on EC2 and writes
   `<stem>.dxnn` to the same prefix.
3. `GET /api/aws/compile/status` reports `pending` → `running` → `succeeded` / `failed`.
   Done = the `.dxnn` exists; otherwise the execution named `dx-compile-<stem>-<hash>`
   started after the upload decides. Console links: the execution, the CloudWatch log group
   `/dx-compiler/<stack>/execution`, the S3 prefix.
4. `GET /api/aws/compile/download` streams the `.dxnn`; `POST /api/aws/compile/save`
   writes it into the DX App models directory (`DX_APP_MODELS_DIR`).

`GET /api/aws/status` reports whether `boto3` is installed, the profile names in
`~/.aws`, and the default region `ap-northeast-2`.

## Credentials

boto3's default chain, optionally narrowed to a named profile. The server never accepts,
stores, logs or returns an access key. `boto3` is an optional extra
(`pip install -e '.[aws]'`); without it the page still loads and shows an install hint.

## Code

- `server.py` — routes only.
- `core/aws_compile.py` — all AWS calls and input validation (region, stack name, job
  prefix, file types and sizes).
- Tests: `tests/dx_edge/` (botocore `Stubber`, no network).

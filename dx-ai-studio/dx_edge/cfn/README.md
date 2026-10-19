# Vendored CloudFormation templates

`dx_edge/core/aws_stack.py` sends these as `TemplateBody` when DX Cloud creates a stack.
They are compact JSON, not YAML: Studio's base runtime needs no PyYAML, and the
Greengrass YAML (~57 KB) is over the 51,200-byte `TemplateBody` limit while its compact JSON fits.

| File | Source |
|---|---|
| `compiler.json` | `deepx-sangminkang/dx-compiler-aws-poc` @ 87aa8ed, `dx-compiler-marketplace-v2.yaml` (DEEPX Compiler, Marketplace 2.3.0, product `prod-ei6ws54bjw7to`) |
| `greengrass.json` | `aws cloudformation get-template --stack-name greengrassstacktest1` (DEEPX Greengrass Solution, product `prod-w3itlxbo76pdo`) |

## Deployment behavior and limits

- The public Studio module is **DX Cloud**, at `/cloud/`; `dx_edge` is its package
  name. AWS operations require optional boto3 and the Studio host's credential
  chain/profile. AWS CLI is not the backend execution mechanism.
- For example, choose the Greengrass product, refresh subscription status, enter a
  new stack name and create it in Studio. `aws_stack.py` supplies `ModelBucketName`,
  the default VPC and the first returned default subnet, and requests
  `CAPABILITY_IAM`. All other parameters use template defaults, including
  `InstanceType: t3.xlarge`. The UI does not accept custom VPC/subnet/instance values;
  use the AWS Console path when those are required.
- The subscription probe resolves each template's `ImageId` SSM parameter. The
  vendored Compiler label is 2.3.0; Greengrass uses a version-specific staging SSM
  path. Neither the probe nor older Console screenshots prove current Marketplace
  version/region availability. Confirm in the deployment account before use.
- The Greengrass template **creates** an `AWS::IoT::ThingGroup`: blank
  `ThingGroupName` derives `<stack-name>-cores`; a supplied name names the new
  resource, **not an imported existing group**. A conflicting existing name can
  fail creation.
- Its `com.deepx.dx-runtime` recipe installs the driver package, extracts `dx_rt`
  and runs `./install.sh --all` then `./build.sh`, updates firmware with
  `/usr/local/bin/dxrt-cli -u fw.bin`, and builds `dx_stream` using `./install.sh`
  (no `--all`) then `./build.sh`. Existing-target checks can skip work. This deploys
  runtime software, not the compiled model or an inference job.
- Studio generates a device registration script for manual execution on the device;
  it does not run it over SSH. Check device prerequisites and Greengrass component
  lifecycle states after running it.
- Both model buckets have `DeletionPolicy: Retain` and
  `UpdateReplacePolicy: Retain`, with versioning enabled. Stack deletion leaves
  data/versions to review and remove separately. The Greengrass Thing Group has no
  Retain policy; deletion attempts to remove the group and can require clearing
  membership first. It does not uninstall local device software or cancel
  Marketplace subscriptions.
- Stack creation/compile can incur charges. A `.dxnn` in S3 is separate from a
  completed EC2 termination step; inspect workflow events and leftover resources
  after failures.

## Regenerate

The templates are vendored artifacts; change their source and regenerate rather
than hand-editing them. Run in a separate dev environment with PyYAML
(`python3 -m pip install pyyaml`); this is conversion tooling, not a Studio runtime
requirement. CloudFormation short tags become their long JSON forms:

```python
import json, sys, yaml

class Loader(yaml.SafeLoader):
    pass

def _tag(loader, suffix, node):
    name = "Ref" if suffix == "Ref" else f"Fn::{suffix}"
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
        if suffix == "GetAtt":
            value = value.split(".", 1)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node, deep=True)
    else:
        value = loader.construct_mapping(node, deep=True)
    return {name: value}

Loader.add_multi_constructor("!", _tag)
src, dst = sys.argv[1:3]
with open(src, encoding="utf-8") as f:
    doc = yaml.load(f, Loader=Loader)
with open(dst, "w", encoding="utf-8") as f:
    f.write(json.dumps(doc, separators=(",", ":"), ensure_ascii=False))
```

`python convert.py dx-compiler-marketplace-v2.yaml compiler.json` — then
`pytest tests/dx_edge/test_aws_stack.py` checks the size limit and required parameters.

# Vendored CloudFormation templates

`dx_edge/core/aws_stack.py` sends these as `TemplateBody` when DX Cloud creates a stack.
They are compact JSON, not YAML: Studio has no runtime dependencies (no PyYAML), and the
Greengrass YAML (~57 KB) is over the 51,200-byte `TemplateBody` limit while its compact JSON fits.

| File | Source |
|---|---|
| `compiler.json` | `deepx-sangminkang/dx-compiler-aws-poc` @ 87aa8ed, `dx-compiler-marketplace-v2.yaml` (DEEPX Compiler, Marketplace 2.3.0, product `prod-ei6ws54bjw7to`) |
| `greengrass.json` | `aws cloudformation get-template --stack-name greengrassstacktest1` (DEEPX Greengrass Solution, product `prod-w3itlxbo76pdo`) |

## Regenerate

Run in a dev environment with PyYAML (`pip install pyyaml`); CloudFormation short tags become
their long JSON forms:

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

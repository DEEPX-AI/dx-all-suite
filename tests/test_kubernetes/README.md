# Kubernetes Tests

Two suites that fail when the Kubernetes docs stop working as written. They read commands,
jq expressions, and paths out of the docs instead of keeping their own copy.

| Suite | Marker | Needs | Time |
|---|---|---|---|
| `test_k8s_static.py` | `kubernetes_static` | helm, jq, git, and network once to fetch the NFD subchart. No cluster or NPU | seconds |
| `test_k8s_acceptance.py` | `kubernetes` | a DX-M1 node; for the full flow a clean OS with internet and passwordless sudo | ~2 min re-run; first QA run 20–60 min (driver + image builds) |

## Acceptance test (QA)

On a clean OS with a DX-M1, internet, and passwordless sudo, after cloning with submodules:

```bash
git clone --recurse-submodules <dx-all-suite> && cd dx-all-suite
pip install -r tests/requirements.txt
DX_K8S_QA=1 python3 -m pytest tests/test_kubernetes/test_k8s_acceptance.py -m kubernetes -v -rsw
```

This follows the Quickstart from step 0:

| Test | Doc | What happens |
|---|---|---|
| `q0` | Quickstart step 0 | runs the step-0 block: k3s, kubeconfig, helm, jq |
| `q1` | step 1 | runs the step-1 block (`install.sh --runtime-only`) if `dxcli -s` lists no card. If it still lists none, warns and continues |
| `q2` | step 2 | containerd 2.x (CDI on by default), or CDI enabled in the 1.7 template |
| `q3a` | — | images the chart and samples use: present in k3s → pull → **build locally under the same name and import**. Builds are needed until the images are published on ghcr |
| `q3` | Install | runs the Install block (`helm install …`). If the OCI chart is unreachable, installs the checkout's chart and warns |
| `a1`–`a8` | Verify, Run a workload, Beginner Guide ex. 1–6 | allocatable, labels, smoke pod, no request → no device, too many → Pending, firmware nodeSelector, inference FPS, plugin metrics |
| `a9` | Beginner Guide ex. 7 | deletes the plugin pod and waits for recovery |
| `a10` | Beginner Guide ex. 8 | runs the guide's PromQL; skipped without Prometheus (the docs do not install it) |
| `qz` | — | `helm uninstall` if `q3` installed it (k3s stays) |

Every step skips what is already done, so a re-run resumes where the last one stopped.

Without `DX_K8S_QA=1` the destructive and slow steps (`q0`, `q1` install, `q3a`, `q3`, `a9`, `qz`)
are skipped and the rest runs against a cluster that already has `dx-npu` installed.

## Static checks

```bash
python3 -m pytest tests/test_kubernetes/test_k8s_static.py -m kubernetes_static -v
```

Chart lint and render scenarios (NFD on/off, image tag, version label, PCI match), a fresh checkout
rendering after the deploy README's `helm dependency build` steps, sample and dashboard sanity, every `kubectl get node -o json | jq` in the docs run
against a recorded one-node List (`fixtures/node-list.json`), and every doc path and link.

The NFD subchart is gitignored, so render tests first run the deploy README's checkout steps
(`helm repo add` + `helm dependency build`). Without network they skip, or fail under
`DX_K8S_REQUIRE_TOOLS=1`. A docker `DX_K8S_HELM_CMD` does not keep `helm repo add` between
calls, so use a native helm for the first run.

## Environment variables

| Var | Default | Effect |
|---|---|---|
| `DX_K8S_QA` | unset | `1` enables the destructive/slow steps |
| `DX_K8S_KEEP` | unset | `1` makes `qz` keep the release |
| `DX_K8S_REQUIRE_TOOLS` | unset | `1` turns a missing tool from skip into failure |
| `DX_K8S_HELM_CMD` | `helm` | helm command, e.g. a docker wrapper mounting the repo and `/tmp` at the same paths |
| `DX_K8S_CHART_SOURCE` | `auto` | `oci`, `checkout`, or `auto` (OCI if reachable) |
| `DX_K8S_IMAGES` | `auto` | `pull` never builds images |
| `DX_K8S_PLUGIN_IMAGE` | chart default | plugin image to install and prepare |
| `DX_K8S_RUNTIME_IMAGE` | inference-pod image | runtime image for `a7` |
| `DX_K8S_MODEL_DIR` | unset | `a7` mounts this host dir as the models dir instead of downloading |

Workloads run in the namespace `dx-k8s-acceptance`, created and deleted by the suite.

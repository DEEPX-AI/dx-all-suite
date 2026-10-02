# DX-M1 on Kubernetes (k3s)

Enables scheduling DEEPX DX-M1 NPUs on k3s. The device plugin itself lives in the
[`dx-k8s-device-plugin`](../../dx-k8s-device-plugin) submodule; this dir holds the
`dx-npu` Helm chart, the NFD labeling rule, and sample workloads.

## Architecture

```
host (per NPU node)          k3s cluster
─────────────────────        ─────────────────────────────────────────
dx-runtime/install.sh   ──►  driver (dxrt-driver-dkms) + firmware + dxrtd
containerd CDI enabled       (enable_cdi=true, cdi_spec_dirs incl /etc/cdi)

Helm: dx-npu ──► NodeFeatureRule (PCI 1ff4 → deepx.ai/dx-m1.present)
              └► device-plugin DaemonSet → advertises deepx.ai/dx-m1
                   ├─ writes /etc/cdi/deepx.json  (device nodes + host libs)
                   └─ Allocate → CDI ref deepx.ai/dx-m1=<id>
Pod requests deepx.ai/dx-m1: 1 → containerd injects /dev/dxrtN + libs
```

## Prerequisites

1. **Each NPU node** — host driver + firmware + runtime:
   ```bash
   cd dx-runtime && ./install.sh --runtime-only
   dxcli -s   # must list the NPU(s)
   ```
2. **containerd CDI** — on by default in containerd 2.x (`sudo k3s ctr version` → v2.x,
   nothing to do). containerd 1.7 needs it enabled; on k3s, copy the generated
   `config.toml` to `config.toml.tmpl` and append the CDI block — a template holding only
   the CDI lines replaces k3s's whole containerd config. Exact steps:
   [Quickstart, step 2](../../docs/source/06_Kubernetes_Quickstart.md#prerequisites).
3. **NFD** — node-feature-discovery in the cluster (set `nfd.enabled=true` to let this
   chart pull it in, or install separately). Required for the NodeFeatureRule.

## Install

From the published OCI chart (CI pushes on every chart change):

```bash
helm install dx-npu oci://ghcr.io/deepx-ai/charts/dx-npu -n dx-system --create-namespace
```

Or from this checkout. The NFD subchart is not committed, and Helm checks every declared
dependency even with `nfd.enabled=false`, so fetch it first (needs network once):

```bash
helm repo add node-feature-discovery https://kubernetes-sigs.github.io/node-feature-discovery/charts
helm dependency build ./charts/dx-npu
helm install dx-npu ./charts/dx-npu -n dx-system --create-namespace
```

Verify:

```bash
kubectl get node -o json | jq '.items[].status.allocatable' | grep deepx.ai/dx-m1
kubectl apply -f samples/test-pod.yaml && kubectl logs -f dx-m1-test
```

## Key values

| Value | Default | Purpose |
|---|---|---|
| `resourceName` | `deepx.ai/dx-m1` | advertised extended resource |
| `devicePlugin.image.tag` | `""` (= chart `appVersion`) | plugin image tag (ghcr) |
| `devicePlugin.nodeSelectorLabel` | `deepx.ai/dx-m1.present` | NFD gate |
| `nodeFeatureRule.enabled` | `true` | apply the PCI 1ff4 label rule |
| `nfd.enabled` | `false` | also deploy node-feature-discovery (chart dependency) |
| `metrics.enabled` | `true` | serve `deepx_npu_*` on `:9400` + headless Service |
| `metrics.serviceMonitor.enabled` | `false` | Prometheus-operator ServiceMonitor |

## NFD

The chart declares `node-feature-discovery` as an optional dependency (`condition:
nfd.enabled`). To deploy NFD with the chart, add `--set nfd.enabled=true` (from a checkout,
after the `helm dependency build` step above):

```bash
helm install dx-npu ./charts/dx-npu -n dx-system --create-namespace --set nfd.enabled=true
```

Without NFD the chart still installs but skips the NodeFeatureRule, so label NPU nodes
yourself (below). If the cluster already runs NFD, leave `nfd.enabled=false` — only the NodeFeatureRule
is applied. Without any NFD, label nodes manually:
`kubectl label node <n> deepx.ai/dx-m1.present=true`.

## Metrics

The device plugin serves Prometheus metrics in-process on `:9400/metrics`:
`deepx_npu_up`, `deepx_npu_device_healthy`, and per-core
`deepx_npu_core_{temperature_celsius,voltage_millivolts,clock_mhz}`. A headless
Service (`<release>-metrics`) exposes them; enable `metrics.serviceMonitor.enabled`
with prometheus-operator present.

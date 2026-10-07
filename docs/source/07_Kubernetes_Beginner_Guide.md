# Kubernetes Beginner Guide — Learning with the DX-M1 NPU

This guide is for people who have never used Kubernetes. Each idea is first explained with a
**kindergarten classroom**, then checked with real commands.

If you only need installation steps, see the [Kubernetes Quickstart](06_Kubernetes_Quickstart.md).

---

## Part 1. The picture

### Imagine a kindergarten

```
Kindergarten (Cluster)
│
├─ Head teacher (Scheduler)        "Which classroom should this child go to?"
│
├─ Classroom A (Node)              door sign: 1 special block
│    ├─ Class monitor (Device Plugin)
│    ├─ Special block (DX-M1) 🧩
│    └─ Child (Pod) 🙋
│
└─ Classroom B (Node)              door sign: no special block
     └─ Child (Pod) 🙂
```

| In the kindergarten | In Kubernetes | What it does |
|---|---|---|
| The whole kindergarten | **Cluster** | Several computers used as one |
| A classroom | **Node** | One computer |
| A child | **Pod** | One running program (a box around containers) |
| The head teacher | **Scheduler** | Decides which classroom each child goes to |
| A special block | **DX-M1 NPU** | A card that runs AI inference fast |

### A child raises a hand: "Can I have a special block?"

To play with a special block, a child must **raise a hand**. In the Pod's YAML that looks like:

```yaml
resources:
  limits:
    deepx.ai/dx-m1: 1     # "One special block, please!"
```

The head teacher only sends that child to a classroom **that still has a free block**.
Never to classroom B, which has none.

### How does the head teacher know where the blocks are?

On their own, they don't. A few helpers make it work.

**🧑‍🏫 Class monitor = Device Plugin** (`dx-k8s-device-plugin`)

Every classroom with a block has one class monitor, who keeps reporting to the head teacher:
"We have 1 special block, and it works!"

If the block breaks, the monitor reports it right away and the head teacher stops sending
children there. The rule that puts exactly one monitor in every block classroom is called a
**DaemonSet**.

**🏷️ Door sign = NFD (Node Feature Discovery) label**

A sign on the classroom door: "Special block · 1 · version v2.7.6". A child (or a parent) can
ask to go only to classrooms whose sign says v2.7.6. That is a **nodeSelector**.

**🚚 Delivery helper = CDI (Container Device Interface)**

When a child enters the classroom, the helper puts the block and its **instruction booklet**
(driver libraries) right on the child's desk. The child doesn't pack anything. That is why a
container image can use the NPU without the DEEPX runtime baked in.

**📦 Classroom setup box = Helm chart** (`dx-npu`)

Installing the monitors, door-sign rules, and health log one by one is tedious, so they all
come in one box. Open it once (`helm install`) and every classroom is ready.

**🩺 School nurse = Prometheus**, **📊 Notice board = Grafana**

Every 30 seconds the nurse records each block's temperature, pulse (clock), and health.
The notice board draws those records as graphs. If a block was sick overnight, one look at the
board in the morning tells you.

### One page summary

```
Child (Pod) raises a hand     "deepx.ai/dx-m1: 1, please"
        │
        ▼
Head teacher (Scheduler)      reads the monitors' reports, picks a classroom with a free block
        │                     (can also pick by door sign / version)
        ▼
Delivery helper (CDI)         puts /dev/dxrt0 + runtime libraries + dxcli on the desk
        │
        ▼
Child plays with the block    AI inference runs
        │
        ▼
Nurse (Prometheus)            records temperature and health → graphs on the board (Grafana)
```

### Three rules to remember

1. **No raised hand, no block.** A Pod that does not request `deepx.ai/dx-m1` gets no NPU.
2. **One block, one child.** A card belongs to one Pod at a time. Others wait in line (`Pending`).
3. **No monitor, no block.** If the device plugin stops, the block disappears from the head teacher's view.

---

## Part 2. Try it yourself

These examples were run on a k3s node with a DX-M1 installed. They assume the `dx-npu` chart is
already installed. If not, follow the [Quickstart](06_Kubernetes_Quickstart.md) from
**step 0 (installing k3s, kubectl, helm)**.

> If output looks summarized, prefix `kubectl logs` with `rtk proxy` to see the raw text
> (only relevant where rtk is installed).

### Example 1. Does our classroom have a block?

```bash
kubectl get node -o json | jq '.items[].status.allocatable | with_entries(select(.key|test("deepx")))'
```
```json
{ "deepx.ai/dx-m1": "1" }
```
The head teacher knows this classroom has one special block.

And the door sign:
```bash
kubectl get node -o json | jq '.items[].metadata.labels | with_entries(select(.key|test("deepx")))'
```
```json
{
  "deepx.ai/dx-m1.count": "1",
  "deepx.ai/dx-m1.driver-version": "v2.5.1",
  "deepx.ai/dx-m1.fw-version": "v2.7.6",
  "deepx.ai/dx-m1.pcie-driver-version": "v2.4.1",
  "deepx.ai/dx-m1.present": "true",
  "deepx.ai/dx-m1.product": "M1"
}
```

### Example 2. Raise a hand, get a block

```bash
kubectl apply -f deploy/k8s/samples/test-pod.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Running pod/dx-m1-test --timeout=120s
kubectl logs dx-m1-test
```
```
=== /dev/dxrt* ===
crw-rw-rw- 1 root root 507, 0 ... /dev/dxrt0
=== dxcli -s ===
DXRT v3.4.2
 * Device 0: M1, Accelerator type
 ...
NPU 0: voltage 750 mV, clock 1000 MHz, temperature 43'C
```
This Pod is plain `ubuntu:24.04` with no DEEPX software, yet the block (`/dev/dxrt0`) and
`dxcli` are inside. The **delivery helper (CDI)** brought them.

```bash
kubectl delete pod dx-m1-test
```

### Example 3. What if you don't raise a hand?

Same Pod, minus the `deepx.ai/dx-m1: 1` line:

```bash
sed '/deepx.ai\/dx-m1: 1/d; /resources:/d; /limits:/d' deploy/k8s/samples/test-pod.yaml \
  | sed 's/name: dx-m1-test/name: dx-m1-norequest/' | kubectl apply -f -
kubectl wait --for=jsonpath='{.status.phase}'=Running pod/dx-m1-norequest --timeout=120s
kubectl logs dx-m1-norequest
```
```
=== /dev/dxrt* ===
no NPU injected
```
That's **rule 1**: no raised hand, no block.

```bash
kubectl delete pod dx-m1-norequest
```

### Example 4. Asking for more blocks than exist

The classroom has one block; ask for two.

```bash
kubectl run greedy --image=ubuntu:24.04 --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"greedy","image":"ubuntu:24.04","command":["sleep","60"],"resources":{"limits":{"deepx.ai/dx-m1":"2"}}}]}}'
kubectl get pod greedy
kubectl describe pod greedy | tail -3
```
```
NAME     READY   STATUS    RESTARTS   AGE
greedy   0/1     Pending   0          8s

0/1 nodes are available: 1 Insufficient deepx.ai/dx-m1.
```
`Pending` means waiting in line; the head teacher says there aren't enough blocks
(`Insufficient`). That's **rule 2**: NPUs are counted and handed out like CPU and memory.

```bash
kubectl delete pod greedy
```

### Example 5. Picking classrooms by version

Use the door sign to choose. Run only on nodes with firmware `v2.7.6`:

```yaml
# fw-pick.yaml
apiVersion: v1
kind: Pod
metadata:
  name: fw-pick
spec:
  restartPolicy: Never
  nodeSelector:
    deepx.ai/dx-m1.fw-version: "v2.7.6"   # only classrooms with this sign
  containers:
    - name: c
      image: ubuntu:24.04
      command: ["sleep", "30"]
      resources:
        limits:
          deepx.ai/dx-m1: 1
```
```bash
kubectl apply -f fw-pick.yaml
kubectl get pod fw-pick          # → ContainerCreating / Running
```
Change the version to something that doesn't exist, like `"v9.9.9"`:
```
0/1 nodes are available: 1 node(s) didn't match Pod's node affinity/selector.
```
No classroom has that sign, so the Pod stays `Pending`. With many nodes on mixed firmware, this
is how you place **a model validated only on a specific version** safely.

```bash
kubectl delete pod fw-pick
```

### Example 6. Actually playing with the block (AI inference)

```bash
kubectl apply -f deploy/k8s/samples/inference-pod.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Succeeded pod/dx-m1-inference --timeout=300s
kubectl logs dx-m1-inference -c inference | grep -E "NPU Processing|Latency|FPS" | tail -3
```
```
  - NPU Processing Time  : 18.107 ms
  - Latency              : 26.783 ms
  - FPS                  : 34.04
```
This Pod works in two steps:

1. A **prep helper (initContainer)** downloads the model file (YoloV7) first.
2. The child (main container) starts `dxrtd` and runs inference with `dxrun`, which reports the speed.

> Why start `dxrtd` inside the Pod? The DEEPX runtime talks to its helper program (`dxrtd`)
> over a socket that doesn't leave the container, so each Pod runs its own. The card belongs to
> that Pod alone, so they never collide.

> If the image isn't in a registry yet, build and import it locally first. The steps are in the
> header comment of `deploy/k8s/samples/inference-pod.yaml`.

```bash
kubectl delete pod dx-m1-inference
```

### Example 7. When the class monitor steps out

```bash
kubectl delete pod -n dx-system -l app.kubernetes.io/component=device-plugin
kubectl get node -o json | jq '.items[].status.allocatable["deepx.ai/dx-m1"]'
```
It briefly reads `"0"`: with no monitor, the block vanishes from the head teacher's view
(**rule 3**). Within seconds the DaemonSet brings a new monitor and it's back to `"1"`.

Note the door signs (labels) stay put. NFD owns the signs and the monitor owns the block count,
so they move independently.

### Example 8. Reading the nurse's log

With Prometheus installed:

```bash
kubectl port-forward -n monitoring svc/kps-kube-prometheus-stack-prometheus 9090:9090
```
Open `http://localhost:9090`, type into the search box, press **Execute**:

| Question | Type this |
|---|---|
| Is the block healthy? (1 = healthy) | `deepx_npu_device_healthy` |
| Temperature per core? | `deepx_npu_core_temperature_celsius` |
| Blocks available to hand out now? | `kube_node_status_allocatable{resource="deepx_ai_dx_m1"}` |
| Hottest core? | `max(deepx_npu_core_temperature_celsius)` |

The **Graph** tab shows how it changed over time. A Grafana dashboard lives at
`deploy/k8s/dashboards/dx-npu.json`; paste it into Grafana under **Dashboards → New → Import**.

---

## Part 3. Common snags

| If this happens | In kindergarten terms | Check |
|---|---|---|
| Pod stuck in `Pending` | All blocks taken, or no classroom has the sign you asked for | Events at the bottom of `kubectl describe pod <name>` |
| allocatable is `0` | No monitor, or the block was reported sick | `kubectl get pods -n dx-system`, `deepx_npu_device_healthy` |
| No `/dev/dxrt0` inside the Pod | The delivery helper (CDI) didn't run | containerd CDI setup ([Quickstart](06_Kubernetes_Quickstart.md) step 2) |
| `ImagePullBackOff` | The child can't find their bag (image) | Image name, whether it's published, whether it was imported locally |
| `dxrt service is not running` | The block helper (`dxrtd`) wasn't started | Run `dxrtd &` first in the Pod command |
| `GLIBC_2.38 not found` | The desk is too old to read the booklet | Use `ubuntu:24.04` or newer as the Pod image |

---

## Glossary

| Term | One line |
|---|---|
| **Cluster** | Several computers used as one |
| **Node** | One computer in it |
| **Pod** | The unit that runs; a box around one or more containers |
| **Container** | A portable bag holding a program and its files |
| **Scheduler** | Decides which Node a Pod goes to |
| **DaemonSet** | Rule for running "one on every matching Node" |
| **Device Plugin** | Program that tells Kubernetes about special hardware (the NPU) |
| **Extended Resource** | A resource beyond CPU and memory; here `deepx.ai/dx-m1` |
| **Label / nodeSelector** | A Node's door sign / choosing Nodes by that sign |
| **NFD** | Inspects Node hardware and puts up door signs automatically |
| **CDI** | Standard rule for putting devices and files into containers |
| **initContainer** | A prep container that runs before the main one |
| **Helm / Chart** | Kubernetes installer / one install box |
| **Prometheus / Grafana** | Number logbook / the board that draws it |
| **Pending** | Waiting because there is nowhere to place it |

"""Tier 3 — follow the Kubernetes Quickstart and Beginner Guide on a DX-M1 node.

QA run (clean OS, internet, DX-M1, passwordless sudo) — the whole Quickstart from step 0:

    DX_K8S_QA=1 pytest tests/test_kubernetes/test_k8s_acceptance.py -m kubernetes -v

Without DX_K8S_QA only the non-destructive checks run, against a cluster that already
has dx-npu installed. Steps are idempotent, so a re-run resumes where the last one stopped.

Q0, Q1, and Q3 execute the literal bash blocks of those Quickstart sections; workloads use
the sample manifests the docs point to. Env vars: see tests/test_kubernetes/README.md.
"""

import os
import re
import sys
import urllib.parse
import warnings
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from k8s_helpers import (  # noqa: E402
    CHART_DIR, QA, QUICKSTART, REPO_ROOT, RESOURCE, SAMPLES_DIR,
    _docker, _sudo_prefix, allocatable, doc_block, ensure_chart_deps, ensure_image, helm_cmd, kubectl,
    kubectl_json, need, npu_node, run, unschedulable_reason, wait_pod, wait_until,
)

pytestmark = pytest.mark.kubernetes

GUIDE = REPO_ROOT / "docs" / "source" / "07_Kubernetes_Beginner_Guide.md"
NS = "dx-k8s-acceptance"
RELEASE, RELEASE_NS = "dx-npu", "dx-system"
OCI_CHART = re.compile(r"oci://\S+/dx-npu")
STATE = {"installed_by_test": False}

qa_only = pytest.mark.skipif(not QA, reason="destructive/slow step; set DX_K8S_QA=1 (QA machine)")


def cluster_up() -> bool:
    return run(["kubectl", "get", "nodes"], check=False, timeout=30).returncode == 0 if _has("kubectl") else False


def _has(tool):
    import shutil
    return shutil.which(tool) is not None


def dxcli_lists_card() -> bool:
    if not _has("dxcli"):
        return False
    r = run(["dxcli", "-s"], check=False, timeout=120)
    return r.returncode == 0 and re.search(r"\* Device \d+:", r.out) is not None


def chart_defaults() -> dict:
    values = yaml.safe_load((CHART_DIR / "values.yaml").read_text())
    app = yaml.safe_load((CHART_DIR / "Chart.yaml").read_text())["appVersion"]
    img = values["devicePlugin"]["image"]
    return {"plugin_image": f"{img['repository']}:{img['tag'] or app}"}


def plugin_image() -> str:
    return os.getenv("DX_K8S_PLUGIN_IMAGE") or chart_defaults()["plugin_image"]


def runtime_image() -> str:
    if os.getenv("DX_K8S_RUNTIME_IMAGE"):
        return os.environ["DX_K8S_RUNTIME_IMAGE"]
    pod = yaml.safe_load((SAMPLES_DIR / "inference-pod.yaml").read_text())
    return pod["spec"]["containers"][0]["image"]


# =========================================================================== Quickstart setup

@qa_only
def test_q0_cluster_tools():
    """Quickstart step 0: k3s (with kubectl), kubeconfig, helm, jq."""
    if cluster_up():
        need("helm")
        need("jq")
        return
    run(doc_block(QUICKSTART, "Cluster tools"), shell=True, timeout=1800)
    wait_until(cluster_up, 300, what="kubectl get nodes")
    wait_until(lambda: "Ready" in kubectl("get", "nodes", "--no-headers", check=False).out, 300,
               what="node Ready")


def test_q1_host_runtime():
    """Quickstart step 1: host driver/firmware/runtime; `dxcli -s` lists the card.
    No reboot wait: if the card is still not listed after installing, warn and go on —
    the scheduling checks below fail on their own if the NPU really is unusable."""
    if dxcli_lists_card():
        return
    if not QA:
        pytest.skip("`dxcli -s` lists no card; DX_K8S_QA=1 runs the step-1 install")
    run(doc_block(QUICKSTART, "Each NPU node"), shell=True, timeout=3600, check=False)
    if not dxcli_lists_card():
        warnings.warn("`dxcli -s` lists no card after step 1; continuing (a reboot may be needed)")


def test_q2_containerd_cdi():
    """Quickstart step 2: containerd 2.x has CDI on by default; 1.7 needs it in the template."""
    if not _has("k3s"):
        pytest.skip("not a k3s node")
    r = run([*_sudo_prefix(), "k3s", "ctr", "version"], check=False, timeout=60)
    if r.returncode != 0:
        pytest.skip(f"cannot run `k3s ctr version` (needs sudo): {r.out[-300:]}")
    major = int(re.search(r"Version:\s+v?(\d+)", r.out).group(1))
    if major >= 2:
        return
    tmpl = Path("/var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl")
    body = run([*_sudo_prefix(), "cat", str(tmpl)], check=False).out
    assert "enable_cdi = true" in body, f"containerd {major}.x needs CDI enabled in {tmpl}"


@qa_only
def test_q3a_images():
    """Images the chart and samples use. Not on ghcr yet, so missing ones are built
    locally under the same name and imported into k3s; once published they are pulled."""
    def build_plugin(ref):
        run([*_docker(), "build", "-t", ref, str(REPO_ROOT / "dx-k8s-device-plugin")], timeout=3600)

    def build_runtime(ref):
        run(["./docker_build.sh", "--target=dx-runtime", "--ubuntu_version=24.04"], timeout=7200)
        run([*_docker(), "tag", "dx-runtime:ubuntu-24.04", ref])

    for ref, build in ((plugin_image(), build_plugin), (runtime_image(), build_runtime)):
        print(f"{ref}: {ensure_image(ref, build)}")


@qa_only
def test_q3_install():
    """Quickstart Install: the documented `helm install`, then plugin up and labels in."""
    if run([*helm_cmd(), "status", RELEASE, "-n", RELEASE_NS], check=False).returncode == 0:
        return
    block = doc_block(QUICKSTART, "Install").rstrip()
    oci = OCI_CHART.search(block).group(0)
    source = os.getenv("DX_K8S_CHART_SOURCE", "auto")
    if source == "checkout" or (
        source == "auto" and run([*helm_cmd(), "show", "chart", oci], check=False, timeout=120).returncode != 0
    ):
        if source == "auto":
            warnings.warn(f"{oci} is not reachable; installing the chart from the checkout instead")
        ensure_chart_deps(CHART_DIR)  # the checkout's chart needs its NFD subchart fetched
        block = block.replace(oci, str(CHART_DIR))
    if os.getenv("DX_K8S_PLUGIN_IMAGE"):
        repo, tag = os.environ["DX_K8S_PLUGIN_IMAGE"].rsplit(":", 1)
        block += f" --set devicePlugin.image.repository={repo} --set devicePlugin.image.tag={tag}"
    run(block, shell=True, timeout=900)
    STATE["installed_by_test"] = True
    wait_until(npu_node, 300, what=f"NFD label {RESOURCE}.present on a node")
    node = npu_node()["metadata"]["name"]
    wait_until(lambda: allocatable(node) >= 1, 300, what=f"{RESOURCE} allocatable on {node}")


# =========================================================================== verify + workloads

@pytest.fixture(scope="module")
def node():
    need("kubectl")
    if not cluster_up():
        pytest.skip("no reachable cluster")
    n = npu_node()
    if not n:
        pytest.skip(f"no node labeled {RESOURCE}.present=true")
    return n


@pytest.fixture(scope="module")
def ns(node):
    kubectl("delete", "namespace", NS, "--ignore-not-found", "--wait=true", timeout=180)
    kubectl("create", "namespace", NS)
    yield NS
    kubectl("delete", "namespace", NS, "--ignore-not-found", "--wait=false", check=False)


def apply(ns, manifest: dict):
    kubectl("apply", "-n", ns, "-f", "-", input=yaml.safe_dump(manifest))


def sample(name) -> dict:
    return yaml.safe_load((SAMPLES_DIR / name).read_text())


def delete_pod(ns, name):
    kubectl("delete", "pod", "-n", ns, name, "--ignore-not-found", "--wait=true", "--timeout=120s", check=False)


def logs(ns, name, container=None):
    args = ["logs", "-n", ns, name] + (["-c", container] if container else [])
    return kubectl(*args, check=False).out


def plain_pod(name, limit=None, node_selector=None, seconds=30) -> dict:
    spec = {"restartPolicy": "Never",
            "containers": [{"name": "c", "image": "ubuntu:24.04", "command": ["sleep", str(seconds)]}]}
    if limit is not None:
        spec["containers"][0]["resources"] = {"limits": {RESOURCE: limit}}
    if node_selector:
        spec["nodeSelector"] = node_selector
    return {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": name}, "spec": spec}


def test_a1_npu_allocatable(node):
    """Guide ex. 1 / Quickstart verify."""
    assert allocatable(node["metadata"]["name"]) >= 1


def test_a2_node_labels(node):
    """Guide ex. 1: NFD labels from the PCI rule and the plugin's feature file."""
    labels = node["metadata"]["labels"]
    missing = [k for k in ("present", "count", "product", "fw-version", "driver-version", "pcie-driver-version")
               if f"{RESOURCE}.{k}" not in labels]
    assert not missing, f"missing labels: {missing}"


def test_a3_smoke_pod_gets_npu(ns):
    """Quickstart smoke test / Guide ex. 2: plain ubuntu image, device + dxcli arrive via CDI."""
    pod = sample("test-pod.yaml")
    name = pod["metadata"]["name"]
    apply(ns, pod)
    try:
        wait_pod(ns, name, {"Running", "Succeeded"})
        out = wait_until(lambda: (lambda o: o if "Device 0" in o else None)(logs(ns, name)), 90,
                         what="dxcli output in smoke-test logs")
        # The header line also says "/dev/dxrt*"; require an actual character device entry.
        assert re.search(r"^c\S+ .*/dev/dxrt\d+$", out, re.M), out
    finally:
        delete_pod(ns, name)


def test_a4_no_request_no_device(ns):
    """Guide ex. 3: without the resource request the pod gets no NPU."""
    pod = sample("test-pod.yaml")
    pod["metadata"]["name"] = "dx-m1-norequest"
    for c in pod["spec"]["containers"]:
        c.pop("resources", None)
    apply(ns, pod)
    try:
        wait_pod(ns, "dx-m1-norequest", {"Running", "Succeeded"})
        # Wait for the next section header, so the device-listing result is fully written.
        out = wait_until(lambda: (lambda o: o if "=== dxcli" in o else None)(logs(ns, "dx-m1-norequest")), 60,
                         what="device listing in logs")
        assert "no NPU injected" in out, out
    finally:
        delete_pod(ns, "dx-m1-norequest")


def test_a5_more_than_available_is_pending(ns, node):
    """Guide ex. 4: asking for more cards than exist leaves the pod Pending."""
    want = allocatable(node["metadata"]["name"]) + 1
    apply(ns, plain_pod("greedy", limit=want))
    try:
        assert f"Insufficient {RESOURCE}" in unschedulable_reason(ns, "greedy")
    finally:
        delete_pod(ns, "greedy")


def test_a6_firmware_node_selector(ns, node):
    """Guide ex. 5: pick nodes by the firmware label; a version no node has stays Pending."""
    fw = node["metadata"]["labels"][f"{RESOURCE}.fw-version"]
    apply(ns, plain_pod("fw-match", limit=1, node_selector={f"{RESOURCE}.fw-version": fw}))
    apply(ns, plain_pod("fw-miss", limit=1, node_selector={f"{RESOURCE}.fw-version": "v0.0.0-acceptance"}))
    try:
        wait_pod(ns, "fw-match", {"Running", "Succeeded"})
        assert "didn't match" in unschedulable_reason(ns, "fw-miss")
    finally:
        delete_pod(ns, "fw-match")
        delete_pod(ns, "fw-miss")


def test_a7_inference(ns):
    """Quickstart inference / Guide ex. 6: dxrun reports a positive FPS."""
    ref = runtime_image()
    ensure_image(ref, build=lambda r: pytest.fail(f"{r} missing; run test_q3a_images with DX_K8S_QA=1"))
    pod = sample("inference-pod.yaml")
    name = pod["metadata"]["name"]
    for c in pod["spec"].get("initContainers", []) + pod["spec"]["containers"]:
        c["image"] = ref
    model_dir = os.getenv("DX_K8S_MODEL_DIR")
    if model_dir:  # air-gapped: use pre-downloaded models instead of the download initContainer
        pod["spec"].pop("initContainers", None)
        for v in pod["spec"]["volumes"]:
            if v["name"] == "models":
                v.clear()
                v.update({"name": "models", "hostPath": {"path": model_dir, "type": "Directory"}})
    apply(ns, pod)
    try:
        wait_pod(ns, name, "Succeeded", timeout=900)
        fps = [float(x) for x in re.findall(r"FPS\s*:\s*([\d.]+)", logs(ns, name, "inference"))]
        assert fps and min(fps) > 0, f"no positive FPS in inference logs: {fps}"
    finally:
        delete_pod(ns, name)


def plugin_pod() -> dict:
    pods = kubectl_json("get", "pods", "-n", RELEASE_NS, "-l", "app.kubernetes.io/component=device-plugin")["items"]
    running = [p for p in pods if p["status"].get("phase") == "Running" and not p["metadata"].get("deletionTimestamp")]
    return running[0] if running else None


def test_a8_plugin_metrics(node):
    """Quickstart metrics: the plugin serves deepx_npu_* and reports the card healthy."""
    pod = wait_until(plugin_pod, 120, what="running device-plugin pod")
    port = 9400
    out = kubectl("get", "--raw", f"/api/v1/namespaces/{RELEASE_NS}/pods/{pod['metadata']['name']}:{port}/proxy/metrics").out
    assert re.search(r"^deepx_npu_device_healthy\{.*\} 1$", out, re.M), out[:2000]


@qa_only
def test_a9_plugin_restart_recovers(node):
    """Guide ex. 7: deleting the plugin pod drops the card from the scheduler until
    the DaemonSet brings a new one; allocatable comes back."""
    old = wait_until(plugin_pod, 120, what="running device-plugin pod")["metadata"]["name"]
    kubectl("delete", "pod", "-n", RELEASE_NS, old, "--wait=false")
    wait_until(lambda: (p := plugin_pod()) and p["metadata"]["name"] != old, 180, what="replacement plugin pod")
    wait_until(lambda: allocatable(node["metadata"]["name"]) >= 1, 180, what="allocatable restored")


def guide_promql() -> list:
    """The PromQL column of the Beginner Guide's Prometheus table (example 8)."""
    section = GUIDE.read_text().split("### Example 8", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^\|[^|\n]*\|\s*`([^`]+)`\s*\|$", section, re.M)


def test_a10_guide_promql(node):
    """Guide ex. 8: every query in the guide's table returns data. Skipped without
    Prometheus — the docs do not install it."""
    queries = guide_promql()
    assert queries, "no PromQL found under Example 8"
    svcs = kubectl_json("get", "svc", "-A", "-l", "operated-prometheus=true")["items"]
    if not svcs:
        pytest.skip("no Prometheus (prometheus-operator) in the cluster")
    svc = svcs[0]["metadata"]
    base = f"/api/v1/namespaces/{svc['namespace']}/services/{svc['name']}:9090/proxy/api/v1/query"
    empty = []
    for q in queries:
        body = kubectl("get", "--raw", f"{base}?query={urllib.parse.quote(q)}").out
        if '"result":[]' in body or '"status":"success"' not in body:
            empty.append(q)
    assert not empty, f"queries returned no data: {empty}"


# =========================================================================== teardown

@qa_only
def test_qz_uninstall():
    """Undo Q3's install (k3s stays). DX_K8S_KEEP=1 keeps it for inspection."""
    if not STATE["installed_by_test"] or os.getenv("DX_K8S_KEEP") == "1":
        pytest.skip("release not installed by this run, or DX_K8S_KEEP=1")
    run([*helm_cmd(), "uninstall", RELEASE, "-n", RELEASE_NS], timeout=300)

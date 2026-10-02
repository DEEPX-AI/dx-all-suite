"""Tier 1 — static checks of the dx-npu chart, samples, dashboard, and K8s docs.

No cluster, no NPU. Needs helm (or DX_K8S_HELM_CMD), jq, git, and network once to
fetch the NFD subchart (not committed) with the README's checkout steps; render
tests skip without network unless DX_K8S_REQUIRE_TOOLS=1.

    pytest tests/test_kubernetes/test_k8s_static.py -m kubernetes_static
"""

import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from k8s_helpers import (  # noqa: E402
    CHART_DIR, DASHBOARD, FIXTURES, K8S_DOCS, PLUGIN_METRICS_GO, REPO_ROOT, RESOURCE,
    SAMPLES_DIR, ensure_chart_deps, helm, jq_exprs, md_links, need, repo_paths, run,
)

pytestmark = pytest.mark.kubernetes_static

NFR_API = "nfd.k8s-sigs.io/v1alpha1/NodeFeatureRule"
APP_VERSION = yaml.safe_load((CHART_DIR / "Chart.yaml").read_text())["appVersion"]


def render(*args, chart=CHART_DIR) -> list:
    ensure_chart_deps(chart)
    docs = yaml.safe_load_all(helm("template", "t", chart, *args).stdout)
    return [d for d in docs if d]


def of_kind(objs, kind) -> list:
    return [o for o in objs if o.get("kind") == kind]


def plugin_daemonset(objs) -> dict:
    ds = [d for d in of_kind(objs, "DaemonSet") if d["metadata"]["name"].endswith("-device-plugin")]
    assert len(ds) == 1, f"expected one device-plugin DaemonSet, got {[d['metadata']['name'] for d in ds]}"
    return ds[0]


# --------------------------------------------------------------------------- chart

def test_s1_helm_lint():
    out = helm("lint", CHART_DIR).out
    assert "0 chart(s) failed" in out, out


def test_s2_default_render():
    objs = render()
    assert not of_kind(objs, "NodeFeatureRule"), "NodeFeatureRule must not render without NFD (CRD may be absent)"
    container = plugin_daemonset(objs)["spec"]["template"]["spec"]["containers"][0]
    assert container["image"].endswith(f":{APP_VERSION}"), container["image"]
    for o in objs:
        assert o["metadata"].get("labels", {}).get("app.kubernetes.io/version") == APP_VERSION, o["metadata"]["name"]


def test_s3_nfd_enabled_renders_rule_matching_m1():
    rules = of_kind(render("--set", "nfd.enabled=true"), "NodeFeatureRule")
    assert len(rules) == 1
    expr = rules[0]["spec"]["rules"][0]["matchFeatures"][0]["matchExpressions"]
    assert expr["vendor"]["value"] == ["1ff4"], expr
    assert expr["device"]["value"] == ["0100"], expr


def test_s4_rule_renders_when_cluster_serves_nfd_api():
    assert len(of_kind(render("--api-versions", NFR_API), "NodeFeatureRule")) == 1


def test_s5_rule_can_be_disabled():
    assert not of_kind(render("--set", "nfd.enabled=true", "--set", "nodeFeatureRule.enabled=false"), "NodeFeatureRule")


def test_s6_image_tag_override():
    container = plugin_daemonset(render("--set", "devicePlugin.image.tag=dev"))["spec"]["template"]["spec"]["containers"][0]
    assert container["image"].endswith(":dev"), container["image"]


def test_s7_fresh_checkout_renders_after_documented_steps(tmp_path):
    """A fresh clone has no subchart (it is gitignored), and Helm checks every declared
    dependency even with nfd.enabled=false. The deploy README's checkout steps must
    fetch it so the chart renders."""
    need("git")
    rel = CHART_DIR.relative_to(REPO_ROOT)
    archive = tmp_path / "chart.tar"
    # Tracked files only (staged included): what a fresh clone gets.
    tree = run(["git", "write-tree"]).stdout.strip()
    run(["git", "archive", "--format=tar", "-o", str(archive), tree, str(rel)])
    with tarfile.open(archive) as t:
        t.extractall(tmp_path)
    fresh = tmp_path / rel
    assert not list((fresh / "charts").glob("*.tgz")), "subchart tarball is committed; it should be fetched"
    objs = render(chart=fresh)  # runs the README's checkout steps first
    assert plugin_daemonset(objs)


# --------------------------------------------------------------------------- samples / dashboard

def _containers(pod, key="containers"):
    return pod["spec"].get(key, [])


def test_s8_samples():
    pods = {p.name: yaml.safe_load(p.read_text()) for p in sorted(SAMPLES_DIR.glob("*.yaml"))}
    assert {"test-pod.yaml", "inference-pod.yaml"} <= set(pods), sorted(pods)
    for name in ("test-pod.yaml", "inference-pod.yaml"):
        limits = _containers(pods[name])[0].get("resources", {}).get("limits", {})
        assert str(limits.get(RESOURCE)) == "1", f"{name} must request {RESOURCE}: 1"
    inference = pods["inference-pod.yaml"]
    assert _containers(inference, "initContainers"), "inference-pod must fetch its model in an initContainer"
    script = " ".join(_containers(inference)[0].get("args", []))
    assert "dxrtd" in script, "inference-pod must start its own dxrtd (dx_rt talks to it over a local socket)"


def test_s9_dashboard_queries_existing_metrics():
    dash = json.loads(DASHBOARD.read_text())
    assert dash.get("uid") and dash.get("panels")
    exprs = [t["expr"] for p in dash["panels"] for t in p.get("targets", [])]
    used = set(re.findall(r"deepx_npu_\w+", " ".join(exprs)))
    assert used, "dashboard queries no deepx_npu_* metric"
    if not PLUGIN_METRICS_GO.exists():
        pytest.skip("dx-k8s-device-plugin submodule not checked out")
    defined = set(re.findall(r'NewDesc\(\s*"(deepx_npu_\w+)"', PLUGIN_METRICS_GO.read_text()))
    assert used <= defined, f"dashboard uses metrics the plugin does not serve: {sorted(used - defined)}"


# --------------------------------------------------------------------------- docs

NODE_LIST = FIXTURES / "node-list.json"
DOC_IDS = [d.relative_to(REPO_ROOT).as_posix() for d in K8S_DOCS]


def _jq_cases():
    return [(d, e) for d in K8S_DOCS for e in jq_exprs(d)]


def test_s10_docs_have_jq_checks():
    assert _jq_cases(), "no `kubectl get node -o json | jq` command found in the K8s docs"


@pytest.mark.parametrize("doc,expr", _jq_cases(),
                         ids=[f"{d.name}:{e}" for d, e in _jq_cases()])
def test_s10_doc_jq_works_on_real_node_list(doc, expr):
    """`kubectl get node -o json` is a List even for one node, so an expression that
    reads `.status` directly prints nothing — the bug the review caught by hand."""
    need("jq")
    r = subprocess.run(["jq", expr, str(NODE_LIST)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    assert lines and "null" not in lines, f"{doc.name}: `jq '{expr}'` prints nothing useful:\n{r.stdout or '(empty)'}"


@pytest.mark.parametrize("doc", K8S_DOCS, ids=DOC_IDS)
def test_s11_doc_paths_and_links_exist(doc):
    missing = [p for p in repo_paths(doc) if not (REPO_ROOT / p).exists()]
    missing += [l for l in md_links(doc) if not (doc.parent / l).exists()]
    assert not missing, f"{doc.relative_to(REPO_ROOT)} points at missing files: {missing}"

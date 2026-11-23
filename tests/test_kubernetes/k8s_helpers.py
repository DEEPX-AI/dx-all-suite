"""Shared helpers for the Kubernetes test suites.

The point of these suites is to fail when the K8s docs stop working as written,
so the helpers read commands, jq expressions, and paths straight out of the docs
instead of keeping a second copy in the tests.
"""

import json
import os
import re
import shlex
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
K8S_DIR = REPO_ROOT / "deploy" / "k8s"
CHART_DIR = K8S_DIR / "charts" / "dx-npu"
SAMPLES_DIR = K8S_DIR / "samples"
DASHBOARD = K8S_DIR / "dashboards" / "dx-npu.json"
PLUGIN_METRICS_GO = REPO_ROOT / "dx-k8s-device-plugin" / "internal" / "metrics" / "metrics.go"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

SITE = "https://developer.deepx.ai/tech-docs/DX-AllSuite"


class _PageText(HTMLParser):
    """Published guide page -> Markdown-like text: `##` headings, numbered `**step**`
    items, fenced code blocks, `inline code` and `| table | rows |`, which is all the
    doc helpers and the tests look for."""

    def __init__(self) -> None:
        super().__init__()
        self.out: list = []
        self._pre = False
        self._ol: list = []
        self._step = False   # just wrote "N. ": keep the step's first words on that line
        self._skip = 0       # inside <script>/<style>: not page text

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "pre":
            lang = re.search(r"language-(\w+)", attr.get("class") or "")
            self.out.append(f"\n```{lang.group(1) if lang else ''}\n")
            self._pre = True
        elif tag == "br" and self._pre:
            self.out.append("\n")
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "ol":
            self._ol.append(int(attr.get("start") or 1) - 1)
        elif tag == "li" and self._ol:
            self._ol[-1] += 1
            self.out.append(f"\n{self._ol[-1]}. ")
            self._step = True
        elif tag in ("strong", "code") and not self._pre:
            self.out.append("**" if tag == "strong" else "`")
        elif tag == "tr":
            self.out.append("\n|")
        elif tag in ("td", "th"):
            self.out.append(" ")
        elif tag in ("p", "li", "div", "ul") and not self._pre:
            if not self._step:
                self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag == "pre":
            self.out.append("\n```\n")
            self._pre = False
        elif tag == "ol" and self._ol:
            self._ol.pop()
        elif tag in ("strong", "code") and not self._pre:
            self.out.append("**" if tag == "strong" else "`")
        elif tag in ("td", "th"):
            self.out.append(" |")
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n")

    def handle_data(self, data):
        if self._skip:
            return
        if self._step:
            if not data.strip():
                return
            self._step = False
        self.out.append(data.replace("\u200b", ""))


class SiteDoc:
    """A guide page on developer.deepx.ai, read the way the local Markdown files are.
    When the page cannot be read the text is empty and one flag says why:
    `unreachable` (no network, or the site is failing) or `gone` (the site answered
    404/410: the page was removed or renamed). `require_doc` turns them into a skip
    and a failure."""

    def __init__(self, slug: str) -> None:
        self.name = slug
        self.url = f"{SITE}/{slug}/"
        self.parent = REPO_ROOT
        self.unreachable = False
        self.gone = 0   # the HTTP status, when the site says the page does not exist
        self._text = None

    def read_text(self) -> str:
        if self._text is None:
            try:
                with urllib.request.urlopen(self.url, timeout=20) as r:
                    page = _PageText()
                    page.feed(r.read().decode("utf-8", errors="replace"))
                self._text = "".join(page.out)
            except urllib.error.HTTPError as e:
                if e.code in (404, 410):
                    self.gone = e.code
                else:
                    self.unreachable = True
                self._text = ""
            except OSError:
                self.unreachable = True
                self._text = ""
        return self._text


def require_doc(doc) -> None:
    """A published guide that cannot be fetched skips the test; one the site no
    longer has fails it. Local files pass through."""
    if not isinstance(doc, SiteDoc):
        return
    doc.read_text()
    if doc.gone:
        pytest.fail(f"{doc.url} is gone from the site (HTTP {doc.gone})")
    if doc.unreachable:
        pytest.skip(f"{doc.url} is unreachable")


def doc_id(doc) -> str:
    return doc.url if isinstance(doc, SiteDoc) else doc.relative_to(REPO_ROOT).as_posix()


QUICKSTART = SiteDoc("Kubernetes_Quickstart")
BEGINNER_GUIDE = SiteDoc("Kubernetes_Beginner_Guide")
K8S_DOCS = [
    QUICKSTART,
    BEGINNER_GUIDE,
    K8S_DIR / "README.md",
    REPO_ROOT / "README.md",
    # absent from a release tree
    *(p for p in (REPO_ROOT / "README-KO.md",) if p.is_file()),
]

RESOURCE = "deepx.ai/dx-m1"
QA = os.getenv("DX_K8S_QA") == "1"


# --------------------------------------------------------------------------- tools

def need(tool: str) -> None:
    """Skip when a tool is missing, unless DX_K8S_REQUIRE_TOOLS=1 makes it a failure,
    so an automated run cannot go green by skipping everything."""
    if shutil.which(tool):
        return
    msg = f"`{tool}` not found on PATH"
    if os.getenv("DX_K8S_REQUIRE_TOOLS") == "1":
        pytest.fail(msg)
    pytest.skip(msg)


def run(cmd, *, input=None, timeout=300, check=True, cwd=REPO_ROOT, shell=False):
    """Run a command, return CompletedProcess with text output (stderr merged)."""
    r = subprocess.run(
        cmd, input=input, text=True, capture_output=True, timeout=timeout,
        cwd=cwd, shell=shell, executable="/bin/bash" if shell else None,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if check and r.returncode != 0:
        shown = cmd if isinstance(cmd, str) else " ".join(map(str, cmd))
        pytest.fail(f"command failed ({r.returncode}): {shown}\n{out[-4000:]}")
    r.out = out
    return r


def helm_cmd() -> list:
    override = os.getenv("DX_K8S_HELM_CMD")
    if override:
        return shlex.split(override)
    need("helm")
    return ["helm"]


def helm(*args, **kw):
    return run([*helm_cmd(), *map(str, args)], **kw)


def kubectl(*args, **kw):
    return run(["kubectl", *map(str, args)], **kw)


def kubectl_json(*args):
    return json.loads(kubectl(*args, "-o", "json").stdout)


# --------------------------------------------------------------------------- docs

_FENCE = re.compile(r"^[ \t]*```(\w*)\n(.*?)^[ \t]*```", re.S | re.M)
_HEADING = re.compile(r"^(#{2,4} .*|\d+\. \*\*.*)$", re.M)


def _dedent(block: str) -> str:
    lines = block.splitlines()
    pad = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    return "\n".join(l[pad:] for l in lines) + "\n"


def doc_block(doc: Path, heading_prefix: str, n: int = 0, lang: str = "bash") -> str:
    """Return the n-th ``lang`` fenced block under the heading (or numbered step)
    that starts with ``heading_prefix``. Fails if the heading is gone, so renaming
    a Quickstart section breaks the test instead of silently skipping a step."""
    require_doc(doc)
    text = doc.read_text()
    headings = [(m.start(), m.group(1)) for m in _HEADING.finditer(text)]
    found = []
    for m in _FENCE.finditer(text):
        if m.group(1) != lang:
            continue
        owner = next((h for p, h in reversed(headings) if p < m.start()), "")
        if owner.lstrip("#0123456789. *").startswith(heading_prefix.lstrip("#0123456789. *")):
            found.append(_dedent(m.group(2)))
    if len(found) <= n:
        pytest.fail(f"{doc.name}: no {lang} block #{n} under a heading starting with {heading_prefix!r}")
    return found[n]


def jq_exprs(doc: Path) -> list:
    """Every jq expression the doc applies to ``kubectl get node -o json``."""
    return re.findall(r"kubectl get nodes? -o json \| jq (?:-\w+ )*'([^']+)'", doc.read_text())


def repo_paths(doc: Path) -> list:
    """Repo-relative paths a reader is told to use (deploy/k8s/…)."""
    paths = re.findall(r"(?<![\w/.])(deploy/k8s/[\w./-]*\w)", doc.read_text())
    return sorted(set(paths))


def md_links(doc: Path) -> list:
    """Relative links to files (``[x](path)``), fragment stripped, URLs excluded."""
    out = []
    for target in re.findall(r"\]\(([^)\s]+)\)", doc.read_text()):
        if re.match(r"^[a-z]+://|^#|^mailto:", target):
            continue
        out.append(target.split("#", 1)[0])
    return sorted(set(t for t in out if t))


# --------------------------------------------------------------------------- chart deps

DEPLOY_README = K8S_DIR / "README.md"
_NET_ERRORS = re.compile(r"no such host|dial tcp|connection refused|i/o timeout|"
                         r"Could not resolve|network is unreachable|TLS handshake timeout", re.I)


def checkout_dep_steps() -> str:
    """The deploy README's "from this checkout" block, minus the final `helm install`:
    the steps a reader runs to fetch the NFD subchart, which is not committed."""
    block = doc_block(DEPLOY_README, "Install", n=1)
    steps = [l for l in block.splitlines() if l.strip() and not l.lstrip().startswith("helm install")]
    if not any("helm dependency build" in l for l in steps):
        pytest.fail(f"{DEPLOY_README.name}: checkout install no longer runs `helm dependency build`")
    return "\n".join(steps) + "\n"


def ensure_chart_deps(chart_dir: Path = CHART_DIR) -> None:
    """Fetch the chart's dependencies by running the documented checkout steps, unless
    already present. Needs network; skips when it is unavailable (fails under
    DX_K8S_REQUIRE_TOOLS=1). Any other failure means the documented steps are wrong."""
    deps = yaml_load(chart_dir / "Chart.yaml").get("dependencies", [])
    if all(list((chart_dir / "charts").glob(f"{d['name']}-*.tgz")) for d in deps):
        return
    cmd = checkout_dep_steps()
    if os.getenv("DX_K8S_HELM_CMD"):
        cmd = re.sub(r"(?m)^(\s*)helm ", lambda m: m.group(1) + os.environ["DX_K8S_HELM_CMD"] + " ", cmd)
    r = run(cmd, shell=True, check=False, timeout=300, cwd=chart_dir.parent.parent)
    if r.returncode == 0:
        return
    if _NET_ERRORS.search(r.out):
        msg = f"cannot fetch chart dependencies (no network?):\n{r.out[-800:]}"
        if os.getenv("DX_K8S_REQUIRE_TOOLS") == "1":
            pytest.fail(msg)
        pytest.skip(msg)
    pytest.fail(f"the README's checkout steps failed:\n{cmd}\n{r.out[-2000:]}")


def yaml_load(path: Path):
    import yaml
    return yaml.safe_load(path.read_text())


# --------------------------------------------------------------------------- cluster

def npu_node() -> dict:
    """First node labeled as carrying a DX-M1, or None."""
    nodes = kubectl_json("get", "nodes", "-l", f"{RESOURCE}.present=true")["items"]
    return nodes[0] if nodes else None


def allocatable(node_name: str) -> int:
    n = kubectl_json("get", "node", node_name)
    return int(n["status"].get("allocatable", {}).get(RESOURCE, "0"))


def wait_until(pred, timeout: float, interval: float = 2.0, what: str = "condition"):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = pred()
        if last:
            return last
        time.sleep(interval)
    pytest.fail(f"timed out after {timeout:.0f}s waiting for {what} (last: {last!r})")


_PULL_ERRORS = {"ErrImagePull", "ImagePullBackOff", "InvalidImageName"}


def pod_state(ns: str, name: str) -> dict:
    return kubectl_json("get", "pod", "-n", ns, name)


def wait_pod(ns: str, name: str, phases, timeout: float = 180) -> dict:
    """Wait until the pod reaches one of ``phases``. Fails fast on image pull errors,
    naming the image, since that is the most likely failure before images are published."""
    phases = {phases} if isinstance(phases, str) else set(phases)

    def check():
        pod = pod_state(ns, name)
        statuses = pod["status"].get("initContainerStatuses", []) + pod["status"].get("containerStatuses", [])
        for cs in statuses:
            waiting = cs.get("state", {}).get("waiting", {})
            if waiting.get("reason") in _PULL_ERRORS:
                pytest.fail(
                    f"pod {name}: cannot pull {cs.get('image')} ({waiting['reason']}).\n"
                    f"Publish it, or import it into k3s: docker save <image> | "
                    f"sudo k3s ctr --namespace k8s.io images import -"
                )
        if pod["status"].get("phase") == "Failed" and "Failed" not in phases:
            pytest.fail(f"pod {name} failed:\n{kubectl('logs', '-n', ns, name, '--all-containers', check=False).out[-3000:]}")
        return pod if pod["status"].get("phase") in phases else None

    return wait_until(check, timeout, what=f"pod {name} in {sorted(phases)}")


def unschedulable_reason(ns: str, name: str, timeout: float = 60) -> str:
    def check():
        for c in pod_state(ns, name)["status"].get("conditions", []):
            if c.get("type") == "PodScheduled" and c.get("status") == "False" and c.get("message"):
                return c["message"]
        return None
    return wait_until(check, timeout, what=f"scheduler verdict for {name}")


# --------------------------------------------------------------------------- images

def _sudo_prefix() -> list:
    return [] if os.geteuid() == 0 else ["sudo", "-n"]


def _docker() -> list:
    need("docker")
    if run(["docker", "info"], check=False, timeout=30).returncode == 0:
        return ["docker"]
    return [*_sudo_prefix(), "docker"]


def k3s_has_image(ref: str) -> bool:
    r = run([*_sudo_prefix(), "k3s", "ctr", "--namespace", "k8s.io", "images", "ls", "-q"],
            check=False, timeout=60)
    return r.returncode == 0 and ref in r.stdout.split()


def k3s_import(ref: str) -> None:
    docker = " ".join(_docker())
    sudo = " ".join(_sudo_prefix())
    run(f"{docker} save {shlex.quote(ref)} | {sudo} k3s ctr --namespace k8s.io images import -",
        shell=True, timeout=1800)
    if not k3s_has_image(ref):
        pytest.fail(f"imported {ref} but k3s still does not list it")


def ensure_image(ref: str, build) -> str:
    """Make ``ref`` available to k3s: already in its store → pull → build locally
    under the same name and import. ``build(ref)`` must leave ``ref`` in docker.

    Returns how it got there. Builds only in QA mode (they can take tens of minutes)
    and never when DX_K8S_IMAGES=pull."""
    if k3s_has_image(ref):
        return "present"
    pull = run([*_sudo_prefix(), "k3s", "ctr", "--namespace", "k8s.io", "images", "pull", ref],
               check=False, timeout=600)
    if pull.returncode == 0 and k3s_has_image(ref):
        return "pulled"
    if os.getenv("DX_K8S_IMAGES", "auto") == "pull" or not QA:
        pytest.fail(f"{ref} is not in k3s and cannot be pulled; set DX_K8S_QA=1 to build it locally\n{pull.out[-1500:]}")
    build(ref)
    k3s_import(ref)
    return "built"

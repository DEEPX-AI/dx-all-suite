"""Lab flows that must do real work on the DX-M1.

- Add Model passes a language add_model.sh accepts (cpp|py|both, not ``--lang python``) and does not rely on the
  script's built-in references, which are legacy folders the per-model layout does not have.
- A package copied from a per-model example must not keep the reference's ``_FIXED_VARIANT``, or it dies with
  "no variant config".
- Rollback really rolls back, and an applied change stays listed in Generated Files / Safety Center.
- Experiment advances past "compile / pending".
"""

import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

_STUDIO_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_STUDIO_DIR / "shared"))

REF = "yolo26-n_640x640"

# A stand-in for add_model.sh: records its argv, then copies the --base-model example to <category>/<name>
# with file names (not contents) renamed — what the real script does to a per-model example.
FAKE_ADD_MODEL = r"""#!/bin/bash
echo "$@" > "$(dirname "$0")/argv.txt"
NAME="$1"; shift; shift
LANG_MODE=both; CAT=""; BASE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG_MODE="$2"; shift 2;;
    --category) CAT="$2"; shift 2;;
    --base-model) BASE="$2"; shift 2;;
    *) shift;;
  esac
done
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
case "$LANG_MODE" in cpp) L="cpp";; py) L="python";; both) L="cpp python";; *) echo "Invalid --lang: $LANG_MODE (cpp|py|both)"; exit 1;; esac
for l in $L; do
  SRC=$(find "$ROOT/src/${l}_example" -type d -name "$BASE" | head -1)
  [ -n "$SRC" ] || { echo "Base model not found: $BASE"; exit 1; }
  DST="$ROOT/src/${l}_example/$CAT/$NAME"
  mkdir -p "$(dirname "$DST")"; cp -r "$SRC" "$DST"
  find "$DST" -depth -name "*$BASE*" | while read -r f; do
    d=$(dirname "$f"); b=$(basename "$f"); mv "$f" "$d/${b//$BASE/$NAME}"
  done
done
echo "[SUCCESS] model package created: $NAME"
"""


def _example(root, lang, task, family, stem, factory=True):
    d = root / "src" / f"{lang}_example" / task / family / stem
    (d / "factory").mkdir(parents=True)
    ext = ".py" if lang == "python" else ".cpp"
    (d / f"{stem}_sync{ext}").write_text(f'_FIXED_VARIANT = "{stem}"\n' if lang == "python" else "int main(){}\n")
    (d / "config.json").write_text(json.dumps({"variant": stem, "dxnn_file": f"{stem}.dxnn"}))
    if factory:
        fext = ".py" if lang == "python" else ".hpp"
        (d / "factory" / f"{stem}_factory{fext}").write_text("class Yolo26Factory: pass\n")
    return d


@pytest.fixture
def app_root(tmp_path):
    """A per-model dx_app tree: yolo26-n in both languages, a python-only example, one without a factory."""
    root = tmp_path / "dx_app"
    for lang in ("python", "cpp"):
        _example(root, lang, "object_detection", "yolo26", REF)
    _example(root, "python", "object_detection", "damoyolo", "damoyolo-s_640x640")
    _example(root, "python", "image_classification", "resnet", "resnet18_224x224", factory=False)
    (root / "config").mkdir()
    (root / "config" / "model_registry.json").write_text(json.dumps([{"variant": REF, "family": "yolo26"}]))
    scripts = root / "scripts"
    scripts.mkdir()
    (scripts / "add_model.sh").write_text(FAKE_ADD_MODEL)
    from shared import dx_app_layout
    dx_app_layout.clear_cache()
    patches = [
        patch("developer.DX_APP_ROOT", root),
        patch("developer.CPP_DIR", root / "src" / "cpp_example"),
        patch("developer.PY_DIR", root / "src" / "python_example"),
        patch("developer.SCRIPTS_DIR", scripts),
        patch("lab_portal.DX_APP_ROOT", root),
        patch("lab_portal.CPP_DIR", root / "src" / "cpp_example"),
        patch("lab_portal.PY_DIR", root / "src" / "python_example"),
    ]
    for p in patches:
        p.start()
    yield root
    for p in patches:
        p.stop()
    dx_app_layout.clear_cache()
    import lab_portal
    lab_portal._manifests.clear()
    lab_portal._apply_locks.clear()


def _tok():
    from developer import lab_session
    return lab_session()["token"]


# ── Add Model ─────────────────────────────────────────────────────────────────────────────


def test_reference_examples_are_the_examples_with_a_factory_per_language(app_root):
    from developer import reference_examples
    refs = reference_examples()
    od = {r["name"]: r["langs"] for r in refs["object_detection"]}
    assert od[REF] == ["python", "cpp"]
    assert od["damoyolo-s_640x640"] == ["python"]
    assert "image_classification" not in refs  # its only example has no factory to copy


def test_add_model_passes_py_and_a_per_model_base(app_root):
    from developer import dev_add
    res = dev_add(_tok(), "mynet", "object_detection", "python", "object_detection", "")
    assert res.get("ok") is True, res
    argv = (app_root / "scripts" / "argv.txt").read_text().split()
    assert argv[argv.index("--lang") + 1] == "py"
    assert argv[argv.index("--category") + 1] == "object_detection"
    assert argv[argv.index("--base-model") + 1] in (REF, "damoyolo-s_640x640")
    assert argv[1] == "detection"  # a task type add_model.sh accepts


def test_add_model_both_languages_starts_from_an_example_that_has_both(app_root):
    from developer import dev_add
    res = dev_add(_tok(), "mynet", "object_detection", "both", "object_detection", "")
    assert res.get("ok") is True, res
    assert res["reference"] == REF
    assert sorted(res["created"]) == ["src/cpp_example/object_detection/mynet",
                                      "src/python_example/object_detection/mynet"]


def test_add_model_renames_the_copied_variant_so_the_package_runs(app_root):
    from developer import dev_add
    res = dev_add(_tok(), "mynet", "object_detection", "python", "object_detection", "", base_model=REF)
    assert res.get("ok") is True, res
    d = app_root / "src" / "python_example" / "object_detection" / "mynet"
    assert (d / "mynet_sync.py").read_text() == '_FIXED_VARIANT = "mynet"\n'
    assert json.loads((d / "config.json").read_text())["variant"] == "mynet"
    # the model file stays the reference's until the user points --model at theirs
    assert json.loads((d / "config.json").read_text())["dxnn_file"] == f"{REF}.dxnn"


def test_add_model_rejects_a_base_that_is_not_an_example_of_the_category(app_root):
    from developer import dev_add
    res = dev_add(_tok(), "mynet", "object_detection", "both", "object_detection", "", base_model="damoyolo-s_640x640")
    assert res.get("status") == 400 and res.get("error_code") == "unknown_base_model"


def test_add_model_says_when_a_category_has_nothing_to_start_from(app_root):
    from developer import dev_add
    res = dev_add(_tok(), "mynet", "image_classification", "python", "image_classification", "")
    assert res.get("status") == 400 and res.get("error_code") == "no_reference"


def test_add_model_failure_carries_the_scripts_reason_without_colour_codes(app_root):
    (app_root / "scripts" / "add_model.sh").write_text(
        "#!/bin/bash\necho -e '\\033[0;31m[DXAPP] [ERROR]\\033[0m C++ reference factory not found'\nexit 1\n")
    from developer import dev_add
    res = dev_add(_tok(), "mynet", "object_detection", "python", "object_detection", "")
    assert res.get("ok") is False
    assert res["error"] == "[DXAPP] [ERROR] C++ reference factory not found"
    assert "\x1b" not in res["output"]


def test_lab_capabilities_offer_the_start_from_examples(app_root):
    from lab_portal import lab_capabilities
    caps = lab_capabilities()
    assert {r["name"] for r in caps["reference_examples"]["object_detection"]} == {REF, "damoyolo-s_640x640"}


def test_add_model_dry_run_names_the_start_from_example(app_root):
    from lab_portal import plan_add_model
    m = plan_add_model(_tok(), {"model_name": "mynet", "category": "object_detection", "lang": "both"})
    assert m["kind"] == "add_model" and m["inputs"]["base_model"] == REF
    bad = plan_add_model(_tok(), {"model_name": "mynet", "category": "image_classification", "lang": "python"})
    assert bad.get("error_code") == "no_reference"


# ── Apply → listed → rollback ────────────────────────────────────────────────────────────


def _apply_add_model(name="mynet", lang="both"):
    from lab_portal import plan_add_model, apply_add_model
    tok = _tok()
    m = plan_add_model(tok, {"model_name": name, "category": "object_detection", "lang": lang})
    body, code = apply_add_model(tok, {"manifest_id": m["id"]})
    assert code == 200 and body.get("ok") is True, body
    return m["id"], body


def test_an_applied_add_model_stays_listed_with_its_files(app_root):
    from lab_portal import list_lab_manifests, generated_files_for_manifest
    mid, body = _apply_add_model()
    listed = {m["id"]: m for m in list_lab_manifests()}
    assert listed[mid]["status"] == "applied"
    files, code = generated_files_for_manifest(mid)
    paths = {f["path"] for f in files["files"]}
    assert "src/python_example/object_detection/mynet/mynet_sync.py" in paths
    assert "src/cpp_example/object_detection/mynet/factory/mynet_factory.hpp" in paths


def test_composer_workflows_are_not_listed_as_lab_changes(app_root):
    from lab_portal import create_manifest, list_lab_manifests
    create_manifest("composer_workflow", inputs={}, status="ready")
    assert all(m["kind"] in ("add_model", "task_scaffold") for m in list_lab_manifests())


def test_rollback_deletes_exactly_what_apply_created(app_root):
    from lab_portal import rollback_manifest, list_lab_manifests
    keep = app_root / "src" / "python_example" / "object_detection" / "yolo26" / REF
    mid, _ = _apply_add_model()
    created = [app_root / "src" / f"{l}_example" / "object_detection" / "mynet" for l in ("python", "cpp")]
    assert all(p.is_dir() for p in created)
    refused, code = rollback_manifest(mid, {"confirmations": {"rollback": "rollback:other"}})
    assert code == 400 and refused["error_code"] == "confirmation_required"
    body, code = rollback_manifest(mid, {"confirmations": {"rollback": "rollback:mynet"}})
    assert code == 200 and body["ok"] is True, body
    assert not any(p.exists() for p in created)
    assert keep.is_dir()
    assert {m["id"]: m for m in list_lab_manifests()}[mid]["status"] == "rolled_back"


def test_rollback_refuses_an_add_model_that_overwrote_existing_files(app_root):
    from lab_portal import plan_add_model, apply_add_model, rollback_manifest
    existing = app_root / "src" / "python_example" / "object_detection" / "mynet"
    existing.mkdir(parents=True)
    (existing / "mine.py").write_text("# the user's own file\n")
    tok = _tok()
    m = plan_add_model(tok, {"model_name": "mynet", "category": "object_detection", "lang": "python"})
    body, code = apply_add_model(tok, {"manifest_id": m["id"], "confirmations": {"overwrite": "overwrite:mynet"}})
    assert code == 200, body
    body, code = rollback_manifest(m["id"], {"confirmations": {"rollback": "rollback:mynet"}})
    assert code == 400 and body["error_code"] == "rollback_unsupported"
    assert (existing / "mine.py").is_file()


def test_rollback_of_a_manifest_that_was_never_applied_is_refused(app_root):
    from lab_portal import plan_add_model, rollback_manifest
    m = plan_add_model(_tok(), {"model_name": "mynet", "category": "object_detection", "lang": "both"})
    body, code = rollback_manifest(m["id"], {"confirmations": {"rollback": "rollback:mynet"}})
    assert code == 400 and body["error_code"] == "not_applied"


def test_rollback_of_a_created_task_skeleton_removes_its_files(app_root):
    from lab_portal import plan_task_scaffold, apply_task_scaffold, rollback_manifest
    tok = _tok()
    m = plan_task_scaffold(tok, {"task_name": "depth_fusion", "lang": "python", "scaffold_type": "full"})
    body, code = apply_task_scaffold(tok, {"manifest_id": m["id"]})
    assert code == 200, body
    made = [app_root / op["path"] for op in m["operations"]]
    assert made and all(p.is_file() for p in made)
    body, code = rollback_manifest(m["id"], {"confirmations": {"rollback": "rollback:depth_fusion"}})
    assert code == 200, body
    assert not any(p.exists() for p in made)


# ── Experiment ───────────────────────────────────────────────────────────────────────────


class _FakeProc:
    def __init__(self, lines, rc):
        self._lines, self.returncode, self.killed = lines, None, False
        self._rc = rc
        self.stdout = iter(line + "\n" for line in lines)

    def wait(self, timeout=None):
        self.returncode = -9 if self.killed else self._rc
        return self.returncode

    def kill(self):
        self.killed = True


@pytest.fixture
def experiment(tmp_path, monkeypatch):
    import lab_portal
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "m.dxnn").write_bytes(b"x")
    monkeypatch.setattr(lab_portal, "SCRIPT_DIR", tmp_path)
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", tmp_path)
    lab_portal._experiment_runs.clear()
    yield lab_portal
    lab_portal._experiment_runs.clear()


def _wait_terminal(lp, run_id, timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        run, _ = lp.get_experiment_run(run_id)
        if run["status"] in ("completed", "failed", "cancelled"):
            return run
        time.sleep(0.02)
    raise AssertionError(f"run did not finish: {run}")


def test_experiment_runs_inspect_smoke_benchmark_and_reports_fps(experiment):
    lp = experiment
    calls = []
    outputs = {
        "parse_model": (["Model Information", " .dxnn Format Version   : v8"], 0),
        "single": (["* Benchmark Result (single input)", "  - FPS : 40.13"], 0),
        "bench": (["* Benchmark Result (100 inputs)", "  - FPS : 183.05"], 0),
    }

    def popen(cmd, **kw):
        calls.append(cmd)
        key = "parse_model" if cmd[0].endswith("parse_model") else ("single" if "-s" in cmd else "bench")
        return _FakeProc(*outputs[key])

    with patch.object(lp, "_experiment_popen", popen):
        run, code = lp.start_experiment_run({"source_path": "outputs/m.dxnn", "model_name": "m"})
        assert code == 200 and [s["id"] for s in run["steps"]] == ["inspect", "smoke", "benchmark"]
        lp.launch_experiment_run(run["id"])
        run = _wait_terminal(lp, run["id"])
    assert run["status"] == "completed", run
    assert [s["status"] for s in run["steps"]] == ["done", "done", "done"]
    assert run["result"]["fps"] == pytest.approx(183.05)
    assert any("FPS : 183.05" in line for line in run["log_tail"])
    assert [Path(c[0]).name for c in calls] == ["parse_model", "run_model", "run_model"]


def test_experiment_stops_at_the_step_that_fails(experiment):
    lp = experiment

    def popen(cmd, **kw):
        if cmd[0].endswith("parse_model"):
            return _FakeProc(["[dxrt-exception] Invalid model exception error-code=262"], 255)
        raise AssertionError("must not run the NPU after a failed inspect")

    with patch.object(lp, "_experiment_popen", popen):
        run, _ = lp.start_experiment_run({"source_path": "outputs/m.dxnn"})
        lp.launch_experiment_run(run["id"])
        run = _wait_terminal(lp, run["id"])
    assert run["status"] == "failed"
    assert run["steps"][0]["status"] == "failed"
    assert "Invalid model" in run["blockers"][0]["message"]


def test_experiment_cancel_kills_the_running_step(experiment):
    lp = experiment
    gate = threading.Event()
    procs = []

    class _Slow(_FakeProc):
        def __init__(self):
            super().__init__([], 0)
            self.stdout = self._lines_until_killed()

        def _lines_until_killed(self):
            gate.set()
            while not self.killed:
                time.sleep(0.01)
            return
            yield  # pragma: no cover

    def popen(cmd, **kw):
        p = _Slow()
        procs.append(p)
        return p

    with patch.object(lp, "_experiment_popen", popen):
        run, _ = lp.start_experiment_run({"source_path": "outputs/m.dxnn"})
        lp.launch_experiment_run(run["id"])
        assert gate.wait(2)
        lp.cancel_experiment_run(run["id"])
        run = _wait_terminal(lp, run["id"])
    assert run["status"] == "cancelled"
    assert procs and procs[0].killed


def test_repeated_dry_runs_list_one_preview(app_root):
    from lab_portal import plan_add_model, list_lab_manifests
    for _ in range(3):
        plan_add_model(_tok(), {"model_name": "mynet", "category": "object_detection", "lang": "both"})
    plan_add_model(_tok(), {"model_name": "other", "category": "object_detection", "lang": "both"})
    names = [m["inputs"]["model_name"] for m in list_lab_manifests()]
    assert sorted(names) == ["mynet", "other"]

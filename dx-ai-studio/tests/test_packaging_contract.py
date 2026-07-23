import importlib
import re
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]

# The only SOURCE (non-test) sys.path.insert calls allowed to remain after the
# packaging refactor. Each targets the EXTERNAL sibling dx-runtime (dx_engine /
# NPU libs / a separate compiler venv), not the studio tree, so the editable
# install cannot replace them. Everything else must resolve via `pip install -e .`.
_ALLOWED_SOURCE_SYSPATH_INSERT = {
    "dx_app/core/config.py",            # dx_engine/_pydxrt runtime site dirs
    "dx_monitor/core/hardware_init.py", # dx-runtime venv / dx_rt python package
    "dx_compiler/core/compile_worker.py",  # runs under the separate dx-compiler venv (no studio .pth)
}
_SKIP_DIRS = (".venv", "docs/.venv-docs", ".git")

def test_no_unexpected_source_syspath_insert():
    offenders = set()
    for p in REPO.rglob("*.py"):
        rel = p.relative_to(REPO).as_posix()
        if rel.startswith("tests/") or any(rel.startswith(d) or f"/{d}/" in f"/{rel}" for d in _SKIP_DIRS):
            continue
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if re.search(r"sys\.path\.insert\s*\(", line):
                if rel not in _ALLOWED_SOURCE_SYSPATH_INSERT:
                    offenders.add(rel)
                break
    assert not offenders, (
        "Unexpected source sys.path.insert (should resolve via editable install): "
        + ", ".join(sorted(offenders))
    )

def test_pyproject_exists():
    assert (REPO / "pyproject.toml").exists()

def test_core_subpackages_import_qualified():
    for app in ["dx_app","dx_modelzoo","dx_stream","dx_compiler",
                "dx_benchmark","dx_monitor","dx_planner","dx_agent_dev"]:
        assert importlib.import_module(f"{app}.core") is not None

def test_shared_importable():
    import shared  # noqa

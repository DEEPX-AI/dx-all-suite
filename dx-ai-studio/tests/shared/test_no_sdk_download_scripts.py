"""Studio never runs the SDK's sample download scripts (SR-847 / SR-848).

dx_stream's setup_sample_models.sh ignores a failed mkdir and reports it as a download failure
(SR-847); dx_app's download_models.py writes straight to the final path, so an interrupted run
leaves a truncated model that a re-run skips (SR-848). Both are SDK scripts that are already
being released, so Studio installs samples itself (shared/asset_setup.py over
shared/atomic_download.py) and reads those scripts only as declarations. This pins that no
product path executes them — or the SDK setup.sh wrappers that call them.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SDK_DOWNLOADERS = {"setup_sample_models.sh", "setup_sample_videos.sh", "download_models.py",
                   "setup_assets.py", "setup.sh"}
SKIP = {".venv", "var", "outputs", "tests", "node_modules", "__pycache__", "docs", "dx-agent-dev"}
# Reads the SDK declarations (BASE_URL, SOURCE_PATH, …) as text; never executes them.
DECLARATION_READERS = {"shared/asset_setup.py": {"setup_sample_models.sh", "setup_sample_videos.sh"}}


def _product_python():
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if SKIP & set(rel.parts[:-1]) or rel.parts[0] == "scripts":
            continue
        yield rel.as_posix(), path


def _bare_script_names(path):
    """String constants that are exactly an SDK script name (a path join / argv element),
    not prose such as a model card's "./setup_sample_models.sh --models X" instruction."""
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            name = node.value.strip().lstrip("./").rsplit("/", 1)[-1]
            if node.value.strip() in SDK_DOWNLOADERS or (
                    name in SDK_DOWNLOADERS and " " not in node.value.strip()):
                yield node.value.strip()


def test_no_product_code_names_an_sdk_download_script_to_run():
    offenders = {}
    for rel, path in _product_python():
        names = set(_bare_script_names(path)) - DECLARATION_READERS.get(rel, set())
        if names:
            offenders[rel] = sorted(names)
    assert not offenders, f"Studio code refers to SDK download scripts: {offenders}"


def test_the_declaration_reader_never_executes_what_it_reads(monkeypatch, tmp_path):
    import subprocess

    from shared import asset_setup
    from tests.shared.test_asset_setup import archive, opener, sdk

    def forbidden(*args, **kwargs):
        raise AssertionError(f"asset setup started a process: {args[:1]}")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, forbidden)
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    for component in ("app", "stream"):
        base = tmp_path / ("sdk-" + component)
        base.mkdir()
        root = sdk(base, component)
        asset_setup.install_assets(component, sdk_root=root, resource_root=base / "res",
                                   open_url=opener([], archive()))

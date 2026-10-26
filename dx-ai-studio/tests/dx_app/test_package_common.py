"""Model package export — a per-model package runs outside the Studio.

extract_model_package.sh trims common/ to static imports, but per-model examples name their processors in
config.json; a trimmed package dies with "processor class 'LetterboxPreprocessor' is exported by neither
common.processors nor common.visualizers".
"""
from __future__ import annotations

import pytest

from dx_app.core import package_common


def test_the_full_common_is_vendored_next_to_the_runner(tmp_path):
    common = tmp_path / "pkg" / "runtime/python/object_detection/m/common"
    (common / "processors").mkdir(parents=True)
    src = tmp_path / "dx_app/src/python_example/common/processors"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("from .letterbox_preprocessor import LetterboxPreprocessor\n")
    (src / "letterbox_preprocessor.py").write_text("class LetterboxPreprocessor: ...\n")
    package_common.complete_python_common(tmp_path / "dx_app", common.parent)
    assert (common / "processors/letterbox_preprocessor.py").read_text() == "class LetterboxPreprocessor: ...\n"


def test_a_symlink_in_common_is_refused(tmp_path):
    src = tmp_path / "dx_app/src/python_example/common"
    src.mkdir(parents=True)
    (src / "evil.py").symlink_to("/etc/passwd")
    (tmp_path / "pkg/common").mkdir(parents=True)
    with pytest.raises(ValueError):
        package_common.complete_python_common(tmp_path / "dx_app", tmp_path / "pkg")


def test_export_model_package_tars_the_per_model_folder_with_a_full_common(tmp_path, monkeypatch):
    """/api/extract writes outputs/py/<task>/<family>/<stem>/ and must look there, not for a folder named after the
    model directly under outputs/ (download_url would be empty); the packaged folder carries the full common/."""
    import subprocess
    import tarfile

    from dx_app.core import developer

    root = tmp_path / "dx_app"
    ex = root / "src/python_example/object_detection/yolo26/yolo26-n_640x640"
    ex.mkdir(parents=True)
    full = root / "src/python_example/common/processors"
    full.mkdir(parents=True)
    (full / "letterbox_preprocessor.py").write_text("class LetterboxPreprocessor: ...\n")
    (root / "scripts").mkdir()
    (root / "scripts/extract_model_package.sh").write_text("")
    out = tmp_path / "outputs"

    def fake_run(cmd, **kw):
        d = out / "py" / "object_detection/yolo26/yolo26-n_640x640"
        (d / "common/processors").mkdir(parents=True)
        (d / "yolo26-n_640x640_sync.py").write_text("")
        return subprocess.CompletedProcess(cmd, 0, "ok", "")

    for name, value in (("SCRIPTS_DIR", root / "scripts"), ("PY_DIR", root / "src/python_example"),
                        ("CPP_DIR", root / "src/cpp_example"), ("OUTPUTS_DIR", out), ("DX_APP_ROOT", root)):
        monkeypatch.setattr(developer, name, value)
    monkeypatch.setattr(developer.subprocess, "run", fake_run)
    out.mkdir()
    res = developer.extract_model_package("object_detection/yolo26/yolo26-n_640x640", "py")
    assert res["ok"] and res["download_url"], res
    with tarfile.open(out / res["download_url"].rsplit("/", 1)[-1]) as tar:
        names = tar.getnames()
    assert "py/yolo26-n_640x640/yolo26-n_640x640_sync.py" in names
    assert "py/yolo26-n_640x640/common/processors/letterbox_preprocessor.py" in names

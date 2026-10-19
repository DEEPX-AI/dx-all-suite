"""Builds a self-contained fake ``DX_APP_ROOT`` for the inference E2E triple gate.

Why a fake *root* instead of monkeypatching ``run_inference``
-------------------------------------------------------------
``dx_app.core.inference.run_inference`` resolves everything it needs from
``DX_APP_ROOT`` (model registry, ``.dxnn`` file, C++ binary, sample input) and
hands the annotated still back through the ``DXAPP_SAVE_IMAGE`` env var. All of
those are already env-overridable (``shared/paths.py``), so pointing
``DX_APP_ROOT`` at a fixture tree swaps ONLY the NPU binary: the real
``subprocess.Popen`` still runs, the real ``_parse_perf`` still parses, the real
result-image pipeline still base64-encodes, and the real ``/api/run`` route still
serves it.

Stubbing ``run_inference`` itself would have skipped all of that and the test
would have asserted against its own fixture data.

The fake binary is a plain POSIX shell script so it needs no interpreter
packages: it is exec'd directly by ``Popen`` and would otherwise inherit the
SYSTEM python (which has no Pillow), not the test venv.
"""
from __future__ import annotations

import os
from pathlib import Path

MODEL_NAME = "e2eyolo"
CATEGORY = "object_detection"
MODEL_FILE = f"assets/models/{MODEL_NAME}.dxnn"
SAMPLE_IMAGE = "sample/img/sample_street.jpg"

# Must satisfy dx_app/core/performance.py::_parse_perf:
#   - a line containing "PERFORMANCE SUMMARY" opens the block
#   - "<Step> <ms> ms <fps> FPS" rows feed the pipeline table
#   - "Overall FPS : <n>" -> res["fps"], "Inference <ms> ms" -> res["latency"]
#   - a trailing "=====" line closes the block
PERF_STDOUT = """\
[fake-runner] DX-RT stub — no NPU touched
===== PERFORMANCE SUMMARY =====
  Read           2.10 ms    476.2 FPS
  Preprocess     1.40 ms    714.3 FPS
  Inference      6.35 ms    157.5 FPS
  Postprocess    1.05 ms    952.4 FPS
  Total Frames : 1
  Total Time : 0.011 s
  Overall FPS : 92.6 FPS
===============================
"""

# Values the triple gate asserts on, derived from PERF_STDOUT above.
EXPECTED_FPS = 92.6
EXPECTED_LATENCY_MS = 6.35


def _write_jpeg(path: Path, *, boxes: bool) -> None:
    """Write a JPEG; with ``boxes=True`` draw detection rectangles + labels."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (640, 384), (38, 44, 56))
    d = ImageDraw.Draw(img)
    # A little structure so input and output are visually distinct files.
    d.rectangle([0, 300, 640, 384], fill=(60, 66, 80))
    if boxes:
        for xy, label in (
            ((48, 96, 232, 330), "person 0.94"),
            ((300, 150, 470, 300), "car 0.88"),
        ):
            d.rectangle(xy, outline=(99, 140, 255), width=4)
            d.text((xy[0] + 6, xy[1] + 6), label, fill=(255, 255, 255))
    img.save(path, "JPEG", quality=90)


def build(root: Path) -> Path:
    """Materialise the fixture tree at ``root`` and return it."""
    root = Path(root)
    for rel in ("assets/models", "config", "sample/img", "bin",
                f"src/cpp_example/{CATEGORY}/{MODEL_NAME}", "_fixture"):
        (root / rel).mkdir(parents=True, exist_ok=True)

    # get_models() only checks that <model>_sync.cpp exists to mark the model as
    # having a C++ runner; the file's contents are never read.
    (root / f"src/cpp_example/{CATEGORY}/{MODEL_NAME}/{MODEL_NAME}_sync.cpp").write_text(
        "// fixture placeholder\n", encoding="utf-8")

    # _required_dxnn_exists() checks existence only — never parses the container.
    (root / MODEL_FILE).write_bytes(b"DXNN\x00fixture-not-a-real-model\n")

    # Registry: <id>\t<category>\t<model_file>  (shared/catalog_sources.py)
    (root / "config/test_models.conf").write_text(
        "# fixture registry for the inference E2E triple gate\n"
        f"{MODEL_NAME}\t{CATEGORY}\t{MODEL_FILE}\n", encoding="utf-8")

    _write_jpeg(root / SAMPLE_IMAGE, boxes=False)
    annotated = root / "_fixture/annotated.jpg"
    _write_jpeg(annotated, boxes=True)

    binary = root / "bin" / f"{MODEL_NAME}_sync"
    binary.write_text(
        "#!/bin/sh\n"
        "# Fake DX-RT runner. Stands in for bin/<model>_sync so the full studio\n"
        "# path runs without an NPU. Ignores CLI args on purpose.\n"
        f'[ -n "$DXAPP_SAVE_IMAGE" ] && cp "{annotated}" "$DXAPP_SAVE_IMAGE"\n'
        "cat <<'PERF_EOF'\n"
        f"{PERF_STDOUT}"
        "PERF_EOF\n"
        "exit 0\n",
        encoding="utf-8")
    binary.chmod(0o755)
    return root


def activate(root: Path) -> None:
    """Point the studio at ``root``. MUST run before dx_app.core.config imports."""
    os.environ["DX_APP_ROOT"] = str(root)

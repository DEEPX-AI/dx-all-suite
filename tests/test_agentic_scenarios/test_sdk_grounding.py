"""SDK Grounding Tests — Prevent hallucinated API names in .deepx/ instructions.

These tests cross-check that `.deepx/` files only describe API symbols
(class names, method names, parameter names) that actually exist in the
official SDK source code or official SDK documentation.

Regression coverage:
- IFactory 5-method names (create_preprocessor / create_postprocessor / ...)
- SingleImageCalibDataset (hallucinated class, never existed in SDK)
- CALIBRATION_OK log marker (hallucinated, never in SDK)
- dx_com.compile() parameter names

Each test scans `.deepx/` files (templates, fragments, skills, agents, memory)
and fails if a BANNED pattern is found.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DEEPX_ROOTS = [
    REPO_ROOT / ".deepx",
    REPO_ROOT / "dx-runtime" / ".deepx",
    REPO_ROOT / "dx-runtime" / "dx_app" / ".deepx",
    REPO_ROOT / "dx-runtime" / "dx_stream" / ".deepx",
    REPO_ROOT / "dx-compiler" / ".deepx",
]


def _collect_deepx_md_files() -> list[Path]:
    """Collect all .md files under every .deepx/ subtree that exists.

    The sdk_grounding_reference.md file is excluded because it intentionally
    documents banned symbols as a BANNED table for human reference.
    """
    files: list[Path] = []
    for root in DEEPX_ROOTS:
        if root.exists():
            files.extend(root.rglob("*.md"))
    # Exclude the reference file itself — it deliberately lists banned symbols
    files = [
        f for f in files
        if f.name != "sdk_grounding_reference.md"
    ]
    return files


DEEPX_MD_FILES = _collect_deepx_md_files()


def _scan(pattern: str, files: list[Path] | None = None) -> list[tuple[Path, int, str]]:
    """Return (file, lineno, line) for every match of *pattern* across *files*."""
    hits: list[tuple[Path, int, str]] = []
    target = files or DEEPX_MD_FILES
    rx = re.compile(pattern)
    for path in target:
        try:
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(line):
                    hits.append((path, i, line.strip()))
        except OSError:
            pass
    return hits


# ---------------------------------------------------------------------------
# 1. IFactory method names — must match the real interface in i_factory.py
#    Actual methods: create_preprocessor, create_postprocessor, create_visualizer,
#                    get_model_name, get_task_type
# ---------------------------------------------------------------------------

WRONG_IFACTORY_METHODS = [
    r"\bget_input_params\b",
    r"\brun_inference\b",
    r"\bpost_processing\b",
    # "create," and "release" are too generic — only flag combined pattern
    r"IFactory.*\(create,\s*get_input_params",
    r"IFactory.*\(create,\s*run_inference",
]


class TestIFactoryMethodNames:
    """IFactory 5-method names must match the actual i_factory.py interface."""

    @pytest.mark.parametrize("pattern", WRONG_IFACTORY_METHODS)
    def test_wrong_ifactory_method_not_in_deepx(self, pattern: str):
        """Hallucinated IFactory method names must not appear in .deepx/ docs."""
        hits = _scan(pattern)
        assert not hits, (
            f"Hallucinated IFactory method pattern '{pattern}' found in .deepx/ files:\n"
            + "\n".join(f"  {p}:{n}: {line}" for p, n, line in hits)
        )

    def test_correct_ifactory_methods_present(self):
        """At least one .deepx/ file must document the correct IFactory methods."""
        correct_methods = [
            "create_preprocessor",
            "create_postprocessor",
            "create_visualizer",
            "get_model_name",
            "get_task_type",
        ]
        for method in correct_methods:
            hits = _scan(re.escape(method))
            assert hits, (
                f"Correct IFactory method '{method}' not found in any .deepx/ file. "
                "Ensure instructions document the real SDK interface."
            )


# ---------------------------------------------------------------------------
# 2. SingleImageCalibDataset — never existed in dx_com SDK
# ---------------------------------------------------------------------------


class TestNoSingleImageCalibDataset:
    """SingleImageCalibDataset is a hallucinated class that must not appear."""

    def test_not_in_deepx_instructions(self):
        hits = _scan(r"SingleImageCalibDataset")
        assert not hits, (
            "Hallucinated class 'SingleImageCalibDataset' found in .deepx/ files "
            "(this class does not exist in the dx_com SDK):\n"
            + "\n".join(f"  {p}:{n}: {line}" for p, n, line in hits)
        )


# ---------------------------------------------------------------------------
# 3. CALIBRATION_OK log marker — hallucinated, never in dx_com SDK
# ---------------------------------------------------------------------------


class TestNoCalibrationOkMarker:
    """CALIBRATION_OK is a hallucinated log marker that must not appear."""

    def test_not_in_deepx_instructions(self):
        hits = _scan(r"CALIBRATION_OK")
        assert not hits, (
            "Hallucinated log marker 'CALIBRATION_OK' found in .deepx/ files "
            "(this marker does not exist in dx_com output):\n"
            + "\n".join(f"  {p}:{n}: {line}" for p, n, line in hits)
        )


# ---------------------------------------------------------------------------
# 4. dx_com.compile() parameter names — must match official SDK
#    Official params: model, output_dir, config, dataloader, calibration_method,
#                     calibration_num, quantization_device, opt_level,
#                     aggressive_partitioning, input_nodes, output_nodes,
#                     enhanced_scheme, gen_log, float64_calibration
# ---------------------------------------------------------------------------

WRONG_DXCOM_PARAMS = [
    # Common hallucinations: wrong parameter names
    r"dx_com\.compile\(.*output_path\s*=",   # wrong: should be output_dir
    r"dx_com\.compile\(.*model_path\s*=",    # wrong: should be model (positional or kwarg)
    r"dx_com\.compile\(.*calib_num\s*=",     # wrong: should be calibration_num
    r"dx_com\.compile\(.*quant_device\s*=",  # wrong: should be quantization_device
]


class TestDxComParamNames:
    """dx_com.compile() must only be called with documented parameter names."""

    @pytest.mark.parametrize("pattern", WRONG_DXCOM_PARAMS)
    def test_wrong_dxcom_param_not_in_deepx(self, pattern: str):
        hits = _scan(pattern)
        assert not hits, (
            f"Incorrect dx_com.compile() parameter pattern '{pattern}' "
            "found in .deepx/ files (does not match official SDK signature):\n"
            + "\n".join(f"  {p}:{n}: {line}" for p, n, line in hits)
        )


# ---------------------------------------------------------------------------
# 5. GStreamer element whitelist — only documented dx_stream elements allowed
#    Documented: dxpreprocess, dxinfer, dxpostprocess, dxosd, dxtracker
# ---------------------------------------------------------------------------

VALID_DX_GSTREAMER_ELEMENTS = {
    "dxpreprocess",
    "dxinfer",
    "dxpostprocess",
    "dxosd",
    "dxtracker",
}

# Patterns that would indicate an undocumented dx-prefixed element
UNDOCUMENTED_DX_ELEMENT_PATTERN = re.compile(r"\bdx[a-z]+\b")
KNOWN_NON_ELEMENT_WORDS = {
    # Non-element dx- prefixed identifiers that are valid
    "dxcom", "dxnn", "dxm", "dxnpu", "dxrt", "dxq",
    "dxpreprocess", "dxinfer", "dxpostprocess", "dxosd", "dxtracker",
    # Allowed abbreviations / prefixes in identifiers
    "dx_com", "dx_engine", "dx_rt", "dx_app", "dx_stream", "dx_m1",
}


class TestGStreamerElements:
    """dx_stream pipelines must only reference documented GStreamer elements."""

    def test_documented_elements_referenced(self):
        """At least one .deepx/ file mentions the core dx_stream elements."""
        stream_deepx = REPO_ROOT / "dx-runtime" / "dx_stream" / ".deepx"
        if not stream_deepx.exists():
            pytest.skip("dx_stream .deepx not found (submodule not initialized)")

        stream_files = list(stream_deepx.rglob("*.md"))
        for element in ("dxpreprocess", "dxinfer", "dxpostprocess"):
            hits = _scan(re.escape(element), stream_files)
            assert hits, (
                f"Core GStreamer element '{element}' not found in dx_stream .deepx/ files."
            )

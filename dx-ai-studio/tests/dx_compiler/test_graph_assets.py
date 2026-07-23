"""Wave 1C – compiler graph asset stub remediation tests."""

import pathlib

import pytest

STATIC_JS = pathlib.Path(__file__).resolve().parents[2] / "dx_compiler" / "static" / "js"

GRAPH_ASSETS = ["graph_renderer.js", "graph_viewer.js", "dagre.min.js"]


class TestGraphAssetsAreNotWarningStubs:
    """Each shipped JS asset must be real code, not a one-line warning stub."""

    @pytest.mark.parametrize("filename", GRAPH_ASSETS)
    def test_no_stub_warning(self, filename: str) -> None:
        content = (STATIC_JS / filename).read_text()
        assert "shared assets not installed" not in content, (
            f"{filename} is still a stub warning"
        )

    @pytest.mark.parametrize("filename", GRAPH_ASSETS)
    def test_more_than_three_nonempty_lines(self, filename: str) -> None:
        lines = [
            line
            for line in (STATIC_JS / filename).read_text().splitlines()
            if line.strip()
        ]
        assert len(lines) > 3, (
            f"{filename} has only {len(lines)} non-empty lines — looks like a stub"
        )


class TestGraphAssetsDefineExpectedGlobals:
    """graph_renderer.js must define GraphRenderer; graph_viewer.js must define GraphViewer."""

    def test_graph_renderer_defines_global(self) -> None:
        content = (STATIC_JS / "graph_renderer.js").read_text()
        assert "window.GraphRenderer =" in content or "window.GraphRenderer=" in content, (
            "graph_renderer.js must assign window.GraphRenderer (not just mention it in comments)"
        )

    def test_graph_viewer_defines_global(self) -> None:
        content = (STATIC_JS / "graph_viewer.js").read_text()
        assert "window.GraphViewer =" in content or "window.GraphViewer=" in content, (
            "graph_viewer.js must assign window.GraphViewer (not just mention it in comments)"
        )


class TestDagreExposesExpectedGlobals:
    """dagre.min.js must expose window.dagre and bundle graphlib for runtime use."""

    def test_dagre_exposes_window_global(self) -> None:
        content = (STATIC_JS / "dagre.min.js").read_text()
        assert (
            "window.dagre" in content
            or ('if(typeof window!=="undefined"){g=window}' in content and "g.dagre=f()" in content)
        ), "dagre.min.js must expose dagre as a browser global"

    def test_dagre_includes_graphlib(self) -> None:
        content = (STATIC_JS / "dagre.min.js").read_text()
        assert "graphlib" in content.lower(), (
            "dagre.min.js must bundle graphlib (graph_renderer uses dagre.graphlib.Graph)"
        )

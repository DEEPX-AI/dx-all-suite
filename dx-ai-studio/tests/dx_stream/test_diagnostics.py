"""dx_stream Deep Diagnostics 11-check backend tests."""
from contextlib import ExitStack
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestDiagnostics(unittest.TestCase):
    CHECK_SPECS = (
        ("_check_pcie", "pcie_link", "blocker"),
        ("_check_dev_files", "dev_files", "blocker"),
        ("_check_kmod", "kmod", "blocker"),
        ("_check_dkms", "dkms", "blocker"),
        ("_check_dxrt_service", "dxrt_service", "blocker"),
        ("_check_gst_install", "gst_install", "blocker"),
        ("_check_gst_plugin", "gst_plugin", "blocker"),
        ("_check_gst_pipeline", "gst_pipeline_test", "blocker"),
        ("_check_webrtc", "webrtc_elements", "advisory"),
        ("_check_disk", "disk_space", "advisory"),
        ("_check_memory", "memory", "advisory"),
    )

    @staticmethod
    def _check_result(check_id, ok=True):
        return {
            "id": check_id,
            "label": {"en": check_id, "ko": check_id},
            "ok": ok,
            "detail": "ok" if ok else "failed",
            "fix": {"en": "fix", "ko": "fix"},
        }

    def test_returns_expected_structure(self):
        from dx_stream.core.diagnostics import deep_diagnostics

        result = deep_diagnostics()
        self.assertIn("all_ok", result)
        self.assertIn("passed", result)
        self.assertIn("total", result)
        self.assertIn("checks", result)
        self.assertEqual(result["total"], 11)
        self.assertEqual(len(result["checks"]), 11)

    def test_each_check_has_required_fields(self):
        from dx_stream.core.diagnostics import deep_diagnostics

        result = deep_diagnostics()
        for c in result["checks"]:
            self.assertIn("id", c)
            self.assertIn("label", c)
            self.assertIn("ok", c)
            self.assertIn("detail", c)
            self.assertIsInstance(c["label"], dict)
            self.assertIn("en", c["label"])
            self.assertIn("ko", c["label"])

    def test_check_ids_are_unique(self):
        from dx_stream.core.diagnostics import deep_diagnostics

        result = deep_diagnostics()
        ids = [c["id"] for c in result["checks"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_passed_count_matches(self):
        from dx_stream.core.diagnostics import deep_diagnostics

        result = deep_diagnostics()
        actual_passed = sum(1 for c in result["checks"] if c["ok"])
        self.assertEqual(result["passed"], actual_passed)

    def test_deep_diagnostics_records_one_check_exception_and_continues(self):
        from dx_stream.core import diagnostics

        def failing_pcie():
            raise RuntimeError("lspci missing")

        with patch.object(diagnostics, "_check_pcie", new=failing_pcie):
            result = diagnostics.deep_diagnostics()

        pcie = next(check for check in result["checks"] if check["id"] == "pcie_link")
        self.assertEqual(len(result["checks"]), result["total"])
        self.assertFalse(pcie["ok"])
        self.assertIn("lspci missing", pcie["detail"])
        self.assertEqual(pcie["severity"], "blocker")
        self.assertEqual(
            {check["id"] for check in result["checks"]},
            {check_id for _, check_id, _ in self.CHECK_SPECS},
        )

    def test_advisory_failure_is_visible_without_blocking_runtime(self):
        from dx_stream.core import diagnostics

        with ExitStack() as stack:
            for attribute, check_id, _severity in self.CHECK_SPECS:
                stack.enter_context(
                    patch.object(
                        diagnostics,
                        attribute,
                        new=lambda check_id=check_id: self._check_result(
                            check_id,
                            ok=check_id != "disk_space",
                        ),
                    )
                )
            result = diagnostics.deep_diagnostics()

        self.assertFalse(result["all_ok"])
        self.assertTrue(result["runtime_ready"])
        self.assertEqual(result["severity_summary"], {"blockers": 0, "advisories": 1})
        self.assertEqual(
            next(check for check in result["checks"] if check["id"] == "disk_space")["severity"],
            "advisory",
        )
        self.assertTrue(
            all(check["severity"] in {"blocker", "advisory"} for check in result["checks"])
        )

    def test_diagnostics_ui_renders_advisories_as_warnings(self):
        studio_root = Path(__file__).resolve().parents[2]
        setup_script = (studio_root / "dx_stream/static/js/stream-setup.js").read_text()
        stream_css = (studio_root / "dx_stream/static/css/stream.css").read_text()

        self.assertIn("runtime_ready", setup_script)
        self.assertIn("diag-card-warn", setup_script)
        self.assertIn(".diag-card-warn", stream_css)
        self.assertIn("DXStream.escHtml", setup_script)

    def test_gst_plugin_check_uses_the_dxinfer_element_factory(self):
        from dx_stream.core import diagnostics

        calls = []

        def fake_run(command, timeout=10):
            calls.append((command, timeout))
            return 0, "", ""

        with patch.object(diagnostics, "_run", new=fake_run):
            result = diagnostics._check_gst_plugin()

        self.assertTrue(result["ok"])
        self.assertEqual(
            calls,
            [(["gst-inspect-1.0", "--exists", "dxinfer"], 10)],
        )

    def test_gst_pipeline_check_parses_dxinfer_with_the_active_profile(self):
        from dx_stream.core import diagnostics
        from shared.runtime_contract import ContractResult

        context = SimpleNamespace(python_executable=Path("/runtime/bin/python3"))
        environment = {"GST_PLUGIN_PATH": "/runtime/gst"}
        captured = {}

        def fake_parse(pipeline, **kwargs):
            captured["pipeline"] = pipeline
            captured.update(kwargs)
            return ContractResult(())

        with (
            patch.object(
                diagnostics,
                "resolve_active_runtime_context",
                return_value=context,
                create=True,
            ),
            patch.object(
                diagnostics,
                "build_child_environment",
                return_value=environment,
                create=True,
            ),
            patch.object(
                diagnostics,
                "validate_stream_pipeline",
                side_effect=fake_parse,
                create=True,
            ),
        ):
            result = diagnostics._check_gst_pipeline()

        self.assertTrue(result["ok"])
        self.assertEqual(
            captured["pipeline"],
            "videotestsrc num-buffers=1 ! dxinfer ! fakesink",
        )
        self.assertEqual(captured["python_executable"], context.python_executable)
        self.assertEqual(captured["environment"], environment)


if __name__ == "__main__":
    unittest.main()

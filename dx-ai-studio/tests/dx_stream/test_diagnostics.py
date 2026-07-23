"""dx_stream Deep Diagnostics 11-check backend tests."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestDiagnostics(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

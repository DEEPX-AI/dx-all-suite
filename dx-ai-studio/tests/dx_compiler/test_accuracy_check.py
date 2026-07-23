"""F22: accuracy compare logic (pure numpy)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dx_compiler.core.accuracy_check import compare_outputs, summarize


class TestAccuracyCheck(unittest.TestCase):
    def test_identical_ok(self):
        r = compare_outputs([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        self.assertTrue(r["ok"])
        self.assertEqual(r["max_abs_diff"], 0.0)
        self.assertAlmostEqual(r["cosine"], 1.0, places=6)

    def test_small_diff_within_tol(self):
        r = compare_outputs([1.0, 2.0, 3.0], [1.001, 2.001, 3.001])
        self.assertTrue(r["ok"])
        self.assertTrue(r["within_tol"])

    def test_large_diff_fails(self):
        r = compare_outputs([1.0, 2.0, 3.0], [10.0, -5.0, 0.1])
        self.assertFalse(r["ok"])
        self.assertGreater(r["max_abs_diff"], 1.0)

    def test_shape_mismatch(self):
        r = compare_outputs([1.0, 2.0], [1.0, 2.0, 3.0])
        self.assertFalse(r["ok"])
        self.assertFalse(r["shape_match"])
        self.assertIn("shape mismatch", r["reason"])

    def test_high_cosine_passes_despite_scale(self):
        # same direction, slightly scaled -> cosine ~1 even if abs diff > tol
        r = compare_outputs([1.0, 2.0, 3.0], [1.05, 2.10, 3.15], rtol=1e-3, atol=1e-3)
        self.assertGreater(r["cosine"], 0.999)
        self.assertTrue(r["ok"])  # passes via cosine gate

    def test_summarize(self):
        # second pair diverges in direction (low cosine), so it must fail
        v = [compare_outputs([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]),
             compare_outputs([1.0, 2.0, 3.0], [3.0, -2.0, 1.0])]
        s = summarize(v)
        self.assertFalse(s["ok"])
        self.assertEqual(s["n"], 2)
        self.assertEqual(s["n_ok"], 1)

    def test_summarize_empty(self):
        self.assertFalse(summarize([])["ok"])


if __name__ == "__main__":
    unittest.main()

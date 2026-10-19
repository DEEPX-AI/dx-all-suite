"""Public ModelZoo adapter contracts.

Parsing itself is covered by tests/dx_modelzoo/test_public_payload_parser.py, against a
fixed copy of the real payload.

This file holds the **adapter contracts that do not depend on how parsing works**: the
injected fetch is used, and a dead network is reported as failure. Both stay valid when the
page changes again.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from dx_modelzoo.metadata.adapters import public_modelzoo_adapter

_FIXTURE = (Path(__file__).parent / "fixtures" / "public_modelzoo_payload.html").read_text(
    encoding="utf-8"
)


class TestPublicModelZooAdapter(unittest.TestCase):
    def test_adapter_uses_injected_fetch(self):
        r = public_modelzoo_adapter(".", fetch_text=lambda url: _FIXTURE)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(len(r["models"]), 8)

    def test_adapter_handles_fetch_failure(self):
        def boom(url):
            raise RuntimeError("network down")

        r = public_modelzoo_adapter(".", fetch_text=boom)
        self.assertFalse(r["ok"])
        self.assertTrue(r["errors"])

    def test_adapter_reports_a_shape_change_as_failure(self):
        """A changed page structure must be reported as failure, not as an empty catalog.

        Silent partial success is the worst case: a catalog with fewer models looks the
        same and passes through merge.
        """
        r = public_modelzoo_adapter(".", fetch_text=lambda url: "<html>no payload</html>")
        self.assertFalse(r["ok"])
        self.assertTrue(any("__MODEL_ZOO_DATA__" in e for e in r["errors"]), r["errors"])


if __name__ == "__main__":
    unittest.main()

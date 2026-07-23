#!/usr/bin/env python3
"""Vendor asset contract tests — shared/static/vendor/ integrity."""

import os
import unittest
from pathlib import Path

# dx-ai-studio repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_DIR = REPO_ROOT / "shared" / "static" / "vendor"

# Approved vendor files (whitelist)
APPROVED_VENDOR_FILES = {
    "chart.umd.min.js",
    "mermaid.min.js",
}

# Minimum size threshold (bytes) — guards against accidentally truncated files
CHART_MIN_SIZE = 5000
MERMAID_MIN_SIZE = 100_000


class TestChartVendorFile(unittest.TestCase):
    """chart.umd.min.js existence, size, and signature."""

    chart_path = VENDOR_DIR / "chart.umd.min.js"

    def test_chart_file_exists(self):
        self.assertTrue(
            self.chart_path.is_file(),
            f"chart.umd.min.js must exist at {self.chart_path}",
        )

    def test_chart_file_size_exceeds_minimum(self):
        size = self.chart_path.stat().st_size
        self.assertGreater(
            size,
            CHART_MIN_SIZE,
            f"chart.umd.min.js is {size} bytes, expected > {CHART_MIN_SIZE}",
        )

    def test_chart_file_contains_minichart_export_signature(self):
        content = self.chart_path.read_text(encoding="utf-8", errors="replace")
        self.assertIn("MiniChart", content)
        self.assertIn("global.Chart", content)
        self.assertIn("(function (global)", content)


class TestMermaidVendorFile(unittest.TestCase):
    """mermaid.min.js — Agent Dev markdown diagrams."""

    mermaid_path = VENDOR_DIR / "mermaid.min.js"

    def test_mermaid_file_exists(self):
        self.assertTrue(
            self.mermaid_path.is_file(),
            f"mermaid.min.js must exist at {self.mermaid_path}",
        )

    def test_mermaid_file_size_exceeds_minimum(self):
        size = self.mermaid_path.stat().st_size
        self.assertGreater(
            size,
            MERMAID_MIN_SIZE,
            f"mermaid.min.js is {size} bytes, expected > {MERMAID_MIN_SIZE}",
        )

    def test_mermaid_file_contains_mermaid_export(self):
        content = self.mermaid_path.read_text(encoding="utf-8", errors="replace")
        self.assertIn("mermaid", content.lower())


class TestNoUnapprovedVendorFiles(unittest.TestCase):
    """Only approved files may exist in vendor directory."""

    def test_no_unapproved_vendor_files(self):
        if not VENDOR_DIR.is_dir():
            self.skipTest("vendor directory does not exist")
        actual_files = {f.name for f in VENDOR_DIR.iterdir() if f.is_file()}
        unapproved = actual_files - APPROVED_VENDOR_FILES
        self.assertEqual(
            unapproved,
            set(),
            f"Unapproved vendor files found: {unapproved}",
        )


if __name__ == "__main__":
    unittest.main()

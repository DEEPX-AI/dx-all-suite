"""Tests for suggest-fix patch schema and rules."""

import unittest

from shared.chat.suggest_fix_schema import (
    apply_patches_to_form,
    validate_patch,
    validate_result,
)
from shared.chat.suggest_fix_rules import match_rules


class TestSuggestFixSchema(unittest.TestCase):
    def test_validate_opt_level_patch(self):
        p = validate_patch({
            "target": "form",
            "field": "opt_level",
            "action": "set",
            "value": 0,
            "reason": "timeout",
        })
        self.assertIsNotNone(p)
        self.assertEqual(p["value"], 0)

    def test_rejects_invalid_opt_level(self):
        p = validate_patch({
            "target": "form",
            "field": "opt_level",
            "action": "set",
            "value": 9,
            "reason": "x",
        })
        self.assertIsNone(p)

    def test_apply_patches_to_form(self):
        form = {"opt_level": 1, "aggressive_partitioning": False}
        patches = [validate_patch({
            "target": "form",
            "field": "opt_level",
            "action": "set",
            "value": 0,
            "reason": "slow",
        })]
        out = apply_patches_to_form(form, patches)
        self.assertEqual(out["opt_level"], 0)


class TestSuggestFixRules(unittest.TestCase):
    def test_timeout_suggests_lower_opt(self):
        result = match_rules("Compile timed out after 3600 seconds", "")
        self.assertIsNotNone(result)
        fields = [p["field"] for p in result["patches"]]
        self.assertIn("opt_level", fields)

    def test_subprocess_node_selection_rule(self):
        result = match_rules("node_selection_unsupported_subprocess", "")
        self.assertIsNotNone(result)
        self.assertTrue(any(p["field"] == "node_selection" for p in result["patches"]))

    # Phase A: autopilot only retries form/resume/dxq patches; config-class errors
    # must yield NO retryable patch (so the loop pauses instead of burning attempts).
    _RETRYABLE = {"form", "resume", "dxq"}

    def test_timeout_is_retryable(self):
        result = match_rules("Compile timed out after 3600 seconds", "")
        retryable = [p for p in result["patches"] if p["target"] in self._RETRYABLE]
        self.assertTrue(retryable, "timeout should produce a retryable form patch")

    def test_input_mismatch_is_not_retryable(self):
        result = match_rules("Input name not found: expected 'images'", "")
        self.assertIsNotNone(result)
        retryable = [p for p in result["patches"] if p["target"] in self._RETRYABLE]
        self.assertEqual(retryable, [], "config-class fix must not be auto-retryable")

    def test_no_placeholder_empty_inputs_patch(self):
        result = match_rules("input name mismatch", "")
        for p in result["patches"]:
            self.assertFalse(
                p.get("target") == "config_json" and p.get("field") == "inputs" and p.get("value") == {},
                "placeholder config_json inputs={} patch should be removed",
            )


class TestConfigPatch(unittest.TestCase):
    def test_apply_config_dataset_path(self):
        from shared.chat.config_patch import apply_config_patches
        cfg = {"inputs": {"x": [1, 3, 224, 224]}}
        out = apply_config_patches(cfg, [{
            "target": "config_json",
            "field": "dataset_path",
            "value": "/data/calib",
        }])
        self.assertEqual(out["default_loader"]["dataset_path"], "/data/calib")


if __name__ == "__main__":
    unittest.main()

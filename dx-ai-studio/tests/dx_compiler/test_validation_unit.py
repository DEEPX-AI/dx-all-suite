"""Unit contracts for the pure functions in validation.py.

Needed besides the HTTP tests (test_boundary_no_500.py): multipart fields are
**always strings**, so bool, int and None can never reach them through `/compile`.
Without coverage here those branches would be untested until a JSON endpoint
calls the same validators.
"""
from __future__ import annotations

import pytest

from dx_compiler.core.validation import (
    ValidationError, validate_fs_path, validate_opt_level,
)


class TestOptLevel:
    @pytest.mark.parametrize("raw, expected", [("0", 0), ("1", 1), (0, 0), (1, 1), (" 1 ", 1)])
    def test_documented_values_pass(self, raw, expected):
        assert validate_opt_level(raw) == expected

    def test_absent_means_the_documented_default(self):
        """The documented default is 1, the same as `fields.get("opt_level", "1")`."""
        assert validate_opt_level(None) == 1

    @pytest.mark.parametrize("raw", ["abc", "1.5", "", "   ", [], {}])
    def test_unparseable_is_refused(self, raw):
        with pytest.raises(ValidationError):
            validate_opt_level(raw)

    @pytest.mark.parametrize("raw", [-1, 2, 3, 999, "-5"])
    def test_outside_the_documented_range_is_refused(self, raw):
        with pytest.raises(ValidationError):
            validate_opt_level(raw)

    @pytest.mark.parametrize("raw", [True, False])
    def test_bool_is_refused(self, raw):
        """In Python True is an instance of int. Unless filtered first, True would
        silently pass as opt_level 1 and False as 0."""
        with pytest.raises(ValidationError):
            validate_opt_level(raw)

    @pytest.mark.parametrize("raw", ["", "   "])
    def test_an_empty_value_says_empty_not_quote_quote(self, raw):
        """An empty form field is the most common mistake. A message like
        `Invalid opt_level: ''` hardly tells the user what they left out.

        Without this contract the empty-value branch is dead code — `int("")` also
        raises ValueError, which the except below catches anyway. This pins what the
        branch actually does (the message), so mutation testing cannot remove it unnoticed.
        """
        with pytest.raises(ValidationError, match="empty"):
            validate_opt_level(raw)

    def test_the_message_says_what_is_allowed(self):
        """A 400 must say what is wrong; otherwise it is no better than a 500."""
        with pytest.raises(ValidationError, match=r"\[0, 1\]"):
            validate_opt_level("7")


class TestFsPath:
    def test_a_normal_path_passes_through_stripped(self):
        assert validate_fs_path("  /tmp/a.onnx ", "model_path") == "/tmp/a.onnx"

    @pytest.mark.parametrize("raw", [5, ["/tmp/a"], {"p": 1}, True, 1.5])
    def test_non_string_is_refused(self, raw):
        with pytest.raises(ValidationError, match="expected a path string"):
            validate_fs_path(raw, "model_path")

    @pytest.mark.parametrize("raw", [None, "", "   "])
    def test_empty_is_refused_when_required(self, raw):
        with pytest.raises(ValidationError, match="required"):
            validate_fs_path(raw, "model_path")

    @pytest.mark.parametrize("raw", [None, ""])
    def test_empty_is_allowed_when_optional(self, raw):
        assert validate_fs_path(raw, "dataset_path", required=False) == ""

    def test_the_message_names_the_field(self):
        """Without naming the wrong field, the user cannot fix it."""
        with pytest.raises(ValidationError, match="qxnn_path"):
            validate_fs_path(5, "qxnn_path")

    def test_the_path_target_is_not_inspected(self):
        """This function does not look at **where** a path points — only at its type.

        `is_safe_path` is a UX guardrail for the file browser, not a security boundary;
        applied to compile paths it would block a valid model on /media/usb.
        """
        assert validate_fs_path("/etc/passwd", "model_path") == "/etc/passwd"
        assert validate_fs_path("/media/usb/m.onnx", "model_path") == "/media/usb/m.onnx"

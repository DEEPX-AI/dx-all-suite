# SPDX-License-Identifier: Apache-2.0
"""Unit tests for parse_cursor_session._extract_cursor_tool_result.

These tests pin the per-tool-type result-extraction behavior so the parser
captures shell stdout, edit diff, and grep matches in addition to read content.
"""

from __future__ import annotations

# dx_transcripts is on PYTHONPATH=.deepx/tools/src (see tools/tests run command)
from dx_transcripts.parse_cursor_session import _extract_cursor_tool_result


def test_read_tool_extracts_content():
    tc_data = {
        "readToolCall": {
            "result": {"success": {"content": "file body line 1\nline 2"}}
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "read"
    assert "file body line 1" in result
    assert "line 2" in result


def test_shell_tool_extracts_stdout_and_stderr():
    tc_data = {
        "shellToolCall": {
            "result": {
                "success": {
                    "stdout": "hello\nworld\n",
                    "stderr": "warn: x\n",
                    "exitCode": 0,
                    "interleavedOutput": "hello\nwarn: x\nworld\n",
                }
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "shell"
    assert "hello" in result
    assert "world" in result
    assert "warn: x" in result


def test_shell_tool_falls_back_to_interleaved_when_stdout_empty():
    tc_data = {
        "shellToolCall": {
            "result": {
                "success": {
                    "stdout": "",
                    "stderr": "",
                    "interleavedOutput": "interleaved-only-output",
                    "exitCode": 0,
                }
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "shell"
    assert "interleaved-only-output" in result


def test_shell_tool_includes_nonzero_exit_code():
    tc_data = {
        "shellToolCall": {
            "result": {
                "success": {
                    "stdout": "boom",
                    "stderr": "",
                    "exitCode": 2,
                }
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "shell"
    assert "boom" in result
    assert "2" in result


def test_edit_tool_extracts_diff_string():
    tc_data = {
        "editToolCall": {
            "result": {
                "success": {
                    "path": "/tmp/foo.py",
                    "linesAdded": 3,
                    "linesRemoved": 1,
                    "diffString": "--- a/foo.py\n+++ b/foo.py\n@@\n-old\n+new\n",
                }
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "edit"
    assert "+new" in result
    assert "-old" in result
    assert "3" in result and "1" in result


def test_edit_tool_without_diff_falls_back_to_stats():
    tc_data = {
        "editToolCall": {
            "result": {
                "success": {
                    "path": "/tmp/foo.py",
                    "linesAdded": 5,
                    "linesRemoved": 0,
                }
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "edit"
    assert "/tmp/foo.py" in result
    assert "5" in result


def test_grep_tool_extracts_workspace_matches():
    tc_data = {
        "grepToolCall": {
            "result": {
                "success": {
                    "pattern": "foo",
                    "workspaceResults": {
                        "/repo": {
                            "content": {
                                "matches": [
                                    {
                                        "file": "a.py",
                                        "matches": [{"line": 10, "text": "foo bar"}],
                                    }
                                ]
                            }
                        }
                    },
                }
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "grep"
    assert "a.py" in result
    assert "foo bar" in result


def test_error_result_surfaces_error_message():
    tc_data = {
        "shellToolCall": {
            "result": {
                "error": "permission denied",
            }
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "shell"
    assert "permission denied" in result.lower()


def test_unknown_tool_falls_back_to_string_repr():
    tc_data = {
        "newToolCall": {
            "result": {"success": {"content": "x"}}
        }
    }
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "new"
    assert "x" in result


def test_empty_result_returns_empty_string():
    tc_data = {"shellToolCall": {"result": {"success": {}}}}
    name, result = _extract_cursor_tool_result(tc_data)
    assert name == "shell"
    assert result == ""

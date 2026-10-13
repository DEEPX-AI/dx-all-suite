# SPDX-License-Identifier: Apache-2.0
"""
Contract tests for the Claude Code hooks in ``.claude/hooks/``.

Claude Code passes tool input to a hook as a JSON document on **stdin**
(``tool_input.file_path``), not through environment variables.  Measured
against Claude Code 2.110.0 / agent-sdk 0.3.271 by instrumenting both hooks
and triggering a real Write tool call:

* ``CLAUDE_TOOL_INPUT_JSON`` and ``CLAUDE_FILE_PATHS`` are **not** present in
  the hook environment (``CLAUDE_PROJECT_DIR`` is).
* stdin carries ``{"hook_event_name": ..., "tool_name": ..., "tool_input":
  {"file_path": "<absolute path>", ...}}``.

A hook that reads the environment variables therefore never sees a path, and
the generator-output guard silently allows every edit (issue #186).

Feedback routing: a PreToolUse hook blocks with exit code 2 and the reason is
read from **stderr** — stdout is not surfaced to the agent.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

SUITE_ROOT = Path(__file__).resolve().parents[3]
HOOKS_DIR = SUITE_ROOT / ".claude" / "hooks"
GUARD = HOOKS_DIR / "pre-edit-generator-guard.sh"
POST = HOOKS_DIR / "post-edit-dx-agent-gen.sh"
SETTINGS = SUITE_ROOT / ".claude" / "settings.json"

# The guard only acts inside a tree that contains .deepx/, so these tests are
# meaningless without it: the "allowed" cases would pass vacuously while the
# blocking cases failed for an unrelated reason. Fail loudly instead — a suite
# checkout without .deepx/ is itself broken.
if not (SUITE_ROOT / ".deepx").is_dir():  # pragma: no cover - broken checkout
    raise RuntimeError(
        f"{SUITE_ROOT} has no .deepx/ — the hook guard is scoped to .deepx/ trees, "
        "so these contract tests cannot be interpreted here."
    )

# Paths the guard must refuse (Q2 of the Pre-flight Classification rule).
PROTECTED_PATHS = [
    ".claude/skills/dx-skill-router/SKILL.md",
    ".claude/agents/dx-suite-builder.md",
    ".github/agents/dx-suite-builder.agent.md",
    ".github/skills/dx-skill-router/SKILL.md",
    ".opencode/agents/dx-suite-builder.md",
    ".cursor/rules/dx-all-suite.mdc",
    "CLAUDE.md",
    "CLAUDE-KO.md",
    "AGENTS.md",
    "AGENTS-KO.md",
    ".github/copilot-instructions.md",
    ".github/copilot-instructions-KO.md",
]

# Paths the guard must let through (canonical sources and ordinary files).
ALLOWED_PATHS = [
    ".deepx/skills/dx-skill-router/SKILL.md",
    ".deepx/templates/fragments/en/output-isolation.md",
    "src/main.py",
    "docs/index.md",
    "README.md",
    "dx-runtime/dx_app/src/python_example/demo.py",
]


def _payload(file_path: str, event: str = "PreToolUse", tool: str = "Edit") -> str:
    return json.dumps(
        {
            "session_id": "test-session",
            "cwd": str(SUITE_ROOT),
            "hook_event_name": event,
            "tool_name": tool,
            "tool_input": {"file_path": file_path, "old_string": "a", "new_string": "b"},
        }
    )


def _run(script: Path, stdin: str | None, cwd: Path | None = None, env_extra=None):
    """Run a hook the way Claude Code does: JSON on stdin, no tool env vars."""
    import os

    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_")}
    env["CLAUDE_PROJECT_DIR"] = str(SUITE_ROOT)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(script)],
        input=stdin if stdin is not None else "",
        capture_output=True,
        text=True,
        # 60s: the post hook may run a real `dx-agent-gen check` over several repos.
        timeout=60,
        cwd=str(cwd or SUITE_ROOT),
        env=env,
    )


# ---------------------------------------------------------------------------
# pre-edit-generator-guard.sh — blocking behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rel", PROTECTED_PATHS)
def test_guard_blocks_generator_output_relative(rel):
    """A generator-output path on stdin must be refused with exit code 2."""
    proc = _run(GUARD, _payload(rel))
    assert proc.returncode == 2, (
        f"{rel}: expected exit 2 (block), got {proc.returncode}. "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )


@pytest.mark.parametrize("rel", PROTECTED_PATHS)
def test_guard_blocks_generator_output_absolute(rel):
    """Claude Code sends absolute paths — those must be refused too."""
    proc = _run(GUARD, _payload(str(SUITE_ROOT / rel)))
    assert proc.returncode == 2, (
        f"{rel}: absolute path not blocked (exit {proc.returncode})"
    )


@pytest.mark.parametrize("rel", PROTECTED_PATHS)
def test_guard_reason_goes_to_stderr(rel):
    """Exit-2 feedback reaches the agent through stderr, not stdout."""
    proc = _run(GUARD, _payload(rel))
    assert "BLOCKED" in proc.stderr, f"{rel}: no BLOCKED reason on stderr"
    assert proc.stdout.strip() == "", (
        f"{rel}: hook wrote to stdout ({proc.stdout!r}); PreToolUse feedback must use stderr"
    )


def test_guard_block_message_names_the_canonical_source():
    """The reason must tell the agent where to edit instead."""
    proc = _run(GUARD, _payload("CLAUDE.md"))
    assert ".deepx/" in proc.stderr
    assert "dx-agent-gen generate" in proc.stderr


@pytest.mark.parametrize("rel", ALLOWED_PATHS)
def test_guard_allows_non_generated_paths(rel):
    proc = _run(GUARD, _payload(rel))
    assert proc.returncode == 0, (
        f"{rel}: expected exit 0, got {proc.returncode}. stderr={proc.stderr!r}"
    )
    assert proc.stdout == "" and proc.stderr == "", (
        f"{rel}: allowed edit must be silent, got stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )


def test_guard_blocks_regardless_of_cwd(tmp_path):
    """The decision depends on the edited path, not on the shell's cwd."""
    proc = _run(GUARD, _payload(str(SUITE_ROOT / "CLAUDE.md")), cwd=tmp_path)
    assert proc.returncode == 2, f"cwd outside the repo broke the guard (exit {proc.returncode})"


# ---------------------------------------------------------------------------
# pre-edit-generator-guard.sh — degenerate input must not block or hang
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stdin",
    [
        pytest.param("", id="empty"),
        pytest.param("not json at all", id="malformed"),
        pytest.param("{}", id="empty-object"),
        pytest.param('{"tool_input":{}}', id="no-file-path"),
        pytest.param('{"tool_name":"Bash","tool_input":{"command":"ls"}}', id="other-tool"),
    ],
)
def test_guard_fails_open_on_degenerate_stdin(stdin):
    proc = _run(GUARD, stdin)
    assert proc.returncode == 0, f"degenerate stdin must not block (exit {proc.returncode})"


def test_guard_does_not_hang_without_stdin():
    """Run by hand from a terminal the hook must return instead of waiting on stdin."""
    import os

    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_")}
    proc = subprocess.run(
        ["bash", str(GUARD)],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        # 15s: this is the hang detector — the guard must return without stdin,
        # so anything beyond a moment means it is waiting on a read.
        timeout=15,
        cwd=str(SUITE_ROOT),
        env=env,
    )
    assert proc.returncode == 0


# ---------------------------------------------------------------------------
# post-edit-dx-agent-gen.sh
# ---------------------------------------------------------------------------


def test_post_hook_ignores_non_doc_edits():
    proc = _run(POST, _payload("src/main.py", event="PostToolUse"))
    assert proc.returncode == 0
    assert proc.stdout == "" and proc.stderr == ""


def test_post_hook_reads_stdin_and_reaches_the_drift_check():
    """A .md edit must get past path extraction (issue #186: it never did)."""
    proc = _run(
        POST,
        _payload("CLAUDE.md", event="PostToolUse"),
        env_extra={"PATH": "/usr/bin:/bin"},  # dx-agent-gen deliberately absent
    )
    assert proc.returncode == 0
    assert "dx-agent-gen" in proc.stderr, (
        "post hook never reached the drift check — path extraction still broken. "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )
    assert proc.stdout == "", "PostToolUse notices must go to stderr to reach the agent"


def _fake_gen_bin(tmp_path, check_exit: int):
    """A stand-in for dx-agent-gen that records whether `generate` was invoked."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    marker = tmp_path / "generate-was-called"
    fake = bindir / "dx-agent-gen"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        "case \"$1\" in\n"
        f"  check) exit {check_exit} ;;\n"
        f"  generate) echo called >> {marker} ; exit 0 ;;\n"
        "esac\n"
        "exit 0\n"
    )
    fake.chmod(0o755)
    return bindir, marker


def test_post_hook_reports_drift_without_touching_the_tree(tmp_path):
    """Drift detected → tell the agent on stderr, change nothing."""
    bindir, marker = _fake_gen_bin(tmp_path, check_exit=1)
    proc = _run(
        POST,
        _payload("CLAUDE.md", event="PostToolUse"),
        env_extra={"PATH": f"{bindir}:/usr/bin:/bin"},
    )
    assert not marker.exists(), "post hook ran `dx-agent-gen generate` — it must only warn"
    assert "drift" in proc.stderr.lower(), f"drift not reported on stderr: {proc.stderr!r}"
    assert "dx-agent-gen generate" in proc.stderr, "no manual fix command offered"
    assert proc.returncode == 2, (
        f"drift notice must reach the agent (exit 2), got {proc.returncode}"
    )


def test_post_hook_is_silent_when_there_is_no_drift(tmp_path):
    bindir, marker = _fake_gen_bin(tmp_path, check_exit=0)
    proc = _run(
        POST,
        _payload("CLAUDE.md", event="PostToolUse"),
        env_extra={"PATH": f"{bindir}:/usr/bin:/bin"},
    )
    assert proc.returncode == 0, f"clean tree must stay silent, got exit {proc.returncode}"
    assert proc.stdout == "" and proc.stderr == "", f"{proc.stdout!r} {proc.stderr!r}"
    assert not marker.exists()


def test_post_hook_warns_instead_of_auto_regenerating():
    """Policy: report drift, never mutate the tree behind the agent's back."""
    body = POST.read_text()
    executed = [
        line.strip()
        for line in body.splitlines()
        if "dx-agent-gen generate" in line and not line.lstrip().startswith(("#", "echo"))
    ]
    assert not executed, f"post hook must not run generate itself: {executed}"


# ---------------------------------------------------------------------------
# Static contract checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("script", [GUARD, POST])
def test_hooks_do_not_read_unset_tool_env_vars(script):
    """These variables do not exist in the hook environment (measured)."""
    body = script.read_text()
    for var in ("CLAUDE_TOOL_INPUT_JSON", "CLAUDE_FILE_PATHS"):
        assert f"${{{var}" not in body and f"${var}" not in body, (
            f"{script.name} still reads ${var}, which Claude Code never sets"
        )


@pytest.mark.parametrize("script", [GUARD, POST])
def test_hooks_are_syntactically_valid(script):
    proc = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_settings_invokes_hooks_through_project_dir():
    """cwd is not the project dir (measured), so relative hook paths are unsafe."""
    settings = json.loads(SETTINGS.read_text())
    commands = [
        hook["command"]
        for event in settings["hooks"].values()
        for matcher in event
        for hook in matcher["hooks"]
    ]
    assert commands, "no hook commands configured"
    for cmd in commands:
        assert "CLAUDE_PROJECT_DIR" in cmd, (
            f"hook command must be anchored to $CLAUDE_PROJECT_DIR: {cmd!r}"
        )
        # Unset the variable and the path becomes /.claude/hooks/... -> bash exits 127,
        # which PreToolUse treats as a non-blocking error: the guard would stop
        # protecting without saying so. A cwd fallback keeps the pre-fix behaviour.
        assert "${CLAUDE_PROJECT_DIR:-" in cmd, (
            f"hook command must fall back when CLAUDE_PROJECT_DIR is unset: {cmd!r}"
        )

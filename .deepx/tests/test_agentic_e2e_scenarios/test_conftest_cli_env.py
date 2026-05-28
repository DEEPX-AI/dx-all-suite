# SPDX-License-Identifier: Apache-2.0
"""Unit tests for _cli_env.agent_subprocess_env (PR1 — cert/SSL env injection).

Ensures node-based agent CLIs (claude-code / cursor / opencode / copilot) get
NODE_EXTRA_CA_CERTS + NODE_OPTIONS=--use-system-ca so the corporate/proxy root
CA is trusted. Without this, batches lose whole rounds to
"SSL certificate verification failed" / "unable to verify the first certificate".
"""
from __future__ import annotations

import sys
from pathlib import Path

# _cli_env lives in the tests/ dir alongside parse_*_session.py
_TESTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_TESTS_DIR))

import _cli_env  # noqa: E402


def test_helper_exists():
    assert hasattr(_cli_env, "agent_subprocess_env")
    assert hasattr(_cli_env, "SYSTEM_CA_BUNDLE")


def test_no_color_preserved():
    env = _cli_env.agent_subprocess_env()
    assert env.get("NO_COLOR") == "1"


def test_cert_bundle_injected_when_present(monkeypatch, tmp_path):
    fake_ca = tmp_path / "ca-certificates.crt"
    fake_ca.write_text("dummy")
    monkeypatch.setattr(_cli_env, "SYSTEM_CA_BUNDLE", str(fake_ca))
    env = _cli_env.agent_subprocess_env()
    assert env.get("NODE_EXTRA_CA_CERTS") == str(fake_ca)
    assert "--use-system-ca" in env.get("NODE_OPTIONS", "")


def test_no_cert_when_bundle_absent(monkeypatch):
    monkeypatch.setattr(_cli_env, "SYSTEM_CA_BUNDLE", "/nonexistent/ca.crt")
    env = _cli_env.agent_subprocess_env()
    assert env.get("NODE_EXTRA_CA_CERTS") != "/nonexistent/ca.crt"


def test_extra_overrides(monkeypatch, tmp_path):
    fake_ca = tmp_path / "ca.crt"
    fake_ca.write_text("x")
    monkeypatch.setattr(_cli_env, "SYSTEM_CA_BUNDLE", str(fake_ca))
    env = _cli_env.agent_subprocess_env({"FOO": "bar"})
    assert env.get("FOO") == "bar"
    assert env.get("NO_COLOR") == "1"
    assert env.get("NODE_EXTRA_CA_CERTS") == str(fake_ca)


def test_existing_node_options_appended(monkeypatch, tmp_path):
    fake_ca = tmp_path / "ca.crt"
    fake_ca.write_text("x")
    monkeypatch.setattr(_cli_env, "SYSTEM_CA_BUNDLE", str(fake_ca))
    monkeypatch.setenv("NODE_OPTIONS", "--max-old-space-size=4096")
    env = _cli_env.agent_subprocess_env()
    assert "--max-old-space-size=4096" in env["NODE_OPTIONS"]
    assert "--use-system-ca" in env["NODE_OPTIONS"]

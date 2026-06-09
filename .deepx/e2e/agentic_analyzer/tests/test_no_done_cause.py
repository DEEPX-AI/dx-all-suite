# SPDX-License-Identifier: Apache-2.0
"""Tests for lib.aggregate.classify_no_done_cause (T4)."""
from __future__ import annotations
import sys
from pathlib import Path
_ANALYZER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ANALYZER))

from lib.aggregate import classify_no_done_cause as c  # noqa: E402


def test_done_session_has_no_cause():
    assert c(has_done=True, env_failure_signature="", has_output_dirs=True, execution_score=85.0) == ""


def test_session_limit_is_env_rate_limit():
    assert c(has_done=False, env_failure_signature="rate-limit", has_output_dirs=False, execution_score=0.0) == "env-rate-limit"


def test_cert_is_env_cert():
    assert c(has_done=False, env_failure_signature="cert", has_output_dirs=True, execution_score=0.0) == "env-cert"


def test_codex_model_refresh_is_env_signature_prefixed():
    assert c(has_done=False, env_failure_signature="model-refresh-timeout", has_output_dirs=False, execution_score=0.0) == "env-model-refresh-timeout"


def test_real_artifacts_no_done_is_sentinel_omission():
    # codex R5 compiler: produced .dxnn + verify PASS, no DONE
    assert c(has_done=False, env_failure_signature="", has_output_dirs=True, execution_score=90.0) == "sentinel-omission"


def test_no_artifacts_no_done_is_planstop():
    # claude R5 dx_app: ran, result=success/end_turn, no captured artifacts, no DONE
    assert c(has_done=False, env_failure_signature="", has_output_dirs=False, execution_score=0.0) == "incomplete-planstop"


def test_artifacts_but_zero_execution_is_planstop():
    # has_output_dirs but execution_score==0 → still planstop (artifacts may be derived/stale)
    assert c(has_done=False, env_failure_signature="", has_output_dirs=True, execution_score=0.0) == "incomplete-planstop"

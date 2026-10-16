"""DX Cloud on a studio installed without the optional `aws` extra (no boto3, so no botocore either).

The page must still load and say how to install boto3; /api/aws/status answered 500 instead because the
session helper imported botocore before checking for boto3. Runs whether or not boto3 is installed.
"""
from __future__ import annotations

import sys

import pytest

from dx_edge.core import aws_compile as ac


@pytest.fixture()
def no_aws_sdk(monkeypatch):
    for name in ("boto3", "botocore", "botocore.exceptions"):
        monkeypatch.setitem(sys.modules, name, None)


def test_status_reports_boto3_missing_with_the_install_hint(no_aws_sdk):
    st = ac.status()
    assert st["boto3"] is False and st["profiles"] == []
    assert "pip install" in st["install_hint"]


def test_aws_calls_say_boto3_is_missing(no_aws_sdk):
    with pytest.raises(ac.AwsError) as exc:
        ac.list_stacks("", "ap-northeast-2")
    assert exc.value.status == 503 and "boto3" in exc.value.message

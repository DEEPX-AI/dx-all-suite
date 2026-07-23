"""Corporate TLS trust bridge: studio servers should point Python at the system CA
bundle (which holds a TLS-inspection proxy's root CA, e.g. FortiGate) when present, so
HTTPS downloads don't fail with CERTIFICATE_VERIFY_FAILED under certifi-only verification.
"""
import os

import shared.dx_server as dxs


def test_bridge_sets_ca_env_from_system_bundle(monkeypatch):
    monkeypatch.delenv("REQUESTS_CA_BUNDLE", raising=False)
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    bundle = "/etc/ssl/certs/ca-certificates.crt"
    monkeypatch.setattr(dxs.os.path, "isfile", lambda p: p == bundle)
    dxs._bridge_system_ca_trust()
    assert os.environ["REQUESTS_CA_BUNDLE"] == bundle
    assert os.environ["SSL_CERT_FILE"] == bundle


def test_bridge_does_not_override_explicit_env(monkeypatch):
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", "/custom/ca.pem")
    monkeypatch.setenv("SSL_CERT_FILE", "/custom/ca.pem")
    monkeypatch.setattr(dxs.os.path, "isfile", lambda p: True)
    dxs._bridge_system_ca_trust()
    assert os.environ["REQUESTS_CA_BUNDLE"] == "/custom/ca.pem"
    assert os.environ["SSL_CERT_FILE"] == "/custom/ca.pem"


def test_bridge_noop_when_no_system_bundle(monkeypatch):
    monkeypatch.delenv("REQUESTS_CA_BUNDLE", raising=False)
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    monkeypatch.setattr(dxs.os.path, "isfile", lambda p: False)
    dxs._bridge_system_ca_trust()
    assert "REQUESTS_CA_BUNDLE" not in os.environ
    assert "SSL_CERT_FILE" not in os.environ

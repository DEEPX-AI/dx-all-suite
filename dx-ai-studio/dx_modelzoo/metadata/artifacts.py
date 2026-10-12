"""Validation of artifact ids, paths and URLs."""
from __future__ import annotations

import ipaddress
from pathlib import Path
from urllib.parse import urlparse

from dx_modelzoo.metadata.schema import ARTIFACT_IDS


# Hosts allowed for the internal/public profiles
_ALLOWED_HOSTS = {
    "modelzoo-api.devops.dpx.ai",
    "modelzoo-publish-api.devops.dpx.ai",
    "sdk.deepx.ai",
}

# Internal infrastructure hosts — never expose their URLs directly, whatever the profile
_INTERNAL_HOSTS = {"modelzoo-api.devops.dpx.ai", "modelzoo-publish-api.devops.dpx.ai"}
_PUBLIC_HOSTS = {"sdk.deepx.ai"}
INTERNAL_HOSTS = _INTERNAL_HOSTS

# Local/private IP patterns (SSRF protection)
_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
_PRIVATE_PREFIXES = ("10.", "172.16.", "172.17.", "172.18.", "172.19.",
                     "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                     "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                     "172.30.", "172.31.", "192.168.")


def validate_artifact_id(artifact_id: str) -> str:
    """Validate an artifact id. Returns it unchanged if valid, otherwise raises ValueError."""
    if artifact_id in ARTIFACT_IDS:
        return artifact_id
    raise ValueError(f"unknown_artifact: {artifact_id!r}")


def safe_local_artifact_path(root: Path, relative_path: str) -> Path:
    """Validate a local artifact path. Only paths inside root are allowed."""
    root = Path(root).resolve()
    if relative_path.startswith("/"):
        raise ValueError(f"unsafe_artifact_path: {relative_path!r}")
    resolved = (root / relative_path).resolve()
    # Python 3.8-safe (Path.is_relative_to is 3.9+): decide with relative_to + ValueError.
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError("unsafe_artifact_path: resolved path escapes root")
    return resolved


def validate_remote_url(url: str, source_profile: str) -> bool:
    """Validate a remote URL against the allow list (SSRF protection).

    source_profile is kept for caller compatibility; validation is based on the host/IP policy.
    """
    _ = source_profile
    parsed = urlparse(url)

    # HTTPS only
    if parsed.scheme != "https":
        raise ValueError(f"unsafe_artifact_url: non-https scheme {parsed.scheme!r}")

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("unsafe_artifact_url: missing hostname")

    # Block private IPs/localhost
    if hostname in _BLOCKED_HOSTS:
        raise ValueError(f"unsafe_artifact_url: blocked host {hostname!r}")
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None
    if ip is not None:
        ip_targets = [ip]
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip_targets.append(ip.ipv4_mapped)
        for target in ip_targets:
            if (
                target.is_loopback
                or target.is_private
                or target.is_link_local
                or target.is_unspecified
            ):
                raise ValueError(f"unsafe_artifact_url: blocked ip {hostname!r}")
    for prefix in _PRIVATE_PREFIXES:
        if hostname.startswith(prefix):
            raise ValueError(f"unsafe_artifact_url: private IP {hostname!r}")

    # Check the allow list
    if hostname in _ALLOWED_HOSTS:
        return True

    raise ValueError(f"unsafe_artifact_url: unknown host {hostname!r}")


def resolve_artifact(model: dict, artifact_id: str, source_profile: str = "local",
                     local_root: Path | None = None) -> dict:
    """Look up a model's artifact info.

    Returns:
        {"available": bool, "type": "local"|"remote"|None,
         "path": str|None, "url": str|None, "error_code": str|None}
    """
    validate_artifact_id(artifact_id)

    artifacts = model.get("artifacts", {})
    art_info = artifacts.get(artifact_id, {})

    # Check the local path
    local_path = art_info.get("local_path")
    if local_path and local_root:
        try:
            resolved = safe_local_artifact_path(local_root, local_path)
            if resolved.exists():
                return {"available": True, "type": "local", "path": str(resolved),
                        "url": None, "error_code": None}
        except ValueError:
            return {"available": False, "type": None, "path": None,
                    "url": None, "error_code": "unsafe_artifact_path"}

    # Legacy model_file field (corresponds to qlite_dxnn)
    if artifact_id == "qlite_dxnn" and not local_path:
        model_file = model.get("model_file")
        if model_file and local_root:
            try:
                resolved = safe_local_artifact_path(local_root, model_file)
                if resolved.exists():
                    return {"available": True, "type": "local", "path": str(resolved),
                            "url": None, "error_code": None}
            except ValueError:
                pass

    # Check the remote URL
    remote_url = art_info.get("remote_url")
    if remote_url:
        try:
            validate_remote_url(remote_url, source_profile)
            # Never expose internal infrastructure URLs directly, whatever the profile
            hostname = (urlparse(remote_url).hostname or "").lower()
            if hostname in _INTERNAL_HOSTS:
                return {"available": False, "type": None, "path": None,
                        "url": None, "error_code": "artifact_unavailable"}
            return {"available": True, "type": "remote", "path": None,
                    "url": remote_url, "error_code": None}
        except ValueError:
            return {"available": False, "type": None, "path": None,
                    "url": None, "error_code": "unsafe_artifact_url"}

    return {"available": False, "type": None, "path": None,
            "url": None, "error_code": "artifact_unavailable"}

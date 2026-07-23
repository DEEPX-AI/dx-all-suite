"""아티팩트 ID/경로/URL 검증."""
from __future__ import annotations

import ipaddress
from pathlib import Path
from urllib.parse import urlparse

from dx_modelzoo.metadata.schema import ARTIFACT_IDS


# 내부/공개 프로필에서 허용하는 호스트 목록
_ALLOWED_HOSTS = {
    "modelzoo-api.devops.dpx.ai",
    "modelzoo-publish-api.devops.dpx.ai",
    "sdk.deepx.ai",
}

# 내부 인프라 호스트 — profile과 무관하게 URL 직접 노출 차단
_INTERNAL_HOSTS = {"modelzoo-api.devops.dpx.ai", "modelzoo-publish-api.devops.dpx.ai"}
_PUBLIC_HOSTS = {"sdk.deepx.ai"}
INTERNAL_HOSTS = _INTERNAL_HOSTS

# 로컬/사설 IP 패턴 (SSRF 방지)
_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
_PRIVATE_PREFIXES = ("10.", "172.16.", "172.17.", "172.18.", "172.19.",
                     "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                     "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                     "172.30.", "172.31.", "192.168.")


def validate_artifact_id(artifact_id: str) -> str:
    """아티팩트 ID 검증. 유효하면 그대로 반환, 아니면 ValueError."""
    if artifact_id in ARTIFACT_IDS:
        return artifact_id
    raise ValueError(f"unknown_artifact: {artifact_id!r}")


def safe_local_artifact_path(root: Path, relative_path: str) -> Path:
    """로컬 아티팩트 경로 검증. root 내부 경로만 허용."""
    root = Path(root).resolve()
    if relative_path.startswith("/"):
        raise ValueError(f"unsafe_artifact_path: {relative_path!r}")
    resolved = (root / relative_path).resolve()
    # Python 3.8-safe (Path.is_relative_to는 3.9+): relative_to + ValueError로 판정.
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError("unsafe_artifact_path: resolved path escapes root")
    return resolved


def validate_remote_url(url: str, source_profile: str) -> bool:
    """원격 URL 허용 목록 검증. SSRF 방지.

    source_profile는 호출부 호환성을 위해 유지하며, 현재 검증은 host/IP 정책 기반이다.
    """
    _ = source_profile
    parsed = urlparse(url)

    # HTTPS만 허용
    if parsed.scheme != "https":
        raise ValueError(f"unsafe_artifact_url: non-https scheme {parsed.scheme!r}")

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("unsafe_artifact_url: missing hostname")

    # 사설 IP/localhost 차단
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

    # 허용 목록 확인
    if hostname in _ALLOWED_HOSTS:
        return True

    raise ValueError(f"unsafe_artifact_url: unknown host {hostname!r}")


def resolve_artifact(model: dict, artifact_id: str, source_profile: str = "local",
                     local_root: Path | None = None) -> dict:
    """모델의 아티팩트 정보 조회.

    Returns:
        {"available": bool, "type": "local"|"remote"|None,
         "path": str|None, "url": str|None, "error_code": str|None}
    """
    validate_artifact_id(artifact_id)

    artifacts = model.get("artifacts", {})
    art_info = artifacts.get(artifact_id, {})

    # 로컬 경로 확인
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

    # 레거시 model_file 필드 (qlite_dxnn에 해당)
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

    # 원격 URL 확인
    remote_url = art_info.get("remote_url")
    if remote_url:
        try:
            validate_remote_url(remote_url, source_profile)
            # 내부 인프라 호스트는 profile과 무관하게 URL 직접 노출 차단
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

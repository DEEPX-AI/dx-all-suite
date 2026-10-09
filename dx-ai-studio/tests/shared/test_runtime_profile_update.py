"""scripts/runtime_profile_update.py — 한 dx-runtime 릴리즈 tag 로 runtime profile 을 만든다.

dx-runtime 은 릴리즈마다 올라가므로 (2.4.1 → 2.4.2 → …) profile 을 손으로 적지 않는다. tag 하나에서
revision · 구성 버전 · .deb 주소 · SHA-256 을 모두 읽는다. 네트워크는 fetch 함수로 바꿔 끼운다.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from scripts import runtime_profile_update as rpu

NOTES = """# RELEASE_NOTES

## DX-Runtime v9.9.1 / 2026-12-01

- DX_FW: v2.8.0
- NPU Driver: v2.7.0
- DX-RT: v3.6.1
- DX-Stream: v3.2.0
- DX-APP: v3.3.0
"""

DEB = {
    "libdxrt-bin_3.6.1_amd64.deb": b"amd64-bytes",
    "libdxrt-bin_3.6.1_arm64.deb": b"arm64-bytes",
    "dxrt-driver-dkms_2.7.0-2_all.deb": b"driver-bytes",
}


def fake_json(url):
    if url.endswith("/repos/DEEPX-AI/dx-runtime/commits/v9.9.1"):
        return {"sha": "runtimesha"}
    if url.endswith("/repos/DEEPX-AI/dx-all-suite/commits/v9.9.1"):
        return {"sha": "suitesha"}
    if url.endswith("/repos/DEEPX-AI/dx-runtime/contents/dx_rt?ref=v9.9.1"):
        return {"type": "submodule", "sha": "dxrtsha"}
    if url.endswith("/repos/DEEPX-AI/dx-runtime/contents/dx_rt_npu_linux_driver?ref=v9.9.1"):
        return {"type": "submodule", "sha": "drvsha"}
    if url.endswith("/repos/DEEPX-AI/dx_rt/contents/release/3.6.1?ref=dxrtsha"):
        return [{"name": n} for n in DEB if n.startswith("libdxrt")] + [{"name": "libdxrt-dev_3.6.1_amd64.deb"}]
    if url.endswith("/repos/DEEPX-AI/dx_rt_npu_linux_driver/contents/release/2.7.0?ref=drvsha"):
        return [{"name": "dxrt-driver-dkms_2.7.0-2_all.deb"}, {"name": "README.md"}]
    if url.endswith("/repos/DEEPX-AI/dx-runtime/releases/latest"):
        return {"tag_name": "v9.9.1"}
    raise AssertionError(url)


def fake_text(url):
    assert url.endswith("/DEEPX-AI/dx-runtime/v9.9.1/RELEASE_NOTES.md"), url
    return NOTES


def fake_bytes(url):
    return DEB[url.rsplit("/", 1)[1]]


def test_builds_a_profile_from_one_release_tag():
    version, profile = rpu.build_profile("v9.9.1", gstreamer_abi="1.20",
                                         fetch_json=fake_json, fetch_text=fake_text, fetch_bytes=fake_bytes)
    assert version == "9.9.1"
    assert profile["suite_revision"] == "suitesha" and profile["runtime_revision"] == "runtimesha"
    x86 = profile["architectures"]["x86_64"]
    assert x86["runtime"] == {
        "version": "3.6.1",
        "uri": "https://raw.githubusercontent.com/DEEPX-AI/dx_rt/dxrtsha/release/3.6.1/libdxrt-bin_3.6.1_amd64.deb",
        "sha256": hashlib.sha256(b"amd64-bytes").hexdigest(),
    }
    assert profile["architectures"]["aarch64"]["runtime"]["sha256"] == hashlib.sha256(b"arm64-bytes").hexdigest()
    assert x86["driver"]["uri"].endswith("/drvsha/release/2.7.0/dxrt-driver-dkms_2.7.0-2_all.deb")
    assert x86["driver"] == profile["architectures"]["aarch64"]["driver"]


def test_latest_tag_comes_from_the_github_release():
    assert rpu.latest_tag(fetch_json=fake_json) == "v9.9.1"


def test_writing_adds_the_profile_and_moves_the_target(tmp_path):
    path = tmp_path / "runtime_profiles.json"
    path.write_text(json.dumps({"schema_version": 1, "target_runtime_version": "2.4.1",
                                "profiles": {"2.4.1": {"gstreamer_abi": "1.20"}}}), encoding="utf-8")
    rpu.apply_profile(path, "9.9.1", {"gstreamer_abi": "1.20"}, set_target=True)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["target_runtime_version"] == "9.9.1"
    assert set(data["profiles"]) == {"2.4.1", "9.9.1"}


def test_missing_component_version_is_an_error():
    with pytest.raises(rpu.ProfileError):
        rpu.parse_component_versions("## DX-Runtime v1.0.0\n- DX-RT: v3.0.0\n")

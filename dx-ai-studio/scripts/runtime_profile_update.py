"""Build a config/runtime_profiles.json profile from one dx-runtime release tag.

dx-runtime moves forward every release (2.4.1 → 2.4.2 → …). Copying a profile's revisions, component versions,
.deb URLs and SHA-256 by hand is error-prone, so everything is read from that tag on GitHub:

- runtime_revision:   the tag commit in DEEPX-AI/dx-runtime
- suite_revision:     the commit of the same-named tag in DEEPX-AI/dx-all-suite
- component versions: the tag's RELEASE_NOTES.md ("DX-RT: v3.4.2", "NPU Driver: v2.6.0")
- .deb URLs:          release/<version>/ in the dx_rt and dx_rt_npu_linux_driver submodule commits the tag pins
- sha256:             computed by downloading that .deb

    python -m scripts.runtime_profile_update                 # only show the latest release
    python -m scripts.runtime_profile_update --tag v2.4.2 --write
    python -m scripts.runtime_profile_update --write --keep-target   # add the profile, keep the target

GITHUB_TOKEN is used for API requests when set (otherwise anonymous, 60 requests per hour).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "config" / "runtime_profiles.json"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
ORG = "DEEPX-AI"


class ProfileError(RuntimeError):
    pass


def _get(url: str, *, api: bool = False) -> bytes:
    headers = {"User-Agent": "dx-ai-studio-runtime-profile"}
    token = os.environ.get("GITHUB_TOKEN")
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=60) as resp:
        return resp.read()


def fetch_json(url: str):
    return json.loads(_get(url, api=True).decode("utf-8"))


def fetch_text(url: str) -> str:
    return _get(url).decode("utf-8")


def fetch_bytes(url: str) -> bytes:
    return _get(url)


def latest_tag(*, fetch_json=fetch_json) -> str:
    return fetch_json(f"{API}/repos/{ORG}/dx-runtime/releases/latest")["tag_name"]


def parse_component_versions(notes: str) -> dict:
    """Read the DX-RT and NPU Driver versions from the component list at the top of RELEASE_NOTES.md."""
    found = {}
    for key, pattern in (("runtime", r"^-\s*DX-RT:\s*v?([\d.]+)"), ("driver", r"^-\s*NPU Driver:\s*v?([\d.]+)")):
        m = re.search(pattern, notes, re.M)
        if not m:
            raise ProfileError(f"RELEASE_NOTES.md 에 {key} 버전 줄이 없다")
        found[key] = m.group(1)
    return found


def _submodule_sha(tag: str, path: str, fetch_json) -> str:
    entry = fetch_json(f"{API}/repos/{ORG}/dx-runtime/contents/{path}?ref={tag}")
    if not isinstance(entry, dict) or entry.get("type") != "submodule":
        raise ProfileError(f"{path} 는 {tag} 에서 submodule 이 아니다")
    return entry["sha"]


def _pick(names: list[str], pattern: str, what: str) -> str:
    hits = [n for n in names if re.fullmatch(pattern, n)]
    if len(hits) != 1:
        raise ProfileError(f"{what}: {pattern} 에 맞는 파일이 {len(hits)} 개 — {sorted(names)}")
    return hits[0]


def build_profile(tag: str, *, gstreamer_abi: str, fetch_json=fetch_json, fetch_text=fetch_text,
                  fetch_bytes=fetch_bytes) -> tuple[str, dict]:
    """tag (e.g. v2.4.2) → ("2.4.2", profile)."""
    version = tag.lstrip("v")
    runtime_rev = fetch_json(f"{API}/repos/{ORG}/dx-runtime/commits/{tag}")["sha"]
    suite_rev = fetch_json(f"{API}/repos/{ORG}/dx-all-suite/commits/{tag}")["sha"]
    comps = parse_component_versions(fetch_text(f"{RAW}/{ORG}/dx-runtime/{tag}/RELEASE_NOTES.md"))
    rt_sha = _submodule_sha(tag, "dx_rt", fetch_json)
    drv_sha = _submodule_sha(tag, "dx_rt_npu_linux_driver", fetch_json)

    rt_ver, drv_ver = comps["runtime"], comps["driver"]
    rt_files = [e["name"] for e in fetch_json(f"{API}/repos/{ORG}/dx_rt/contents/release/{rt_ver}?ref={rt_sha}")]
    drv_files = [e["name"] for e in fetch_json(
        f"{API}/repos/{ORG}/dx_rt_npu_linux_driver/contents/release/{drv_ver}?ref={drv_sha}")]

    def artifact(repo: str, sha: str, ver: str, name: str) -> dict:
        uri = f"{RAW}/{ORG}/{repo}/{sha}/release/{ver}/{name}"
        return {"version": ver, "uri": uri, "sha256": hashlib.sha256(fetch_bytes(uri)).hexdigest()}

    drv_name = _pick(drv_files, rf"dxrt-driver-dkms_{re.escape(drv_ver)}-\d+_all\.deb", "driver")
    driver = artifact("dx_rt_npu_linux_driver", drv_sha, drv_ver, drv_name)
    archs = {}
    for arch, deb_arch in (("x86_64", "amd64"), ("aarch64", "arm64")):
        name = _pick(rt_files, rf"libdxrt-bin_{re.escape(rt_ver)}_{deb_arch}\.deb", f"runtime {arch}")
        archs[arch] = {"runtime": artifact("dx_rt", rt_sha, rt_ver, name), "driver": dict(driver)}
    return version, {"gstreamer_abi": gstreamer_abi, "suite_revision": suite_rev,
                     "runtime_revision": runtime_rev, "architectures": archs}


def apply_profile(path: Path, version: str, profile: dict, *, set_target: bool) -> None:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    data["profiles"][version] = profile
    if set_target:
        data["target_runtime_version"] = version
    out = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(out + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tag", help="dx-runtime 릴리즈 tag (기본: GitHub 최신 릴리즈)")
    ap.add_argument("--write", action="store_true", help="config/runtime_profiles.json 에 쓴다")
    ap.add_argument("--keep-target", action="store_true", help="target_runtime_version 은 그대로 둔다")
    ap.add_argument("--profiles", type=Path, default=PROFILES)
    args = ap.parse_args(argv)

    data = json.loads(args.profiles.read_text(encoding="utf-8"))
    last = data["profiles"][sorted(data["profiles"], key=lambda v: tuple(int(x) for x in v.split(".")))[-1]]
    tag = args.tag or latest_tag()
    version, profile = build_profile(tag, gstreamer_abi=last.get("gstreamer_abi", "1.20"))
    print(json.dumps({version: profile}, indent=2))
    if args.write:
        apply_profile(args.profiles, version, profile, set_target=not args.keep_target)
        print(f"wrote {args.profiles} (target {'kept' if args.keep_target else version})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

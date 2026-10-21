"""Safe Studio sample setup: ``python -m shared.asset_setup app|stream [--model NAME]``."""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import ssl
import sys
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

from shared import dxrt
from shared.atomic_download import (
    DownloadCancelled, asset_file_status, download_file, prepare_directory,
    publish_stream, write_metadata,
)
from shared.paths import DX_APP_ROOT, SUITE_ROOT


def _name(value, label="Model"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+ -]{0,254}", value):
        raise ValueError("{} name is unsafe or too long: {!r}".format(label, value))
    return value


def _url_filename(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Unsupported asset URL: {}".format(url))
    return _name(unquote(parsed.path.rsplit("/", 1)[-1]), "Asset")


def _redact_urls(message):
    def redact(match):
        url = match.group(0).split("?", 1)[0].split("#", 1)[0]
        scheme, _, rest = url.partition("://")
        host, slash, path = rest.partition("/")
        return "{}://{}{}{}".format(scheme, host.rsplit("@", 1)[-1], slash, path)
    return re.sub(r"https?://[^\s<>\"]+", redact, message, flags=re.I)


def _declaration(script, name, values=None):
    """Read only quoted SDK constants, never source/execute shell or expand commands."""
    text = script.read_text(encoding="utf-8")
    match = re.search(r"^" + re.escape(name) + r"""=(["'])([^\r\n]*?)\1\s*$""", text, re.M)
    if match is None:
        raise ValueError("Unsupported SDK declaration {} in {}".format(name, script))
    value = match.group(2)
    for key, replacement in (values or {}).items():
        value = value.replace("${" + key + "}", replacement)
    if any(char in value for char in ("$", "`", "\n")):
        raise ValueError("Unsupported SDK expansion {} in {}".format(name, script))
    return value


def demo_model_files(root):
    """The .dxnn files dx_app's run_demo.sh launches (its quoted ``DEMO_MODEL=( … )`` array).

    Read as text, like build.sh's own resolver (scripts/build_target_resolver.sh) — never sourced
    or executed. Quick Start downloads and requires only this set.
    """
    script = Path(root) / "run_demo.sh"
    try:
        text = script.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError("Demo model list unavailable: {} ({})".format(script, exc)) from exc
    match = re.search(r"^DEMO_MODEL=\(\s*$(.*?)^\)", text, re.M | re.S)
    if match is None:
        raise ValueError("Demo model list unavailable: no DEMO_MODEL array in {}".format(script))
    names = []
    for line in match.group(1).splitlines():
        line = line.split("#", 1)[0].strip()
        for token in line.split():
            token = token.strip("\"'")
            if token:
                names.append(_name(token))
    if not names:
        raise ValueError("Demo model list unavailable: DEMO_MODEL is empty in {}".format(script))
    return list(dict.fromkeys(names))


def demo_video_files(root):
    """The videos dx_app's run_demo.sh plays (its ``DEMO_VIDEO=( … )`` array), relative to assets/videos.

    Read as text like DEMO_MODEL. Empty entries (image-only demos) and other folders are left out; a tree
    without the array (an older dx_app, dx_stream) names none.
    """
    try:
        text = (Path(root) / "run_demo.sh").read_text(encoding="utf-8")
    except OSError:
        return []
    match = re.search(r"^DEMO_VIDEO=\(\s*$(.*?)^\)", text, re.M | re.S)
    if match is None:
        return []
    names = []
    for line in match.group(1).splitlines():
        token = line.split("#", 1)[0].strip().strip("\"'")
        if token.startswith("assets/videos/") and ".." not in PurePosixPath(token).parts:
            names.append(token[len("assets/videos/"):])
    return list(dict.fromkeys(names))


def _model_tasks(component, root, model, demo=False):
    if model is not None:
        _name(model)
    demo_files = set(demo_model_files(root)) if demo and component == "app" else None
    if component == "stream":
        manifest = json.loads((root / "model_list.json").read_text(encoding="utf-8"))
        version = _name(manifest["version"], "Version")
        names = manifest["models"]
        if not isinstance(names, list) or not names:
            raise ValueError("Model manifest is empty or invalid")
        base = _declaration(root / "setup_sample_models.sh", "BASE_URL")
        tasks = [(_name(name), base.rstrip("/") + "/" + version + "/" + _name(name), None)
                 for name in names]
        if model is not None:
            tasks = [task for task in tasks if task[0] == model]
        target_suffix = "models-" + version
    else:
        manifest = json.loads((root / "scripts" / "modelzoo_manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, list) or not manifest:
            raise ValueError("Model manifest is empty or invalid")
        tasks = []
        for entry in manifest:
            filename = _url_filename(entry["dxnn_url"])
            if demo_files is not None and filename not in demo_files:
                continue
            if model is not None and model.lower() not in (
                    entry["name"].lower(), filename.lower(), Path(filename).stem.lower()):
                continue
            tasks.append((filename, entry["dxnn_url"], entry.get("dxnn_sha256")))
            if entry.get("json_url"):
                tasks.append((_url_filename(entry["json_url"]), entry["json_url"], entry.get("json_sha256")))
        target_suffix = ""
    if not tasks:
        raise ValueError("Model {!r} is not in the SDK manifest".format(model))
    for name, url, digest in tasks:
        if _url_filename(url) != name:
            raise ValueError("Model filename/URL mismatch: {}".format(name))
    return list(dict.fromkeys(tasks)), target_suffix


def _video_contract(root):
    script = root / "setup_sample_videos.sh"
    source_text = script.read_text(encoding="utf-8")
    values = {}
    if "${VIDEO_VERSION}" in source_text:
        values["VIDEO_VERSION"] = _name(_declaration(script, "VIDEO_VERSION"), "Version")
    source = _declaration(script, "SOURCE_PATH", values)
    url = _declaration(script, "BASE_URL").rstrip("/") + "/" + source
    filename = _url_filename(url)
    if not filename.endswith(".tar.gz"):
        raise ValueError("Unsupported SDK video archive: {}".format(source))
    return url, filename, filename[:-7]


def validate_stream_model(root, name):
    """Validate a single-model request before Studio reserves a setup worker."""
    _name(name)
    _model_tasks("stream", Path(root), name)


def _layout(output, expected):
    if output.is_symlink():
        if output.resolve() != expected.resolve():
            raise OSError("Refusing to repoint existing symlink {} -> {}; expected {}. "
                          "Choose or fix the destination explicitly.".format(output, os.readlink(output), expected))
        target = expected
    elif output.exists():
        if not output.is_dir():
            raise OSError("Asset path is not a directory: {}".format(output))
        target = output
    else:
        target = expected
    prepare_directory(output.parent)
    prepare_directory(target)
    return target


def _link(output, target):
    if output.is_symlink():
        if output.resolve() != target.resolve():
            raise OSError("Asset symlink changed during setup: {}".format(output))
    elif not output.exists():
        output.symlink_to(target.resolve(), target_is_directory=True)


def _archive_members(tar):
    files = []
    for member in tar.getmembers():
        parts = PurePosixPath(member.name).parts
        if (member.name.startswith("/") or "\\" in member.name or ".." in parts or ".studio-assets" in parts
                or not (member.isdir() or member.isfile())):
            raise ValueError("Archive contains unsafe member: {}".format(member.name))
        if member.isfile():
            if not parts or member.size <= 0:
                raise ValueError("Archive contains empty/invalid file: {}".format(member.name))
            files.append((member, parts))
    if not files or not any(Path(m.name).suffix.lower() in (".mp4", ".mov", ".avi", ".mkv") for m, _ in files):
        raise ValueError("Archive has no sample videos")
    # SDK get_resource.sh strips one shared top-level directory. App also
    # flattens a sole media subdirectory; repeat only while every file shares it.
    while all(len(parts) > 1 for _, parts in files) and len({parts[0] for _, parts in files}) == 1:
        files = [(member, parts[1:]) for member, parts in files]
    names = [parts for _, parts in files]
    if len(set(names)) != len(names):
        raise ValueError("Archive contains duplicate destinations")
    return files


def _validate_archive(path):
    with tarfile.open(str(path), "r:gz") as tar:
        _archive_members(tar)


def _extract_videos(archive, target, cancel):
    with tarfile.open(str(archive), "r:gz") as tar:
        files = _archive_members(tar)
        for member, parts in files:
            destination = target.joinpath(*parts)
            for parent in [destination] + list(destination.parents):
                if parent == target:
                    break
                if parent.is_symlink():
                    raise OSError("Archive destination is a symlink: {}".format(parent))
        for member, parts in files:
            with tar.extractfile(member) as source:
                publish_stream(source, target.joinpath(*parts), member.size, cancel=cancel,
                               verification="archive-member-size")
        if cancel is not None and cancel():
            raise DownloadCancelled("Asset setup cancelled")
        write_metadata(target / ".studio-assets" / "sample-videos.json", {
            "version": 1, "archive": archive.name,
            "files": [str(PurePosixPath(*parts)) for _, parts in files],
        })


def _open_url(url):
    ca = next((os.environ[key] for key in ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE")
               if os.environ.get(key)), None)
    context = ssl.create_default_context(cafile=ca)
    if os.environ.get("DXAPP_TLS_RELAX_X509_STRICT") == "1" and hasattr(ssl, "VERIFY_X509_STRICT"):
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
    request = urllib.request.Request(url, headers={
        "Accept-Encoding": "identity", "User-Agent": "DX-Studio-Assets/1.0"})
    return opener.open(request, timeout=120)


def _compatible_model(path):
    needed = dxrt.needs_for_file(path)
    if needed:
        raise OSError("DX-RT {} required for {}".format(needed, path.name))


def _roots(component, sdk_root, resource_root):
    if component not in ("app", "stream"):
        raise ValueError("Unknown asset component: {}".format(component))
    root = Path(sdk_root) if sdk_root is not None else (
        DX_APP_ROOT if component == "app" else Path(os.environ.get(
            "DX_STREAM_ROOT", str(SUITE_ROOT / "dx-runtime" / "dx_stream"))))
    resources = Path(resource_root) if resource_root is not None else (
        Path(os.environ["DOCKER_VOLUME_PATH"]) / "res" if os.environ.get("DOCKER_VOLUME_PATH")
        else SUITE_ROOT / "workspace" / "res")
    output = root / ("assets" if component == "app" else "dx_stream/samples")
    return root, resources, output


def _models_location(component, output, resources, suffix):
    model_output = output / "models"
    model_expected = resources / "models" / suffix if suffix else resources / "models"
    if component == "app" and os.environ.get("DX_APP_MODELS_DIR"):
        model_output = Path(os.environ["DX_APP_MODELS_DIR"])
        model_expected = model_output.resolve()
    return model_output, model_expected


def _local_group(files):
    """Count files as verified / unverified (present, no current Studio record) / missing.

    ``ok`` means nothing is missing — a present file is installed whether or not Studio
    recorded its transfer. ``verified`` additionally needs every record; running the step
    again checks an unverified file's size against the server and records it in place.
    """
    result = {"ok": False, "verified": 0, "unverified": 0, "missing": 0, "total": len(files)}
    for path in files:
        result[asset_file_status(path)["state"]] += 1
    result["ok"] = result["total"] > 0 and result["missing"] == 0
    result["all_verified"] = result["total"] > 0 and result["verified"] == result["total"]
    return result


_VIDEO_SUFFIXES = (".mp4", ".mov", ".avi", ".mkv")


def _inventory_files(videos, inventory, filename):
    if (inventory.is_symlink() or inventory.parent.is_symlink()
            or inventory.stat().st_size > 1024 * 1024):
        raise ValueError("Unverified sample video inventory: {}".format(inventory))
    data = json.loads(inventory.read_text(encoding="utf-8"))
    names = data.get("files")
    if (data.get("version") != 1 or data.get("archive") != filename
            or not isinstance(names, list) or not names):
        raise ValueError("Unverified sample video inventory: {}".format(inventory))
    files = []
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or ".studio-assets" in path.parts or "\\" in name:
            raise ValueError("Unsafe sample video inventory")
        files.append(videos.joinpath(*path.parts))
    return files


def _legacy_videos(videos, required=()):
    """Present media files without a Studio inventory: all unverified (an empty folder: missing).

    Without an inventory nothing says which files the archive held, so a half-extracted folder would look
    complete. ``required`` (the videos the demos play) must all be there; each one absent counts as missing.
    """
    found = sorted(path for path in (videos.rglob("*") if videos.is_dir() else [])
                   if path.is_file() and path.suffix.lower() in _VIDEO_SUFFIXES
                   and ".studio-assets" not in path.parts)
    absent = [name for name in required if not videos.joinpath(*PurePosixPath(name).parts).is_file()]
    group = _local_group(found)
    group.update(unverified=group["unverified"] + group["verified"], verified=0, all_verified=False)
    if not found and not absent:
        group.update(missing=1, total=1)   # the archive is the unit when nothing is there
    elif absent:
        group.update(missing=len(absent), total=group["total"] + len(absent), ok=False, all_verified=False,
                     absent=absent)
    return group


def _group_detail(label, group):
    text = "{} {}/{}".format(label, group["total"] - group["missing"], group["total"])
    if group["unverified"]:
        text += " ({} unverified)".format(group["unverified"])
    return text


def sample_assets_status(component, sdk_root=None, resource_root=None):
    """Local-only Setup/Quick Start readiness.

    ``ok``: every manifest artifact (models, JSON sidecars) and every video is present.
    ``demo_ok`` (app): the same for the run_demo.sh demo set Quick Start installs.
    ``verified``: every present file also has a current Studio completion record; a file
    without one is reported as unverified, never as missing, and is not re-downloaded for
    that alone (running the step verifies it by Content-Length).
    Video inventory is written only after every archive member completed. Polls read small
    JSON receipts and stat identities, never remote HEAD/GET or full-file hashes.
    """
    result = {"ok": False, "demo_ok": False, "verified": False,
              "models": _local_group([]), "videos": _local_group([])}
    try:
        root, resources, output = _roots(component, sdk_root, resource_root)
        tasks, suffix = _model_tasks(component, root, None)
        model_output, expected = _models_location(component, output, resources, suffix)
        if model_output.is_symlink() and model_output.resolve() != expected.resolve():
            raise OSError("Conflicting model symlink: {}".format(model_output))
        result["models"] = _local_group([model_output / name for name, _, _ in tasks])
        demo_models = result["models"]
        if component == "app":
            try:
                demo_tasks, _ = _model_tasks(component, root, None, demo=True)
                demo_models = _local_group([model_output / name for name, _, _ in demo_tasks])
            except ValueError as exc:
                demo_models = dict(_local_group([]), error=str(exc))
        result["demo_models"] = demo_models
        _, filename, video_suffix = _video_contract(root)
        videos = output / "videos"
        if videos.is_symlink() and videos.resolve() != (resources / "videos" / video_suffix).resolve():
            raise OSError("Conflicting video symlink: {}".format(videos))
        inventory = videos / ".studio-assets" / "sample-videos.json"
        if not inventory.exists() and not inventory.is_symlink():
            # Videos another installer (the SDK's setup_sample_videos.sh) extracted carry no Studio
            # inventory: the media files present are unverified, not missing.
            result["videos"] = _legacy_videos(videos, demo_video_files(root) if component == "app" else ())
        else:
            result["videos"] = _local_group(_inventory_files(videos, inventory, filename))
        result["ok"] = result["models"]["ok"] and result["videos"]["ok"]
        result["demo_ok"] = demo_models["ok"] and result["videos"]["ok"]
        result["verified"] = result["models"]["all_verified"] and result["videos"]["all_verified"]
        # Short facts joined by " · " (the Setup step list shows each one; setup.js translates them).
        facts = [_group_detail("models", result["models"]), _group_detail("videos", result["videos"])]
        if component == "app":
            facts.insert(0, _group_detail("demo models", demo_models))
        result["detail"] = " · ".join(facts)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result["detail"] = "Unverified sample assets: {}".format(exc)
    return result


def install_assets(component, model=None, *, demo=False, sdk_root=None, resource_root=None,
                   open_url=None, cancel=None, log=print):
    """Install bundled SDK manifests, preserving directories and conflicting user links.

    ``demo`` (app) installs only the run_demo.sh demo models plus the sample videos (Quick Start).
    """
    root, resources, output = _roots(component, sdk_root, resource_root)
    tasks, suffix = _model_tasks(component, root, model, demo=demo)
    model_output, model_expected = _models_location(component, output, resources, suffix)
    models = _layout(model_output, model_expected)
    if model is None:
        video_url, video_filename, video_suffix = _video_contract(root)
        videos = _layout(output / "videos", resources / "videos" / video_suffix)
        archive = resources / "videos" / "download" / video_filename
        prepare_directory(archive.parent)
    for index, (name, url, digest) in enumerate(tasks, 1):
        log("Downloading {}/{} {}".format(index, len(tasks), name), flush=True)
        destination = models / name
        urls = dxrt.download_urls(url)
        for attempt, candidate in enumerate(urls):
            try:
                result = download_file(candidate, destination, open_url=open_url or _open_url,
                                       sha256=digest, cancel=cancel,
                                       skip_existing=not (name.endswith(".dxnn") and dxrt.needs_for_file(destination)),
                                       validate=_compatible_model if name.endswith(".dxnn") else None)
                break
            except DownloadCancelled:
                raise
            except OSError as error:
                log(_redact_urls("Download attempt {}/{} failed for {}: {}: {}".format(
                    attempt + 1, len(urls), candidate, type(error).__name__, error)), flush=True)
                if attempt == len(urls) - 1:
                    raise
        log("{} {} ({} bytes, {})".format(result.status, name, result.size, result.verification), flush=True)
    _link(model_output, models)
    if model is None:
        log(_redact_urls("Downloading video archive {}".format(video_url)), flush=True)
        download_file(video_url, archive, open_url=open_url or _open_url, cancel=cancel, validate=_validate_archive)
        _extract_videos(archive, videos, cancel)
        _link(output / "videos", videos)
    log("[OK] Sample assets verified and installed", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=("app", "stream"))
    parser.add_argument("--model", help="Install only one model named in the SDK manifest (no videos)")
    parser.add_argument("--demo", action="store_true",
                        help="Install only the models dx_app's run_demo.sh launches, plus the videos")
    args = parser.parse_args(argv)

    def cancelled(signum, frame):
        raise DownloadCancelled("Asset setup cancelled")

    previous = signal.signal(signal.SIGTERM, cancelled)
    try:
        install_assets(args.component, model=args.model, demo=args.demo)
        return 0
    except (DownloadCancelled, KeyboardInterrupt) as exc:
        print("[CANCELLED] {}".format(exc), file=sys.stderr, flush=True)
        return 130
    except Exception as exc:
        print(_redact_urls("[ERROR] Asset setup failed (existing assets preserved): {}".format(exc)),
              file=sys.stderr, flush=True)
        return 1
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    sys.exit(main())

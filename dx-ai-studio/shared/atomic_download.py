"""Standard-library transfers that never publish an incomplete destination."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import stat
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path


class DownloadCancelled(OSError):
    pass


@dataclass(frozen=True)
class DownloadResult:
    status: str
    size: int
    verification: str


def _receipt_path(destination):
    key = hashlib.sha256(destination.name.encode("utf-8")).hexdigest()
    return destination.parent / ".studio-assets" / (key + ".json")


def _prepare_receipt_destination(destination):
    receipt = _receipt_path(destination)
    if receipt.parent.is_symlink():
        raise OSError("Asset metadata directory is a symlink: {}".format(receipt.parent))
    prepare_directory(receipt.parent)
    _check_destination(receipt)
    return receipt


def _stat_identity(value, stable=False):
    keys = ("st_size", "st_dev", "st_ino", "st_mtime_ns")
    if not stable:
        keys += ("st_ctime_ns",)
    return {key: getattr(value, key) for key in keys}


def _cleanup_private(*paths):
    for path in paths:
        if path is None:
            continue
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            logging.warning("Studio asset staging cleanup needs attention: %s: %s", path, exc)


def _prepare_metadata(destination, data):
    destination = Path(destination)
    if destination.parent.is_symlink():
        raise OSError("Asset metadata directory is a symlink: {}".format(destination.parent))
    prepare_directory(destination.parent)
    _check_destination(destination)
    partial = destination.parent / (".studio-metadata-" + uuid.uuid4().hex + ".part")
    created = False
    try:
        fd = os.open(str(partial), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream)
            stream.flush()
            os.fsync(stream.fileno())
        return partial
    except BaseException:
        if created:
            _cleanup_private(partial)
        raise


def write_metadata(destination, data):
    """Atomically write Studio-owned receipt/inventory metadata, not model metadata."""
    destination = Path(destination)
    partial = _prepare_metadata(destination, data)
    try:
        _check_destination(destination)
        os.replace(str(partial), str(destination))
    finally:
        _cleanup_private(partial)


@contextmanager
def _publication_lock(destination):
    receipt = _prepare_receipt_destination(destination)
    lock = receipt.with_suffix(".lock")
    _check_destination(lock)
    fd = os.open(str(lock), os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        if os.name == "posix":
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        else:
            import msvcrt
            if os.fstat(fd).st_size == 0:
                os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        yield
    finally:
        os.close(fd)


def _receipt_data(path, name, size, verification):
    # Rename changes ctime. Version 2 binds the staged inode/size/mtime so the
    # entire receipt can be written and fsynced BEFORE the data commit.
    identity = _stat_identity(path.stat(), stable=True)
    if identity["st_size"] != size:
        raise OSError("Asset changed before completion receipt: {}".format(path))
    return {"version": 2, "file": name, "stat": identity, "verification": verification}


def _record_receipt(destination, size, verification):
    with _publication_lock(destination):
        write_metadata(_receipt_path(destination),
                       _receipt_data(destination, destination.name, size, verification))


def _was_published(partial, destination, identity):
    if partial.exists():
        return False
    try:
        return _stat_identity(destination.stat(), stable=True) == identity
    except FileNotFoundError:
        return False


def _commit_asset(partial, destination, size, verification, cancel):
    """Data replacement is the commit boundary, even if interrupted on return."""
    with _publication_lock(destination):
        receipt = _receipt_path(destination)
        data = _receipt_data(partial, destination.name, size, verification)
        staged_receipt = _prepare_metadata(receipt, data)
        backup = None
        receipt_changed = False
        receipt_identity = None
        try:
            receipt_identity = _stat_identity(staged_receipt.stat(), stable=True)
            _check_destination(receipt)
            if receipt.exists():
                backup = receipt.parent / (".studio-receipt-" + uuid.uuid4().hex + ".backup")
                os.link(str(receipt), str(backup))
            _check_cancel(cancel)
            os.replace(str(staged_receipt), str(receipt))
            receipt_changed = True
            _check_cancel(cancel)
            _check_destination(destination)
            os.replace(str(partial), str(destination))
        except BaseException as exc:
            # A signal can arrive after rename succeeds but before Python sees
            # its return. Never roll back just the receipt of published data.
            if _was_published(partial, destination, data["stat"]):
                raise
            if receipt_changed or (receipt_identity is not None and _was_published(
                    staged_receipt, receipt, receipt_identity)):
                try:
                    if backup is not None:
                        os.replace(str(backup), str(receipt))
                    else:
                        receipt.unlink()
                except OSError as rollback_error:
                    saved = backup
                    backup = None  # Keep the prior receipt for explicit recovery.
                    raise OSError("Asset commit failed; prior receipt recovery needed at {}: {}".format(
                        saved, rollback_error)) from exc
            raise
        finally:
            _cleanup_private(staged_receipt, backup)


def asset_file_status(destination):
    """Cheap local-only completion evidence; never hash large files or access HTTP.

    A receipt means a prior transfer matched remote identity Content-Length, a
    supplied authoritative hash, or a validated archive member's length. It is
    not invented SDK metadata or a claim of cryptographic model authenticity.
    Files predating receipts need one explicit online revalidation.
    """
    destination = Path(destination)
    result = {"ok": False, "state": "unverified", "verification": None,
              "detail": "Unverified: no current Studio completion receipt"}
    try:
        current = destination.stat()
    except FileNotFoundError:
        return dict(result, state="missing", detail="Missing asset: {}".format(destination))
    except OSError as exc:
        return dict(result, detail="Unverified asset {}: {}".format(destination, exc))
    if not stat.S_ISREG(current.st_mode) or current.st_size == 0 or destination.is_symlink():
        return result
    receipt = _receipt_path(destination)
    try:
        if (receipt.parent.is_symlink() or receipt.is_symlink()
                or receipt.stat().st_size > 16384):
            return result
        data = json.loads(receipt.read_text(encoding="utf-8"))
        verification = data.get("verification")
        if (data.get("version") in (1, 2) and data.get("file") == destination.name
                and data.get("stat") == _stat_identity(current, stable=data.get("version") == 2)
                and verification in ("content-length", "sha256", "archive-member-size")):
            return {"ok": True, "state": "verified", "verification": verification,
                    "detail": "Studio completion receipt verified ({})".format(verification)}
    except (OSError, ValueError, AttributeError):
        pass
    return result


def _check_cancel(cancel):
    if cancel is not None and cancel():
        raise DownloadCancelled("Asset download cancelled")


def prepare_directory(directory):
    """Fail before network I/O, including when mkdir succeeds but writing cannot."""
    directory = Path(directory)
    probe = directory / (".studio-" + uuid.uuid4().hex + ".probe")
    created = False
    try:
        directory.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(probe), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        os.close(fd)
    except OSError as exc:
        raise type(exc)(exc.errno, "{}: {}".format(directory, exc), str(directory)) from exc
    finally:
        if created:
            probe.unlink()
    return directory


def _check_destination(destination):
    if destination.is_symlink():
        raise OSError("Refusing to replace asset symlink: {}".format(destination))
    if destination.exists() and not destination.is_file():
        raise OSError("Asset destination is not a regular file: {}".format(destination))


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(256 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def publish_stream(stream, destination, size, *, sha256=None, cancel=None, validate=None,
                   verification=None):
    """Copy a bounded stream to a unique sibling and replace only after validation."""
    destination = Path(destination)
    _check_cancel(cancel)
    prepare_directory(destination.parent)
    _check_destination(destination)
    partial = destination.with_name("." + destination.name + "." + uuid.uuid4().hex + ".part")
    created = False
    try:
        fd = os.open(str(partial), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        digest = hashlib.sha256()
        downloaded = 0
        with os.fdopen(fd, "wb") as output:
            while True:
                _check_cancel(cancel)
                chunk = stream.read(256 * 1024)
                _check_cancel(cancel)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                downloaded += len(chunk)
                if size is not None and downloaded > size:
                    raise OSError("Response exceeds expected length for {}".format(destination))
            if downloaded == 0 or (size is not None and downloaded != size):
                raise OSError("Incomplete response for {}: expected {}, received {} bytes".format(
                    destination, size, downloaded))
            if sha256 is not None and digest.hexdigest() != sha256.lower():
                raise OSError("SHA256 mismatch for {}".format(destination))
            output.flush()
            os.fsync(output.fileno())
        if validate is not None:
            validate(partial)
        _check_cancel(cancel)
        verification = verification or ("sha256" if sha256 else "content-length")
        _commit_asset(partial, destination, downloaded, verification, cancel)
        return DownloadResult("downloaded", downloaded, verification)
    finally:
        if created:
            _cleanup_private(partial)


def download_file(url, destination, *, open_url=None, skip_existing=True,
                  sha256=None, cancel=None, validate=None):
    """Verify an existing file by supplied hash or identity GET length; repair stale files.

    ``open_url(url)`` may supply an authenticated/proxied opener. It must request
    identity encoding. Missing length without an authoritative hash is an error,
    never a verified offline/unknown-length skip. Current local receipts need
    no rewrite for cache hits; unreceipted/changed files preflight writes first.
    """
    destination = Path(destination)
    _check_cancel(cancel)
    _check_destination(destination)
    if sha256 is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", sha256):
        raise ValueError("Invalid SHA256 for {}".format(destination))
    cached = skip_existing and asset_file_status(destination)["ok"]
    if skip_existing and sha256 and destination.is_file() and destination.stat().st_size > 0:
        if file_sha256(destination) == sha256.lower():
            if validate is not None:
                validate(destination)
            _check_cancel(cancel)
            if not asset_file_status(destination)["ok"]:
                _record_receipt(destination, destination.stat().st_size, "sha256")
            return DownloadResult("verified", destination.stat().st_size, "sha256")
        cached = False
    if not cached:
        prepare_directory(destination.parent)
        _prepare_receipt_destination(destination)
    if open_url is None:
        def open_url(value):
            request = urllib.request.Request(value, headers={
                "Accept-Encoding": "identity", "User-Agent": "DX-Studio-Assets/1.0"})
            return urllib.request.urlopen(request, timeout=120)

    try:
        with open_url(url) as response:
            if response.status != 200:
                raise OSError("HTTP {} for {}".format(response.status, url))
            headers = response.headers
            encoding = headers.get("Content-Encoding") or headers.get("content-encoding") or "identity"
            length = headers.get("Content-Length") or headers.get("content-length")
            if encoding.lower() != "identity":
                raise OSError("Unverified encoded response for {}: {}".format(url, encoding))
            if length is None and sha256 is None:
                raise OSError("Unverified response for {}: no Content-Length or authoritative hash".format(url))
            if length is not None and not re.fullmatch(r"[0-9]+", str(length)):
                raise OSError("Unverified response for {}: invalid Content-Length".format(url))
            size = int(length) if length is not None else None
            if size == 0:
                raise OSError("Empty response for {}".format(url))
            if (skip_existing and not sha256 and destination.is_file()
                    and destination.stat().st_size == size):
                if validate is not None:
                    validate(destination)
                _check_cancel(cancel)
                if not asset_file_status(destination)["ok"]:
                    _record_receipt(destination, size, "content-length")
                return DownloadResult("verified", size, "content-length")
            if cached:
                prepare_directory(destination.parent)
                _prepare_receipt_destination(destination)
            return publish_stream(response, destination, size, sha256=sha256,
                                  cancel=cancel, validate=validate)
    except DownloadCancelled:
        raise
    except OSError as exc:
        if isinstance(exc, (PermissionError, urllib.error.HTTPError)):
            raise
        raise OSError("Unverified asset {} from {}: {}".format(destination, url, exc)) from exc

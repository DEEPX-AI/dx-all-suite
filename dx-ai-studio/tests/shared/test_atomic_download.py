"""Atomic, verifiable asset transfers; all HTTP responses are in-memory."""
import hashlib
import importlib
import importlib.util
import io
import threading
import urllib.error
from concurrent.futures import ThreadPoolExecutor

import pytest


def downloader():
    assert importlib.util.find_spec("shared.atomic_download"), "Studio needs an atomic downloader"
    return importlib.import_module("shared.atomic_download")


class Response(io.BytesIO):
    status = 200

    def __init__(self, body=b"model", length="5", encoding=None):
        super().__init__(body)
        self.headers = {}
        if length is not None:
            self.headers["Content-Length"] = length
        if encoding:
            self.headers["Content-Encoding"] = encoding


def test_mkdir_failure_precedes_network(tmp_path, monkeypatch):
    dl = downloader()
    original = type(tmp_path).mkdir
    destination = tmp_path / "denied" / "m.dxnn"
    calls = []

    def mkdir(path, *args, **kwargs):
        if path == destination.parent:
            raise PermissionError("original permission failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(type(tmp_path), "mkdir", mkdir)
    with pytest.raises(OSError, match="original permission failure") as exc:
        dl.download_file("https://example/m", destination, open_url=lambda u: calls.append(u))
    assert str(destination.parent) in str(exc.value)
    assert calls == []


@pytest.mark.parametrize("body,length", [(b"abc", "8"), (b"", "0"), (b"abc", "2")])
def test_incomplete_or_empty_never_replaces_good_file(tmp_path, body, length):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"good-old")
    with pytest.raises(OSError):
        dl.download_file("https://example/m", target, skip_existing=False,
                         open_url=lambda u: Response(body, length))
    assert target.read_bytes() == b"good-old"
    assert sorted(p.name for p in tmp_path.iterdir() if p.name != ".studio-assets") == ["m.dxnn"]


def test_stale_file_is_refetched_and_valid_file_revalidated(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"bad")
    responses = []

    def open_url(url):
        response = Response()
        responses.append(response)
        return response

    assert dl.download_file("https://example/m", target, open_url=open_url).status == "downloaded"
    assert target.read_bytes() == b"model"
    assert dl.download_file("https://example/m", target, open_url=open_url).status == "verified"
    assert len(responses) == 2


@pytest.mark.parametrize("length,encoding", [(None, None), ("5", "gzip")])
def test_unverifiable_remote_never_counts_as_verified_skip(tmp_path, length, encoding):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"model")
    with pytest.raises(OSError, match="[Uu]nverified"):
        dl.download_file("https://example/m", target,
                         open_url=lambda u: Response(length=length, encoding=encoding))
    assert target.read_bytes() == b"model"


def test_offline_is_actionable_not_a_verified_skip(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"model")

    def offline(url):
        raise OSError("offline")

    with pytest.raises(OSError, match="offline"):
        dl.download_file("https://example/m", target, open_url=offline)
    assert target.read_bytes() == b"model"


def test_cancel_and_interruption_preserve_existing_file(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"good-old")
    cancelled = threading.Event()

    class Interrupt(Response):
        def read(self, size=-1):
            cancelled.set()
            return super().read(size)

    with pytest.raises(dl.DownloadCancelled):
        dl.download_file("https://example/m", target, skip_existing=False,
                         cancel=cancelled.is_set, open_url=lambda u: Interrupt())
    assert target.read_bytes() == b"good-old"
    assert sorted(p.name for p in tmp_path.iterdir() if p.name != ".studio-assets") == ["m.dxnn"]


def test_interrupted_network_cleans_its_own_partial(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"

    class Broken(Response):
        def read(self, size=-1):
            raise OSError("connection lost")

    with pytest.raises(OSError, match="connection lost"):
        dl.download_file("https://example/m", target, open_url=lambda u: Broken())
    assert [p for p in tmp_path.iterdir() if p.name != ".studio-assets"] == []
    assert not list(tmp_path.rglob("*.part"))


def test_failed_replace_keeps_valid_old_destination(tmp_path, monkeypatch):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"old")
    monkeypatch.setattr(dl.os, "replace", lambda *a: (_ for _ in ()).throw(PermissionError("replace denied")))
    with pytest.raises(PermissionError, match="replace denied"):
        dl.download_file("https://example/m", target, skip_existing=False, open_url=lambda u: Response())
    assert target.read_bytes() == b"old"
    assert sorted(p.name for p in tmp_path.iterdir() if p.name != ".studio-assets") == ["m.dxnn"]


def test_concurrent_downloads_have_independent_partials(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    barrier = threading.Barrier(2)

    def validate(path):
        assert path.read_bytes() == b"model"
        barrier.wait(timeout=5)
        assert len(list(tmp_path.glob("*.part"))) == 2
        barrier.wait(timeout=5)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(dl.download_file, "https://example/m", target,
                               skip_existing=False, open_url=lambda u: Response(),
                               validate=validate) for _ in range(2)]
        for future in futures:
            assert future.result().status == "downloaded"
    assert target.read_bytes() == b"model"
    assert dl.asset_file_status(target)["ok"] is True
    assert sorted(p.name for p in tmp_path.iterdir() if p.name != ".studio-assets") == ["m.dxnn"]


def test_authoritative_hash_detects_same_length_corruption(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"wrong")
    digest = hashlib.sha256(b"model").hexdigest()
    result = dl.download_file("https://example/m", target, sha256=digest,
                              open_url=lambda u: Response())
    assert result.status == "downloaded"
    assert target.read_bytes() == b"model"


def test_http_status_remains_available_for_version_fallback(tmp_path):
    dl = downloader()

    def missing(url):
        raise urllib.error.HTTPError(url, 404, "missing", None, None)

    with pytest.raises(urllib.error.HTTPError) as error:
        dl.download_file("https://example/m", tmp_path / "m.dxnn", open_url=missing)
    assert error.value.code == 404


def test_local_receipt_distinguishes_old_partial_complete_and_changed_file(tmp_path):
    dl = downloader()
    check = getattr(dl, "asset_file_status", None)
    assert callable(check), "Need local-only receipt readiness"
    target = tmp_path / "m.dxnn"
    assert check(target)["state"] == "missing"
    target.write_bytes(b"bad")
    assert check(target)["state"] == "unverified"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    assert check(target)["ok"] is True
    assert check(target)["verification"] == "content-length"
    target.write_bytes(b"other")  # Same length, different contents/mtime/ctime.
    assert check(target)["state"] == "unverified"


def test_verified_remote_skip_creates_receipt_without_reading_body(tmp_path):
    dl = downloader()
    check = getattr(dl, "asset_file_status", None)
    assert callable(check), "Need local-only receipt readiness"
    target = tmp_path / "m.dxnn"
    target.write_bytes(b"model")
    result = dl.download_file("https://example/m", target, open_url=lambda u: Response())
    assert result.status == "verified"
    assert check(target)["ok"] is True


def test_failed_refresh_retains_valid_old_receipt(tmp_path):
    dl = downloader()
    check = getattr(dl, "asset_file_status", None)
    assert callable(check), "Need local-only receipt readiness"
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    with pytest.raises(OSError):
        dl.download_file("https://example/m", target, skip_existing=False,
                         open_url=lambda u: Response(b"bad", "100"))
    assert check(target)["ok"] is True
    assert target.read_bytes() == b"model"


@pytest.mark.parametrize("failure", ["directory", "write", "fsync", "replace", "symlink"])
def test_failed_receipt_commit_preserves_old_file_and_receipt(tmp_path, monkeypatch, failure):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()
    original_prepare = dl.prepare_directory
    original_fsync = dl.os.fsync
    original_replace = dl.os.replace

    if failure == "directory":
        def prepare(path):
            if path == receipt.parent:
                raise PermissionError("metadata directory denied")
            return original_prepare(path)
        monkeypatch.setattr(dl, "prepare_directory", prepare)
    elif failure == "write":
        monkeypatch.setattr(dl.json, "dump",
                            lambda *args, **kwargs: (_ for _ in ()).throw(OSError("metadata write denied")))
    elif failure == "fsync":
        def fsync(fd):
            if dl.os.fstat(fd).st_size > 100:
                raise OSError("metadata fsync denied")
            return original_fsync(fd)
        monkeypatch.setattr(dl.os, "fsync", fsync)
    elif failure == "replace":
        def replace(source, destination):
            if str(destination) == str(receipt):
                raise PermissionError("metadata replace denied")
            return original_replace(source, destination)
        monkeypatch.setattr(dl.os, "replace", replace)
    else:
        saved = tmp_path / "saved-metadata"
        receipt.parent.rename(saved)
        receipt.parent.symlink_to(saved, target_is_directory=True)

    with pytest.raises(OSError):
        dl.publish_stream(io.BytesIO(b"new-valid"), target, 9)
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    if failure != "symlink":
        assert dl.asset_file_status(target)["ok"] is True
    assert not list(tmp_path.rglob("*.part"))


def test_failed_data_commit_restores_old_receipt(tmp_path, monkeypatch):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()
    original_replace = dl.os.replace

    def replace(source, destination):
        if str(destination) == str(target):
            raise PermissionError("model replace denied")
        return original_replace(source, destination)

    monkeypatch.setattr(dl.os, "replace", replace)
    with pytest.raises(PermissionError, match="model replace denied"):
        dl.publish_stream(io.BytesIO(b"new-valid"), target, 9)
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    assert dl.asset_file_status(target)["ok"] is True


def test_cancel_after_receipt_commit_restores_old_receipt(tmp_path, monkeypatch):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()
    original_replace = dl.os.replace
    cancelled = threading.Event()

    def replace(source, destination):
        result = original_replace(source, destination)
        if str(destination) == str(receipt):
            cancelled.set()
        return result

    monkeypatch.setattr(dl.os, "replace", replace)
    with pytest.raises(dl.DownloadCancelled):
        dl.publish_stream(io.BytesIO(b"new-valid"), target, 9, cancel=cancelled.is_set)
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    assert dl.asset_file_status(target)["ok"] is True
    assert not list(tmp_path.rglob("*.part"))
    assert not list(tmp_path.rglob("*.backup"))


def test_version_one_receipts_remain_readable(tmp_path):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_format = dl.json.loads(receipt.read_text())
    old_format["version"] = 1
    old_format["stat"]["st_ctime_ns"] = target.stat().st_ctime_ns
    receipt.write_text(dl.json.dumps(old_format))
    assert dl.asset_file_status(target)["ok"] is True


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("failure", ["directory", "metadata-symlink", "receipt-symlink", "receipt-directory"])
def test_receipt_preflight_precedes_http(tmp_path, monkeypatch, existing, failure):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    if existing:
        target.write_bytes(b"old")
    receipt = dl._receipt_path(target)
    calls = []
    if failure == "directory":
        original = type(tmp_path).mkdir

        def mkdir(path, *args, **kwargs):
            if path == receipt.parent:
                raise PermissionError("receipt directory denied")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(type(tmp_path), "mkdir", mkdir)
    elif failure == "metadata-symlink":
        other = tmp_path / "user-metadata"
        other.mkdir()
        receipt.parent.symlink_to(other, target_is_directory=True)
    else:
        receipt.parent.mkdir()
        if failure == "receipt-symlink":
            other = tmp_path / "user-receipt"
            other.write_bytes(b"personal")
            receipt.symlink_to(other)
        else:
            receipt.mkdir()

    def open_url(url):
        calls.append(url)
        return Response()

    with pytest.raises(OSError) as error:
        dl.download_file("https://example/m", target, open_url=open_url)
    assert str(receipt.parent) in str(error.value)
    assert calls == []
    assert target.read_bytes() == b"old" if existing else not target.exists()
    if failure == "receipt-symlink":
        assert receipt.is_symlink() and other.read_bytes() == b"personal"
    assert not list(tmp_path.rglob("*.part"))


@pytest.mark.parametrize("with_hash", [False, True])
def test_current_verified_cache_hit_needs_no_writes(tmp_path, monkeypatch, with_hash):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()
    calls = []

    def denied(path):
        raise PermissionError("read-only cache: {}".format(path))

    def open_url(url):
        calls.append(url)
        return Response()

    monkeypatch.setattr(dl, "prepare_directory", denied)
    result = dl.download_file("https://example/m", target, open_url=open_url,
                              sha256=hashlib.sha256(b"model").hexdigest() if with_hash else None)
    assert result.status == "verified"
    assert calls == ([] if with_hash else ["https://example/m"])
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    assert dl.asset_file_status(target)["ok"] is True


@pytest.mark.parametrize("existing", [False, True])
def test_interrupt_after_real_data_replace_keeps_committed_pair(tmp_path, monkeypatch, existing):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    if existing:
        dl.download_file("https://example/m", target, open_url=lambda u: Response())
    original_replace = dl.os.replace

    def replace(source, destination):
        original_replace(source, destination)
        if str(destination) == str(target):
            raise KeyboardInterrupt("after atomic data publication")

    monkeypatch.setattr(dl.os, "replace", replace)
    with pytest.raises(KeyboardInterrupt, match="after atomic data publication"):
        dl.publish_stream(io.BytesIO(b"new-valid"), target, 9)
    assert target.read_bytes() == b"new-valid"
    assert dl.asset_file_status(target)["ok"] is True
    assert not list(tmp_path.rglob("*.part"))
    assert not list(tmp_path.rglob("*.backup"))


def test_interrupt_after_real_receipt_replace_restores_old_pair(tmp_path, monkeypatch):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()
    original_replace = dl.os.replace
    interrupted = []

    def replace(source, destination):
        original_replace(source, destination)
        if str(destination) == str(receipt) and not interrupted:
            interrupted.append(True)
            raise KeyboardInterrupt("before atomic data publication")

    monkeypatch.setattr(dl.os, "replace", replace)
    with pytest.raises(KeyboardInterrupt, match="before atomic data publication"):
        dl.publish_stream(io.BytesIO(b"new-valid"), target, 9)
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    assert dl.asset_file_status(target)["ok"] is True
    assert not list(tmp_path.rglob("*.part"))
    assert not list(tmp_path.rglob("*.backup"))


def test_receipt_permissions_are_rechecked_after_http(tmp_path, monkeypatch):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()
    original_prepare = dl.prepare_directory
    opened = []

    def prepare(path):
        if opened and path == receipt.parent:
            raise PermissionError("receipt changed after preflight: {}".format(path))
        return original_prepare(path)

    def open_url(url):
        opened.append(url)
        return Response(b"new-valid", "9")

    monkeypatch.setattr(dl, "prepare_directory", prepare)
    with pytest.raises(PermissionError, match="receipt changed after preflight"):
        dl.download_file("https://example/m", target, skip_existing=False, open_url=open_url)
    assert opened == ["https://example/m"]
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    assert dl.asset_file_status(target)["ok"] is True


def test_readonly_cache_needing_refresh_fails_before_reading_body(tmp_path, monkeypatch):
    dl = downloader()
    target = tmp_path / "m.dxnn"
    dl.download_file("https://example/m", target, open_url=lambda u: Response())
    receipt = dl._receipt_path(target)
    old_receipt = receipt.read_bytes()

    class Changed(Response):
        def read(self, *args):
            pytest.fail("A read-only refresh must fail before reading the response body")

    def denied(path):
        raise PermissionError("read-only cache: {}".format(path))

    monkeypatch.setattr(dl, "prepare_directory", denied)
    with pytest.raises(PermissionError, match="read-only cache"):
        dl.download_file("https://example/m", target, open_url=lambda u: Changed(b"new-valid", "9"))
    assert target.read_bytes() == b"model"
    assert receipt.read_bytes() == old_receipt
    assert dl.asset_file_status(target)["ok"] is True

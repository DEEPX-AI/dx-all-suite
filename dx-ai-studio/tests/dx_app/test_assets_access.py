"""dx_app.core.assets — the file access layer behind /api/images, /api/outputs,
/api/asset-thumb and /api/file_content.

Three of these take a user-supplied path off a query string, so their traversal
guards are the only thing keeping a localhost tool from reading or deleting
outside DX_APP_ROOT. The module sat at 33.3%: the existing thumbnail test needs
opencv, which is not in requirements-ci.txt, so it skips in CI and left the guards
— which need no opencv at all — unexercised.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from dx_app.core import assets as A


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """Redirect every asset root into tmp_path."""
    root = tmp_path / "dx_app"
    (root / "sample" / "img").mkdir(parents=True)
    (root / "assets" / "videos").mkdir(parents=True)
    outputs = root / "outputs"
    outputs.mkdir()
    monkeypatch.setattr(A, "DX_APP_ROOT", root)
    monkeypatch.setattr(A, "SAMPLE_DIR", root / "sample")
    monkeypatch.setattr(A, "ASSETS_DIR", root / "assets")
    monkeypatch.setattr(A, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(A, "_THUMB_CACHE_DIR", root / ".thumb_cache")
    return root


# --------------------------------------------------------------------------
# sample_thumbnail — path-traversal guard (needs no opencv)
# --------------------------------------------------------------------------


def test_sample_thumbnail_refuses_an_outside_file_that_looks_like_an_image(tree):
    """Only the traversal guard can reject this.

    Shaped by mutation testing, twice. `../../etc/passwd` passed with the guard
    deleted because the EXTENSION check rejected it instead; giving it a .jpg
    suffix still passed, because a cache MISS then falls into `import cv2`, which
    is absent here and raises into the bare `except`. Seeding the cache removes
    both stand-ins, leaving the traversal check as the only thing that can say no.
    """
    import hashlib

    outside = tree.parent / "outside.jpg"
    outside.write_bytes(b"pretend-jpeg")
    r = outside.resolve()
    key = hashlib.sha1(f"{r}|{r.stat().st_mtime_ns}|160".encode("utf-8")).hexdigest()
    cached = A._THUMB_CACHE_DIR / (key + ".jpg")
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"cached")

    assert A.sample_thumbnail("../outside.jpg") is None
    assert A.sample_thumbnail(str(outside)) is None


def test_sample_thumbnail_refuses_a_non_image_extension_even_when_cached(tree):
    """Only the extension guard can reject this.

    Also mutation-shaped: an in-tree `server.py` passed with the guard deleted
    because opencv is absent and the decode raised anyway. Seeding the CACHE makes
    the function return before it ever reaches opencv, so the extension check is
    the only thing left standing between the caller and an arbitrary in-tree file.
    """
    import hashlib

    src = tree / "server.py"
    src.write_text("print('secret')")
    r = src.resolve()
    key = hashlib.sha1(f"{r}|{r.stat().st_mtime_ns}|160".encode("utf-8")).hexdigest()
    cached = A._THUMB_CACHE_DIR / (key + ".jpg")
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"cached")

    assert A.sample_thumbnail("server.py") is None


def test_sample_thumbnail_refuses_a_missing_file(tree):
    assert A.sample_thumbnail("sample/img/nope.png") is None


def test_sample_thumbnail_serves_a_cache_hit_without_decoding(tree):
    """The cache-hit path must return before importing opencv at all."""
    src = tree / "sample" / "img" / "a.jpg"
    src.write_bytes(b"pretend-jpeg")
    import hashlib

    resolved = src.resolve()
    key = hashlib.sha1(
        f"{resolved}|{resolved.stat().st_mtime_ns}|160".encode("utf-8")
    ).hexdigest()
    cached = A._THUMB_CACHE_DIR / (key + ".jpg")
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"cached-thumb")

    assert A.sample_thumbnail("sample/img/a.jpg") == cached


def test_sample_thumbnail_cache_key_changes_when_the_source_is_edited(tree):
    """mtime is in the key, so a replaced image must not serve the stale thumbnail."""
    src = tree / "sample" / "img" / "a.jpg"
    src.write_bytes(b"v1")
    import hashlib

    def _key():
        r = src.resolve()
        return hashlib.sha1(f"{r}|{r.stat().st_mtime_ns}|160".encode("utf-8")).hexdigest()

    first = _key()
    os.utime(src, ns=(0, 12345))
    assert _key() != first


def test_sample_thumbnail_width_is_part_of_the_cache_key(tree):
    """Two widths must not collide on one cached file."""
    src = tree / "sample" / "img" / "a.jpg"
    src.write_bytes(b"x")
    import hashlib

    r = src.resolve()
    keys = {
        hashlib.sha1(f"{r}|{r.stat().st_mtime_ns}|{w}".encode("utf-8")).hexdigest()
        for w in (160, 320)
    }
    assert len(keys) == 2


# --------------------------------------------------------------------------
# get_file_content — traversal + extension allowlist
# --------------------------------------------------------------------------


def test_get_file_content_reads_an_allowed_in_tree_file(tree):
    (tree / "notes.md").write_text("# hello")
    assert A.get_file_content("notes.md") == "# hello"


def test_get_file_content_refuses_an_outside_file_with_an_allowed_extension(tree):
    """Only the root guard can reject this.

    Mutation-shaped: `../../etc/passwd` passed with the guard deleted because the
    extension allowlist rejected it first. A .md file just outside the root is
    refused by the root check alone.
    """
    outside = tree.parent / "outside.md"
    outside.write_text("secret notes")
    assert A.get_file_content("../outside.md") is None
    assert A.get_file_content(str(outside)) is None


def test_get_file_content_refuses_an_extension_outside_the_allowlist(tree):
    (tree / "id_rsa").write_text("PRIVATE KEY")
    (tree / "secrets.env").write_text("TOKEN=1")
    assert A.get_file_content("id_rsa") is None
    assert A.get_file_content("secrets.env") is None


def test_get_file_content_allowlist_is_case_sensitive(tree):
    """Documents current behaviour: .PY is not .py and is refused."""
    (tree / "Mod.PY").write_text("x = 1")
    assert A.get_file_content("Mod.PY") is None


def test_get_file_content_replaces_undecodable_bytes_instead_of_raising(tree):
    (tree / "bad.py").write_bytes(b"a = '\xff\xfe'")
    out = A.get_file_content("bad.py")
    assert out is not None and "�" in out


# --------------------------------------------------------------------------
# _scan_sample_img / get_images / get_videos
# --------------------------------------------------------------------------


def test_scan_sample_img_lists_images_and_image_bearing_dirs_only(tree):
    img = tree / "sample" / "img"
    (img / "b.jpg").write_bytes(b"")
    (img / "a.png").write_bytes(b"")
    (img / "notes.txt").write_text("skip me")
    (img / "pair").mkdir()
    (img / "pair" / "left.jpg").write_bytes(b"")
    (img / "empty").mkdir()

    assert A._scan_sample_img() == [
        "sample/img/a.png",   # sorted, and the .txt sibling is filtered out
        "sample/img/b.jpg",
        "sample/img/pair",    # dir kept: it holds an image
    ], "empty/ must be dropped (no images) and notes.txt must never be offered as an input"


def test_scan_sample_img_is_empty_when_the_gallery_is_absent(tree, monkeypatch):
    monkeypatch.setattr(A, "SAMPLE_DIR", tree / "gone")
    assert A._scan_sample_img() == []


def test_get_images_without_a_category_returns_the_sample_gallery(tree):
    (tree / "sample" / "img" / "a.jpg").write_bytes(b"")
    assert A.get_images() == ["sample/img/a.jpg"]


def test_get_images_scans_the_models_own_dir_for_non_gallery_inputs(tree, monkeypatch):
    """LiDAR .bin inputs live outside sample/img; offering jpgs there is wrong."""
    lidar = tree / "sample" / "lidar"
    lidar.mkdir()
    (lidar / "b.bin").write_bytes(b"")
    (lidar / "a.bin").write_bytes(b"")
    (lidar / "readme.txt").write_text("")
    (tree / "sample" / "img" / "street.jpg").write_bytes(b"")

    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_IMAGE", {"3d_object_detection": "sample/lidar/a.bin"})

    got = A.get_images("3d_object_detection")
    assert got == ["sample/lidar/a.bin", "sample/lidar/b.bin"]
    assert not any(g.endswith(".jpg") for g in got)
    assert not any(g.endswith(".txt") for g in got)


def test_get_images_always_includes_the_declared_default(tree, monkeypatch):
    """A default the dir scan missed must still be selectable."""
    other = tree / "sample" / "other"
    other.mkdir()
    (other / "z.png").write_bytes(b"")
    default = other / "default.png"
    default.write_bytes(b"")

    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_IMAGE", {"pose": "sample/other/default.png"})
    got = A.get_images("pose")
    assert "sample/other/default.png" in got


def test_get_images_falls_back_to_the_gallery_for_sample_img_categories(tree, monkeypatch):
    (tree / "sample" / "img" / "a.jpg").write_bytes(b"")
    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_IMAGE", {"detect": "sample/img/a.jpg"})
    assert A.get_images("detect") == ["sample/img/a.jpg"]


def test_get_videos_filters_by_extension(tree):
    v = tree / "assets" / "videos"
    (v / "a.mp4").write_bytes(b"")
    (v / "b.mov").write_bytes(b"")
    (v / "notes.txt").write_text("")
    assert A.get_videos() == ["assets/videos/a.mp4", "assets/videos/b.mov"]


def test_get_videos_puts_the_category_default_first(tree, monkeypatch):
    """The UI selects index 0, so ordering IS the default selection."""
    v = tree / "assets" / "videos"
    for n in ("a.mp4", "b.mp4", "c.mp4"):
        (v / n).write_bytes(b"")
    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_VIDEO", {"detect": "assets/videos/c.mp4"})
    assert A.get_videos("detect")[0] == "assets/videos/c.mp4"


def test_get_videos_ignores_a_preference_that_is_not_present(tree, monkeypatch):
    v = tree / "assets" / "videos"
    (v / "a.mp4").write_bytes(b"")
    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_VIDEO", {"detect": "assets/videos/missing.mp4"})
    assert A.get_videos("detect") == ["assets/videos/a.mp4"]


def test_get_videos_is_empty_without_a_videos_dir(tree, monkeypatch):
    monkeypatch.setattr(A, "ASSETS_DIR", tree / "gone")
    assert A.get_videos() == []


# --------------------------------------------------------------------------
# list_outputs / delete_output
# --------------------------------------------------------------------------


def test_list_outputs_classifies_by_extension(tree):
    out = A.OUTPUTS_DIR
    (out / "a.jpg").write_bytes(b"")
    (out / "b.mp4").write_bytes(b"")
    (out / "c.zip").write_bytes(b"")
    (out / "d.log").write_text("")
    (out / "adir").mkdir()

    kinds = {i["name"]: i["type"] for i in A.list_outputs()}
    assert kinds == {"a.jpg": "image", "b.mp4": "video", "c.zip": "archive", "d.log": "other"}
    assert "adir" not in kinds, "directories are not downloadable outputs"


def test_list_outputs_recognises_a_multi_part_archive_suffix(tree):
    """`.tar.gz` has suffix '.gz'; the check must look at the whole name."""
    (A.OUTPUTS_DIR / "bundle.tar.gz").write_bytes(b"")
    assert A.list_outputs()[0]["type"] == "archive"


def test_list_outputs_is_newest_first(tree):
    out = A.OUTPUTS_DIR
    for name, mtime in (("old.jpg", 1000), ("new.jpg", 9000), ("mid.jpg", 5000)):
        f = out / name
        f.write_bytes(b"")
        os.utime(f, (mtime, mtime))
    assert [i["name"] for i in A.list_outputs()] == ["new.jpg", "mid.jpg", "old.jpg"]


def test_list_outputs_links_a_result_image_to_its_source(tree, monkeypatch):
    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_IMAGE", {"detection": "sample/img/street.jpg"})
    (A.OUTPUTS_DIR / "result_detection_12.jpg").write_bytes(b"")
    assert A.list_outputs()[0]["src_image"] == "sample/img/street.jpg"


def test_list_outputs_leaves_src_image_unset_when_nothing_matches(tree, monkeypatch):
    from dx_app.core import config as C
    monkeypatch.setattr(C, "CAT_IMAGE", {"detection": "sample/img/street.jpg"})
    (A.OUTPUTS_DIR / "result_zzz_12.jpg").write_bytes(b"")
    (A.OUTPUTS_DIR / "plain.jpg").write_bytes(b"")
    assert all(i["src_image"] is None for i in A.list_outputs())


@pytest.mark.parametrize(
    "name", ["", "../outside.jpg", "..", "a/../../b.jpg"],
    ids=["empty", "dotdot", "bare-dotdot", "mixed"],
)
def test_delete_output_refuses_anything_but_a_bare_filename(tree, name):
    assert "error" in A.delete_output(name)


def test_delete_output_separator_guard_actually_prevents_the_delete(tree):
    """Mutation-shaped: asserting only on the error message passed with the "/"
    guard deleted, because the nested path simply missed on disk and answered
    "File not found". Put a REAL file at that nested path so the guard is the only
    thing keeping it alive.
    """
    nested = A.OUTPUTS_DIR / "sub" / "dir.jpg"
    nested.parent.mkdir()
    nested.write_bytes(b"payload")

    assert A.delete_output("sub/dir.jpg") == {"error": "Invalid filename"}
    assert nested.exists(), "a path with a separator must never reach unlink()"


def test_delete_output_cannot_escape_the_outputs_dir(tree):
    """The same, one level up: a real file outside outputs/ must survive."""
    victim = tree / "keepme.jpg"
    victim.write_bytes(b"payload")

    assert "error" in A.delete_output("../keepme.jpg")
    assert victim.exists()


def test_delete_output_dotdot_check_is_redundant_with_the_separator_check(tree):
    """Documents a mutation that legitimately survives.

    Deleting `".." in name` from the guard changes no observable behaviour: on
    POSIX an escape needs a separator, and the "/" check already refuses those. A
    name containing ".." but no "/" (".." itself, "..jpg") resolves inside
    outputs/ and simply is not a file. The ".." clause is unreachable
    defence-in-depth, not a second barrier — so no test can kill that mutant, and
    pretending otherwise with a contrived case would be theatre.
    """
    assert A.delete_output("..") == {"error": "Invalid filename"}
    # With the ".." clause removed this would answer "File not found" instead —
    # a different message, but equally a refusal, and nothing is deleted either way.
    assert not (A.OUTPUTS_DIR / "..jpg").exists()
    assert A.delete_output("..jpg") == {"error": "Invalid filename"}


def test_delete_output_refuses_a_missing_file(tree):
    assert A.delete_output("nope.jpg") == {"error": "File not found"}


def test_delete_output_refuses_a_directory(tree):
    (A.OUTPUTS_DIR / "adir").mkdir()
    assert A.delete_output("adir") == {"error": "File not found"}


def test_delete_output_removes_the_file(tree):
    f = A.OUTPUTS_DIR / "gone.jpg"
    f.write_bytes(b"")
    assert A.delete_output("gone.jpg") == {"ok": True, "deleted": "gone.jpg"}
    assert not f.exists()


def test_delete_output_reports_an_unlink_failure(tree, monkeypatch):
    f = A.OUTPUTS_DIR / "locked.jpg"
    f.write_bytes(b"")

    def _boom(self, **k):
        raise PermissionError("read-only filesystem")

    monkeypatch.setattr(Path, "unlink", _boom)
    assert "read-only filesystem" in A.delete_output("locked.jpg")["error"]

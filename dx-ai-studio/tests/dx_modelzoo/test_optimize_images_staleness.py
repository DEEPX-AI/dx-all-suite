"""Optimized images are rebuilt when their source changes, and the manifest records everything.

A skip rule of "the output already exists" ignores when the source changed, so regenerated
thumbnails would never be re-optimized. catalog.js tries .webp → .jpg → original, so the browser
would keep getting the old picture; --force works around it only by rebuilding every image.

The manifest must also not be overwritten with **only what this run processed**: running
`--model` one at a time would leave only the last one. tools/perf_audit.py only checks
`manifest.is_file()`, so nothing else would notice.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dx_modelzoo.scripts.optimize_images import optimize_images  # noqa: E402

pytest.importorskip("PIL")


def _png(path: Path, colour) -> None:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (40, 30), colour).save(path)


@pytest.fixture()
def tree(tmp_path):
    src = tmp_path / "data"
    out = tmp_path / "optimized"
    _png(src / "thumbnails" / "alpha.jpg", (10, 20, 30))
    _png(src / "thumbnails" / "beta.jpg", (200, 10, 10))
    return src, out


def _run(src, out, **kw):
    return optimize_images(src, out, write=True, **kw)


class TestStaleOutputsAreRebuilt:
    def test_a_regenerated_source_is_optimized_again(self, tree):
        src, out = tree
        first = _run(src, out)
        assert first["written"] == 2

        # Rebuild the source (as when thumbnails are regenerated)
        _png(src / "thumbnails" / "alpha.jpg", (0, 250, 0))
        import os, time

        future = time.time() + 10
        os.utime(src / "thumbnails" / "alpha.jpg", (future, future))

        second = _run(src, out)
        assert second["written"] >= 1, (
            "원본이 바뀌었는데 최적화본을 다시 만들지 않았다 — "
            "브라우저는 계속 옛 그림을 받는다"
        )
        sources = {Path(e["source"]).name for e in second["images"]}
        assert "alpha.jpg" in sources

    def test_an_unchanged_source_is_still_skipped(self, tree):
        """No needless rebuilds: rebuilding unchanged images every time would equal --force."""
        src, out = tree
        _run(src, out)
        again = _run(src, out)
        assert again["written"] == 0 and again["skipped"] == 2


class TestTheManifestDescribesEverything:
    def test_a_partial_run_does_not_erase_the_rest(self, tree):
        """Running `--model` for one image must keep the other records."""
        src, out = tree
        _run(src, out)
        full = json.loads((out / "manifest.json").read_text())
        assert len(full["images"]) == 2

        import os, time

        future = time.time() + 10
        os.utime(src / "thumbnails" / "alpha.jpg", (future, future))
        _run(src, out, model="alpha")

        after = json.loads((out / "manifest.json").read_text())
        names = {Path(e["source"]).name for e in after["images"]}
        assert names == {"alpha.jpg", "beta.jpg"}, (
            f"부분 실행이 나머지 기록을 지웠다: {sorted(names)}"
        )

    def test_the_totals_cover_every_entry(self, tree):
        src, out = tree
        _run(src, out)
        m = json.loads((out / "manifest.json").read_text())
        assert m["total_source_bytes"] == sum(e["source_bytes"] for e in m["images"])

    def test_a_removed_source_drops_out_of_the_manifest(self, tree):
        """Keeping records of removed sources would make the totals disagree with reality.

        The manifest is merged across runs, so removed sources must be dropped explicitly.
        """
        import json
        import os
        import time
        from pathlib import Path as _P

        src, out = tree
        _run(src, out)
        assert len(json.loads((out / "manifest.json").read_text())["images"]) == 2

        (src / "thumbnails" / "beta.jpg").unlink()
        future = time.time() + 10
        os.utime(src / "thumbnails" / "alpha.jpg", (future, future))
        _run(src, out)

        after = json.loads((out / "manifest.json").read_text())
        names = {_P(e["source"]).name for e in after["images"]}
        assert names == {"alpha.jpg"}, f"사라진 원본이 manifest 에 남았다: {sorted(names)}"
        assert after["total_source_bytes"] == sum(e["source_bytes"] for e in after["images"])


class TestTheManifestIsPortable:
    def test_no_absolute_paths_are_written(self, tree):
        """Absolute paths would bake one developer's checkout (/home/…) into the committed manifest.
        Paths are written relative: sources to the source root, outputs to the output root."""
        src, out = tree
        _run(src, out)
        m = json.loads((out / "manifest.json").read_text())
        for e in m["images"]:
            for key in ("source", "webp_path", "jpg_path"):
                if key in e:
                    assert not Path(e[key]).is_absolute(), (key, e[key])
        assert {Path(e["source"]).as_posix() for e in m["images"]} == {"thumbnails/alpha.jpg", "thumbnails/beta.jpg"}

    def test_an_old_absolute_manifest_is_rewritten_relative(self, tree):
        src, out = tree
        _run(src, out)
        m = json.loads((out / "manifest.json").read_text())
        for e in m["images"]:                       # simulate a manifest with absolute paths
            e["source"] = str(src / e["source"])
        (out / "manifest.json").write_text(json.dumps(m))
        import os, time
        future = time.time() + 10
        os.utime(src / "thumbnails" / "alpha.jpg", (future, future))
        _run(src, out, model="alpha")
        after = json.loads((out / "manifest.json").read_text())
        assert sorted(e["source"] for e in after["images"]) == ["thumbnails/alpha.jpg", "thumbnails/beta.jpg"]


def test_the_committed_manifest_has_no_local_paths():
    committed = ROOT / "dx_modelzoo" / "data" / "optimized" / "manifest.json"
    text = committed.read_text(encoding="utf-8")
    assert "/home/" not in text and '"/' not in text

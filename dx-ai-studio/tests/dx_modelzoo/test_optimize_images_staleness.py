"""최적화본은 원본이 바뀌면 다시 만들어져야 하고, manifest 는 전체를 기록해야 한다.

2026-09-21 에 썸네일 11개를 재생성하고 optimize_images.py 를 그냥 돌렸더니
**778개 스킵, 내 파일은 하나도 갱신되지 않았다.** 스킵 조건이 "출력이 이미
존재하면 건너뜀" 이라 원본이 언제 바뀌었는지 보지 않기 때문이다. catalog.js 는
.webp → .jpg → 원본 순으로 시도하므로, 브라우저는 계속 옛 그림을 받는다.
--force 로 우회했지만 그것은 매번 1578개를 전부 다시 만든다는 뜻이다.

두 번째 결함은 더 조용하다. manifest.json 을 **이번 실행에서 처리한 것만으로
덮어쓴다.** `--model` 로 하나씩 돌리면 마지막 하나만 남는다 — 실제로 그렇게
되어 1578개 중 2개만 적힌 manifest 가 커밋됐다. tools/perf_audit.py 는
`manifest.is_file()` 만 보므로 아무도 눈치채지 못했다.
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

        # 원본을 다시 만든다 (썸네일 재생성과 같은 상황)
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
        """과잉 재생성 방지 — 안 바뀐 것까지 매번 다시 만들면 --force 와 같아진다."""
        src, out = tree
        _run(src, out)
        again = _run(src, out)
        assert again["written"] == 0 and again["skipped"] == 2


class TestTheManifestDescribesEverything:
    def test_a_partial_run_does_not_erase_the_rest(self, tree):
        """`--model` 로 하나만 돌려도 나머지 기록이 남아야 한다."""
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
        """원본이 사라진 기록을 남겨두면 합계가 현실과 어긋난다.

        merge 를 넣으면서 생긴 위험이다 — 예전(덮어쓰기)에는 사라진 것이 저절로
        빠졌다. 변이 검사에서 이 가지만 살아남아 계약이 비어 있는 것이 드러났다.
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
        """2026-10-12 release audit: the committed manifest carried ~1,500 paths like /home/deepx/hj_ws/… — one
        developer's checkout. Paths are written relative: sources to the source root, outputs to the output root."""
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
        for e in m["images"]:                       # simulate the old committed file
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

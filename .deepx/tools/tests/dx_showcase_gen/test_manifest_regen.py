"""Tests for the manifest-driven doc regeneration (card grid / catalog / table)."""
import json

import pytest

from dx_showcase_gen import augment, manifest


def _sc(name, kind="retrain", **kw):
    base = dict(
        name=name, kind=kind,
        title_en=f"{name} T", title_ko=f"{name} 제목",
        tagline_en="tag en", tagline_ko="tag ko",
        gif=f"{name}.gif",
        what_en="what en", what_ko="what ko",
        highlight_en="hi en", highlight_ko="hi ko",
        model="Claude Opus 4.8", build="≈ 10 min", turns="9",
        tokens="≈ 6K", cost="≈ $3",
    )
    base.update(kw)
    return manifest.Showcase(**base)


def _man(n=4):
    scs = [_sc(f"s{i}") for i in range(n)]
    return manifest.Manifest(section={
        "title_en": "T", "title_ko": "T",
        "catchphrase_en": "CP en", "catchphrase_ko": "CP ko"}, showcases=scs)


# ---- card_grid -------------------------------------------------------------

def test_card_grid_three_columns_pads_last_row():
    grid = augment.card_grid(_man(4).showcases, lang="en", cols=3)
    assert grid.count("<tr>") == 2          # 4 cells -> 2 rows of 3
    assert grid.count("<td></td>") == 2     # last row padded to 3
    assert grid.count('width="33%"') == 4   # one per real cell


def test_card_grid_links_and_gif_paths_root_surface():
    grid = augment.card_grid(_man(1).showcases, lang="en", surface="root")
    assert 'href="dx-agentic-dev-showcase/s0/README.md"' in grid
    assert 'src="./docs/source/img/s0.gif"' in grid


def test_card_grid_ko_uses_korean_titles_and_ko_readme():
    grid = augment.card_grid(_man(1).showcases, lang="ko", surface="catalog")
    assert "s0 제목" in grid
    assert 'href="./s0/README-ko.md"' in grid
    assert 'src="../docs/source/img/s0.gif"' in grid   # catalog surface = one dir deep


# ---- showcase_table --------------------------------------------------------

def test_showcase_table_has_header_and_one_row_per_showcase():
    table = augment.showcase_table(_man(3).showcases, lang="en")
    assert table.splitlines()[0].startswith("| Showcase | What it is |")
    assert sum(1 for ln in table.splitlines() if ln.startswith("| **[")) == 3


def test_showcase_table_docs_surface_links_to_dir():
    table = augment.showcase_table(_man(1).showcases, lang="en")
    assert "(../../dx-agentic-dev-showcase/s0/)" in table


# ---- catalog_region --------------------------------------------------------

def test_catalog_region_has_summary_table_and_per_showcase_blocks():
    body = augment.catalog_region(_man(2), lang="en")
    assert "| Showcase | Kind | Highlight |" in body
    assert body.count("### ") == 2                 # one block per showcase
    assert body.count('align="right"') == 2        # gif per block


# ---- idempotency -----------------------------------------------------------

def test_upsert_block_idempotent(tmp_path):
    f = tmp_path / "README.md"
    f.write_text("# X\n\n<!-- a:start -->\n<!-- a:end -->\n\ntail\n")
    blk = augment.card_grid(_man(2).showcases, lang="en")
    c1 = augment.upsert_block(str(f), anchor="X", block=blk, mk="a")
    after1 = f.read_text()
    c2 = augment.upsert_block(str(f), anchor="X", block=blk, mk="a")
    assert c1 is True and c2 is False         # second run = no change
    assert f.read_text() == after1


# ---- manifest loading + coverage ------------------------------------------

def _write_manifest(root, names):
    (root / "dx-agentic-dev-showcase").mkdir(parents=True, exist_ok=True)
    entries = [dict(
        name=n, kind="retrain", title_en="t", title_ko="t",
        tagline_en="t", tagline_ko="t", gif="g.gif", what_en="w", what_ko="w",
        highlight_en="h", highlight_ko="h", model="m", build="b",
        turns="1", tokens="1", cost="$1") for n in names]
    (root / manifest.MANIFEST_REL).write_text(json.dumps(
        {"section": {"title_en": "", "title_ko": "", "catchphrase_en": "",
                     "catchphrase_ko": ""}, "showcases": entries}))


def test_load_manifest_roundtrip(tmp_path):
    _write_manifest(tmp_path, ["a", "b"])
    man = manifest.load_manifest(str(tmp_path))
    assert [s.name for s in man.showcases] == ["a", "b"]


def test_missing_from_manifest_detects_unlisted_dir(tmp_path):
    _write_manifest(tmp_path, ["a"])
    # two dirs on disk, only "a" in the manifest -> "b" is missing
    for d in ("a", "b"):
        (tmp_path / "dx-agentic-dev-showcase" / d).mkdir(parents=True)
        (tmp_path / "dx-agentic-dev-showcase" / d / "README.md").write_text("x")
    assert manifest.missing_from_manifest(str(tmp_path)) == ["b"]


def test_real_repo_manifest_covers_all_dirs():
    """The committed manifest must list every showcase dir (regression guard for
    the ultralytics-yolo-deepx-export omission)."""
    import subprocess
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    assert manifest.missing_from_manifest(root) == []

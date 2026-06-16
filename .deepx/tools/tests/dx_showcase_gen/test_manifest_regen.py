"""Tests for the manifest-driven doc regeneration (card grid / catalog / table)."""
import json

import pytest

from dx_showcase_gen import augment, manifest


def _sc(name, kind="retrain", category="ultralytics", **kw):
    base = dict(
        name=name, kind=kind, category=category,
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
    scs = [_sc(f"s{i}") for i in range(n)]   # _sc default category = "ultralytics"
    cats = [manifest.Category(id="ultralytics", status="active",
                              title_en="Ultralytics", title_ko="Ultralytics")]
    return manifest.Manifest(section={
        "title_en": "T", "title_ko": "T",
        "catchphrase_en": "CP en", "catchphrase_ko": "CP ko"},
        showcases=scs, categories=cats)


# ---- card_grid -------------------------------------------------------------

def test_card_grid_three_columns_pads_last_row():
    grid = augment.card_grid(_man(4).showcases, lang="en", cols=3)
    assert grid.count("<tr>") == 2          # 4 cells -> 2 rows of 3
    assert grid.count("<td></td>") == 2     # last row padded to 3
    assert grid.count('width="33%"') == 4   # one per real cell


def test_card_grid_links_and_gif_paths_root_surface():
    grid = augment.card_grid(_man(1).showcases, lang="en", surface="root")
    assert 'href="dx-agent-dev-showcase/s0/README.md"' in grid
    assert 'src="./docs/source/img/s0.gif"' in grid


def test_card_grid_ko_uses_korean_titles_and_ko_readme():
    grid = augment.card_grid(_man(1).showcases, lang="ko", surface="catalog")
    assert "s0 제목" in grid
    assert 'href="./s0/README-ko.md"' in grid
    assert 'src="../docs/source/img/s0.gif"' in grid   # catalog surface = one dir deep


# ---- card media: uniform height, sample, video ----------------------------

def test_card_grid_uses_uniform_height_not_width():
    grid = augment.card_grid(_man(2).showcases, lang="en", height=150)
    assert 'height="150"' in grid
    assert 'width="230"' not in grid          # no per-image width (heights align rows)


def test_sample_card_uses_sample_image():
    s = _sc("wild", card_media="sample", sample="wild-sample.jpg", gif="wild-build.gif")
    grid = augment.card_grid([s], lang="en", surface="root", height=150)
    assert 'src="./docs/source/img/wild-sample.jpg"' in grid   # sample, not the build gif
    assert "wild-build.gif" not in grid


def test_video_card_renders_gif_rendition_not_video_tag():
    # GitHub does NOT render inline <video>; a card_media="video" showcase renders
    # the GIF rendition of the clip (same basename, .gif), never a <video>/.mp4.
    s = _sc("exp", kind="export", card_media="video",
            video="v.mp4", poster="p.jpg")
    grid = augment.card_grid([s], lang="en", surface="root", height=150)
    assert "<video" not in grid and ".mp4" not in grid
    assert '<img src="./docs/source/img/v.gif"' in grid
    # single outer showcase anchor, no nested anchors
    assert grid.count("<a ") == 1


def test_feature_first_uses_build_gif_when_set():
    # When a showcase's primary `gif` is a gameplay/demo, the feature-first 2nd
    # cell uses `build_gif` for the build-capture cell.
    s = _sc("ocr", kind="app", card_media="gif", gif="play.gif")
    s.build_gif = "build.gif"
    cell = augment._gif_cell(s, lang="en", surface="root", height=150, cols=2,
                             caption="build capture (timelapse)")
    assert "build.gif" in cell and "play.gif" not in cell


def test_intro_region_is_announcement_only():
    # the catchphrase now lives under each category heading, not in the top intro
    man = manifest.Manifest(section={
        "title_en": "T", "title_ko": "T", "catchphrase_en": "HERO", "catchphrase_ko": "히어로",
        "announcement_en": "ANNOUNCE", "announcement_ko": "공지"}, showcases=[_sc("a")])
    assert augment.intro_region(man, lang="en") == "ANNOUNCE"
    assert augment.intro_region(man, lang="ko") == "공지"


def test_cardgrid_region_shows_category_blurb_under_heading():
    cats = [manifest.Category(id="ultralytics", status="active",
                              title_en="Ultralytics", title_ko="U",
                              blurb_en="**ONE-CMD hook.**", blurb_ko="훅")]
    man = manifest.Manifest(section={
        "title_en": "T", "title_ko": "T", "catchphrase_en": "", "catchphrase_ko": "",
        "announcement_en": "A", "announcement_ko": "A"},
        showcases=[_sc("u1", category="ultralytics")], categories=cats)
    body = augment.cardgrid_region(man, lang="en")
    assert "#### Ultralytics" in body and "**ONE-CMD hook.**" in body


# ---- categories ------------------------------------------------------------

def _man_cat():
    cats = [
        manifest.Category(id="ultralytics", status="active",
                          title_en="Ultralytics ecosystem", title_ko="Ultralytics 생태계"),
        manifest.Category(id="paddle", status="coming-soon",
                          title_en="PaddlePaddle ecosystem", title_ko="PaddlePaddle 생태계",
                          note_en="Coming soon.", note_ko="추후 추가 예정."),
    ]
    scs = [_sc("u1", category="ultralytics"), _sc("u2", category="ultralytics")]
    return manifest.Manifest(section={
        "title_en": "T", "title_ko": "T", "catchphrase_en": "CP", "catchphrase_ko": "CP",
        "announcement_en": "AN", "announcement_ko": "AN"}, showcases=scs, categories=cats)


def test_by_category_filters():
    man = _man_cat()
    assert [s.name for s in man.by_category("ultralytics")] == ["u1", "u2"]
    assert man.by_category("paddle") == []


def test_cardgrid_region_groups_by_category_with_coming_soon():
    body = augment.cardgrid_region(_man_cat(), lang="en")
    assert "#### Ultralytics ecosystem" in body
    assert "#### PaddlePaddle ecosystem — _Coming soon._" in body   # empty cat -> note, no grid


def test_categorized_table_renders_coming_soon_note_not_table():
    out = augment.categorized_table(_man_cat(), lang="ko")
    assert "#### Ultralytics 생태계" in out
    assert "#### PaddlePaddle 생태계" in out
    assert "추후 추가 예정." in out
    # the coming-soon category has no data rows
    assert out.count("| **[") == 2     # only the 2 ultralytics rows


def test_catalog_region_groups_by_category():
    body = augment.catalog_region(_man_cat(), lang="en")
    assert "## Ultralytics ecosystem" in body
    assert "## PaddlePaddle ecosystem" in body and "Coming soon." in body


# ---- showcase_table --------------------------------------------------------

def test_showcase_table_has_header_and_one_row_per_showcase():
    table = augment.showcase_table(_man(3).showcases, lang="en")
    assert table.splitlines()[0].startswith("| Showcase | What it is |")
    assert sum(1 for ln in table.splitlines() if ln.startswith("| **[")) == 3


def test_showcase_table_docs_surface_links_to_dir():
    table = augment.showcase_table(_man(1).showcases, lang="en")
    assert "(../../dx-agent-dev-showcase/s0/)" in table


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
    (root / "dx-agent-dev-showcase").mkdir(parents=True, exist_ok=True)
    entries = [dict(
        name=n, kind="retrain", category="ultralytics", title_en="t", title_ko="t",
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
        (tmp_path / "dx-agent-dev-showcase" / d).mkdir(parents=True)
        (tmp_path / "dx-agent-dev-showcase" / d / "README.md").write_text("x")
    assert manifest.missing_from_manifest(str(tmp_path)) == ["b"]


def test_real_repo_manifest_covers_all_dirs():
    """The committed manifest must list every showcase dir (regression guard for
    the ultralytics-yolo-deepx-export omission)."""
    import subprocess
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    assert manifest.missing_from_manifest(root) == []

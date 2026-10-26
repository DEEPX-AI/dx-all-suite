"""Every category test_models.conf uses must be in CATEGORIES.

Without this contract one change goes unnoticed:

    model added to the conf, no metadata         → 3 tests fail naming the model id (loud)
    category removed from CATEGORIES             → test_config.py fails (loud)
    new category in the conf, not in CATEGORIES  → **nothing fails**

The last case is silent because the `CATEGORIES` contract checks a **fixed set**. Leave
`CATEGORIES` alone and those tests pass while nobody sees the new name in the conf. The
model falls into the UI's `__unknown__` bucket and has no name in the category filter.

The three dicts are checked together because filling one is only part of the job.
`CATEGORIES` holds the label (6 languages) and icon, `EXAMPLE_TYPES` how to draw the result,
`SAMPLE_IMAGES` which input to run. Miss any one and the task breaks somewhere on screen.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _config():
    sys.path.insert(0, str(ROOT / "dx_modelzoo"))
    from core import config

    return config


def _conf_categories() -> set[str]:
    sys.path.insert(0, str(ROOT))
    from dx_modelzoo.core.catalog import parse_test_models_conf

    return {m["category"] for m in parse_test_models_conf() if m.get("category")}


@pytest.mark.parametrize("table", ["CATEGORIES", "EXAMPLE_TYPES", "SAMPLE_IMAGES"])
def test_every_category_in_the_conf_is_declared(table):
    declared = getattr(_config(), table)
    used = _conf_categories()
    # EXAMPLE_TYPES and SAMPLE_IMAGES are TaskTables: per-model names (face_landmark …) resolve through their legacy pair
    missing = sorted(c for c in used if c not in declared)
    assert not missing, (
        f"test_models.conf 가 쓰는 카테고리가 {table} 에 없다: {missing}\n"
        f"  → dx_modelzoo/core/config.py 의 {table} 에 추가해야 한다.\n"
        f"  → 넣지 않으면 그 모델은 UI 의 __unknown__ 으로 빠지고 아무 오류도 나지 않는다."
    )


def test_the_three_tables_agree_with_each_other():
    """Filling one of the three and forgetting the others is the most common mistake."""
    cfg = _config()
    # Both tables are TaskTables: a per-model name (image_classification …) finds the value of its legacy name
    # (classification) through shared/tasks.py, so no task is written twice. Check lookup, not keys.
    cats = set(cfg.CATEGORIES)
    no_example = sorted(c for c in cats if c not in cfg.EXAMPLE_TYPES)
    no_sample = sorted(c for c in cats if c not in cfg.SAMPLE_IMAGES)
    assert not no_example, f"EXAMPLE_TYPES 가 모르는 task: {no_example}"
    assert not no_sample, f"SAMPLE_IMAGES 가 모르는 task: {no_sample}"
    for name, table in (("EXAMPLE_TYPES", cfg.EXAMPLE_TYPES), ("SAMPLE_IMAGES", cfg.SAMPLE_IMAGES)):
        extra = sorted(set(table) - cats)
        assert not extra, f"CATEGORIES 에 없는 {name} key: {extra}"


def test_each_sample_image_actually_exists():
    """SAMPLE_IMAGES holds paths. A path to nothing makes its consumers fall back **silently**
    to another image: server.py's default image pick uses `images[0]` when the file name is
    not in the list. No error, just the wrong picture.

    dx_app replaces samples between releases, so a stale entry is easy to miss without this
    contract.

    Uses `exists()`, not `is_file()`: embedding and reid use image **pairs**, so the path is a
    directory (3 images in `sample/img/face_pair/`).
    """
    cfg = _config()
    from dx_modelzoo.core.config import DX_APP_ROOT

    from shared import dx_app_layout as layout
    from shared.tasks import NEW_TASKS
    from tests.installed_sdk import require_dx_app
    require_dx_app("sample")
    legacy_root = layout.detect(DX_APP_ROOT) == layout.LEGACY

    missing = []
    for category, rel in cfg.SAMPLE_IMAGES.items():
        if not rel:
            continue
        # Samples for the newer tasks (sample/vpr/ …) exist only in a per-model layout dx_app
        if legacy_root and category in NEW_TASKS:
            continue
        if not (Path(DX_APP_ROOT) / rel).exists():
            missing.append(f"{category} -> {rel}")
    assert not missing, "SAMPLE_IMAGES 가 없는 경로를 가리킨다:\n  " + "\n  ".join(missing)


def test_sample_images_agree_with_the_runtime_source_of_truth():
    """The `test_models.conf` header says: "Source of truth: scripts/run_examples.sh".

    The studio's SAMPLE_IMAGES is a copy of that table, and copies drift silently: the path
    strings live in this repository and the files in the dx_app repository, so neither CI
    sees both. This contract closes that gap.
    """
    import re

    from dx_modelzoo.core.config import DX_APP_ROOT

    script = Path(DX_APP_ROOT) / "scripts" / "run_examples.sh"
    if not script.is_file():
        pytest.skip(f"run_examples.sh 없음: {script}")
    block = re.search(r"CATEGORY_IMAGE=\((.*?)\)", script.read_text(encoding="utf-8"), re.S)
    assert block, "run_examples.sh 에서 CATEGORY_IMAGE 표를 찾지 못했다"
    truth = dict(re.findall(r"\[([a-z_0-9]+)\]=\"([^\"]+)\"", block.group(1)))
    assert truth, "CATEGORY_IMAGE 표가 비어 보인다 — 파싱이 틀렸을 수 있다"

    cfg = _config()
    # The per-model dx_app table has both the legacy name ([reid] = pair folder) and the new one ([person_reid] =
    # one query image). The studio treats the pair as one slot, so when both exist only this checkout's name counts.
    from shared import dx_app_layout as layout
    from shared.tasks import canonical, legacy
    per_model = layout.detect(DX_APP_ROOT) == layout.PER_MODEL
    drift = []
    for category, path in truth.items():
        current = canonical(category) if per_model else legacy(category)
        if current != category and current in truth:
            continue
        mine = cfg.SAMPLE_IMAGES.get(category)
        if mine is None:
            continue  # a missing declaration is caught by the contracts above
        if mine.rstrip("/") != path.rstrip("/"):
            drift.append(f"{category}: studio={mine!r} != run_examples.sh={path!r}")
    assert not drift, "SAMPLE_IMAGES 가 진짜 출처와 어긋난다:\n  " + "\n  ".join(drift)

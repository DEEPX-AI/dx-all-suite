"""Run-tab dataset selection: get_images must surface the valid inputs for a
category, including the special non-sample/img inputs (LiDAR .bin, DOPE png)."""
import pytest

from dx_app.core import assets
from dx_app.core.config import CAT_IMAGE, DX_APP_ROOT


def _exists(rel):
    return (DX_APP_ROOT / rel).exists()


def test_get_images_no_category_is_sample_img_only():
    """Back-compat: no category → the sample/img gallery (jpg/png/bmp only)."""
    imgs = assets.get_images()
    assert isinstance(imgs, list)
    assert all(p.startswith("sample/img/") for p in imgs)


def test_get_images_general_category_returns_sample_img():
    imgs = assets.get_images("object_detection")
    assert all(p.startswith("sample/img/") for p in imgs)


@pytest.mark.skipif(
    not _exists("sample/kitti/velodyne/000049.bin"),
    reason="velodyne sample not present on this board",
)
def test_get_images_3d_lists_velodyne_bins_not_jpgs():
    """3d_object_detection needs LiDAR .bin — surface the velodyne dir, and do NOT
    offer the sample/img jpgs (which would silently break the model)."""
    imgs = assets.get_images("3d_object_detection")
    assert imgs, "expected velodyne .bin inputs"
    assert all(p.endswith(".bin") for p in imgs)
    assert CAT_IMAGE["3d_object_detection"] in imgs


@pytest.mark.skipif(
    not _exists("sample/dope/000000.png"),
    reason="dope sample not present on this board",
)
def test_get_images_pose_lists_dope_dir():
    imgs = assets.get_images("object_pose_estimation")
    assert imgs
    assert CAT_IMAGE["object_pose_estimation"] in imgs
    # dope inputs live outside sample/img
    assert all(not p.startswith("sample/img/") for p in imgs)

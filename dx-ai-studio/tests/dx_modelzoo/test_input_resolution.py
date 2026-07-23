"""Input resolution is derivable from the .dxnn (dx_engine reports the input tensor
shape), so models the source left at 0x0 must still show a real resolution."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "dx_modelzoo"))


def _models():
    from core import catalog as C
    return {m["id"]: m for m in C.get_catalog()["models"]}


def _res(m):
    s = m.get("specification") or {}
    return s.get("input_resolution") or (
        f"{s.get('input_width')}x{s.get('input_height')}" if s.get("input_width") else None)


def test_every_model_has_input_resolution():
    ms = _models()
    missing = [mid for mid, m in ms.items() if not _res(m)]
    assert not missing, f"input_resolution missing for: {missing[:10]}"


def test_known_resolutions_from_dxnn():
    ms = _models()
    # casvit_t / deitbase384 report their real input tensor shape (staging renamed
    # deitbase384_hug -> deitbase384; casvit_xs was removed from the staging catalog).
    assert ms["casvit_t"]["specification"]["input_resolution"] == "224x224x3"
    assert ms["deitbase384"]["specification"]["input_resolution"] == "384x384x3"

"""The Pipeline Builder offers a camera source.

Without v4l2src in the element palette (only urisourcebin and rtspsrc), a pipeline cannot read a USB camera, although
the AI Help knowledge lists v4l2src as the camera source.
"""
from dx_stream.core import elements


def test_v4l2src_is_a_source_with_a_device_property():
    cat = {e["name"]: e for e in elements.ELEMENTS} if hasattr(elements, "ELEMENTS") else None
    if cat is None:
        cat = {e["name"]: e for e in elements.get_elements()}
    v = cat["v4l2src"]
    assert v["category"] == "source"
    assert [p["name"] for p in v["properties"]] == ["device"]
    assert v["description_en"] and v["description_ko"]

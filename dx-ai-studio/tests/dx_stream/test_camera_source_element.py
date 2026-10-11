"""The Pipeline Builder offers a camera source (2026-10-11 real-use audit).

The element palette had urisourcebin and rtspsrc only, so a pipeline could not read a USB camera although the AI Help
knowledge lists v4l2src as the camera source. Verified with a v4l2loopback camera: preset 0 with its source swapped
for v4l2src device=/dev/video0 streams detections.
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

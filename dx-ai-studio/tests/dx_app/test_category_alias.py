"""A run request's category is accepted under either its legacy or its per-model name.

In the per-model dx_app layout CATEGORIES has oriented_object_detection but not obb_detection. Saved recent runs,
links and external clients that send obb_detection must not get a 400 "Unknown category": a name with a counterpart
is mapped to it (in the other direction on a legacy checkout).
"""
from unittest.mock import patch


def _server():
    import server   # after conftest has put dx_app on sys.path (as in test_security_paths)
    return server


def test_a_legacy_category_is_taken_as_its_per_model_pair():
    server = _server()
    with patch.object(server, "CATEGORIES", ["object_detection", "oriented_object_detection"]):
        assert server._require_category("obb_detection") == "oriented_object_detection"
        assert server._require_category("oriented_object_detection") == "oriented_object_detection"


def test_a_per_model_category_is_taken_as_its_legacy_pair_on_main():
    server = _server()
    with patch.object(server, "CATEGORIES", ["object_detection", "obb_detection"]):
        assert server._require_category("oriented_object_detection") == "obb_detection"


def test_unknown_and_traversal_are_still_refused():
    server = _server()
    with patch.object(server, "CATEGORIES", ["object_detection"]):
        for bad in ("nope", "../x", "obb_detection"):
            try:
                server._require_category(bad)
            except ValueError:
                continue
            raise AssertionError(f"{bad!r} accepted")


def test_the_payload_carries_the_resolved_name():
    server = _server()
    data = {"category": "obb_detection", "model_name": "yolo26-n-obb_1024x1024",
            "model_file": "assets/models/yolo26-n-obb_1024x1024.dxnn"}
    with patch.object(server, "CATEGORIES", ["oriented_object_detection"]), \
         patch.object(server, "_require_model_file", lambda _f: None):
        err, _code = server._validate_inference_payload(data)
    assert err is None, err
    assert data["category"] == "oriented_object_detection"

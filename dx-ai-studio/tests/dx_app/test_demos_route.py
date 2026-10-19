# tests/dx_app/test_demos_route.py
import os, sys, json, unittest
_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, _root); sys.path.insert(0, os.path.join(_root, 'dx_app', 'core'))
sys.path.insert(0, os.path.join(_root, 'shared'))

class TestDemosPayload(unittest.TestCase):
    def test_build_demos_payload_shape(self):
        # The route delegates to a pure builder so it is unit-testable without HTTP.
        from dx_app.core.demos import build_demos_payload
        p = build_demos_payload()
        self.assertIn('ok', p); self.assertIn('demos', p); self.assertIn('groups', p)
        if p['demos']:
            d = p['demos'][0]
            self.assertIn('avail', d)
            for k in ('cpp_sync','py_sync','py_sync_cpp_postprocess','model_exists'):
                self.assertIn(k, d['avail'])

if __name__ == '__main__':
    unittest.main()


def test_the_payload_says_which_sample_media_is_on_disk(monkeypatch, tmp_path):
    """Run Demo must not default to a sample video that has not been downloaded: on a machine without assets/videos,
    a Video default makes Run fail at once with 'File not found'."""
    from dx_app.core import demos

    (tmp_path / "sample" / "img").mkdir(parents=True)
    (tmp_path / "sample" / "img" / "street.jpg").write_bytes(b"x")
    monkeypatch.setattr(demos, "_dx_app_root", lambda: tmp_path)
    monkeypatch.setattr(demos, "list_demos", lambda: {"ok": True, "groups": ["Detection"], "demos": [{
        "idx": 0, "label": "Object Detection (YOLOv7)", "group": "Detection", "model": "yolov7.dxnn",
        "category": "object_detection", "model_name": "yolov7", "py_base": "yolov7", "cpp_base": "yolov7",
        "default_video": "assets/videos/nope.mp4", "default_image": "sample/img/street.jpg",
        "async_full": True, "image_only": False}]})
    d = demos.build_demos_payload()["demos"][0]
    assert d["media"] == {"video": False, "image": True}

# tests/dx_app/test_demos.py
"""dx_app run_demo.sh parser."""
import os, sys, tempfile, unittest
from pathlib import Path

_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, _root)
sys.path.insert(0, os.path.join(_root, 'dx_app', 'core'))
sys.path.insert(0, os.path.join(_root, 'shared'))

SAMPLE = '''#!/bin/bash
DEMO_LABELS=(
    # ── Detection (2) ──
    "Object Detection         (YOLOv7)"
    "Face Detection           (SCRFD500M)"
    # ── Classification (1) ──
    "Classification           (ResNet50)"
)
DEMO_GROUPS=(
    "Detection" "Detection"
    "Classification"
)
DEMO_CPP_BASE=(
    yolov7 scrfd500m
    resnet50
)
DEMO_PY_DIR=(
    "object_detection/yolov7"
    "face_detection/scrfd500m"
    "classification/resnet50"
)
DEMO_PY_BASE=(
    yolov7 scrfd500m
    resnet50
)
DEMO_MODEL=(
    yolov7_640x640.dxnn scrfd-500m_640x640.dxnn
    resnet50_224x224.dxnn
)
DEMO_VIDEO=(
    "assets/videos/dogs.mp4"
    "assets/videos/faces.mp4"
    "assets/videos/street.mp4"
)
DEMO_IMAGE=(
    "sample/img/a.jpg"
    "sample/img/b.jpg"
    "sample/img/c.jpg"
)
DEMO_PY_ASYNC=(
    full full
    no_py_async
)
DEMO_IMAGE_ONLY=(
    0 0
    0
)
'''

class TestParseRunDemo(unittest.TestCase):
    def _parse(self):
        from dx_app.core.demos import parse_run_demo
        with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False) as f:
            f.write(SAMPLE); p = f.name
        try:
            return parse_run_demo(Path(p))
        finally:
            os.unlink(p)

    def test_count_and_order(self):
        d = self._parse()
        self.assertEqual(len(d), 3)
        self.assertEqual(d[0]['label'], "Object Detection         (YOLOv7)")
        self.assertEqual(d[0]['group'], "Detection")
        self.assertEqual(d[0]['category'], "object_detection")
        self.assertEqual(d[0]['model_name'], "yolov7")
        self.assertEqual(d[0]['model'], "yolov7_640x640.dxnn")

    def test_async_and_image_only_flags(self):
        d = self._parse()
        self.assertTrue(d[0]['async_full'])
        self.assertFalse(d[2]['async_full'])   # resnet50 = no_py_async
        self.assertFalse(d[0]['image_only'])

    def test_defaults_media(self):
        d = self._parse()
        self.assertEqual(d[0]['default_video'], "assets/videos/dogs.mp4")
        self.assertEqual(d[0]['default_image'], "sample/img/a.jpg")

    def test_malformed_returns_empty(self):
        from dx_app.core.demos import parse_run_demo
        with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False) as f:
            f.write("not a real script\n"); p = f.name
        try:
            self.assertEqual(parse_run_demo(Path(p)), [])
        finally:
            os.unlink(p)

    def test_image_only_flag_true(self):
        from dx_app.core.demos import parse_run_demo
        sample = SAMPLE.replace(
            '"classification/resnet50"',
            '"embedding/resnet50"',
        )
        with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False) as f:
            f.write(sample); p = f.name
        try:
            d = parse_run_demo(Path(p))
            self.assertTrue(d[2]['image_only'])
        finally:
            os.unlink(p)

    def test_length_mismatch_returns_empty(self):
        from dx_app.core.demos import parse_run_demo
        sample = SAMPLE.replace(
            'DEMO_GROUPS=(\n    "Detection" "Detection"\n    "Classification"\n)',
            'DEMO_GROUPS=(\n    "Detection" "Detection"\n)'
        )
        with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False) as f:
            f.write(sample); p = f.name
        try:
            self.assertEqual(parse_run_demo(Path(p)), [])
        finally:
            os.unlink(p)

    def test_list_demos_real_file(self):
        try:
            from dx_app.core.demos import list_demos
        except Exception:
            self.skipTest("dx_app.core.demos not importable in this environment")
        r = list_demos()
        if not r["ok"]:
            self.skipTest("list_demos() could not locate/parse the real run_demo.sh in this environment")
        self.assertTrue(r["ok"] is True)
        self.assertEqual(len(r["demos"]), 23)
        self.assertTrue(len(r["groups"]) > 0)
        self.assertEqual(len(set(r["groups"])), len(r["groups"]))
        self.assertEqual(r["groups"][0], "Detection")

if __name__ == '__main__':
    unittest.main()

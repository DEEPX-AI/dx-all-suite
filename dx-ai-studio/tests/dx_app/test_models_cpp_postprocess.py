import os, sys, unittest
from unittest.mock import patch
_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, _root); sys.path.insert(0, os.path.join(_root, 'dx_app', 'core'))
sys.path.insert(0, os.path.join(_root, 'shared'))

class TestCppPostprocessFlags(unittest.TestCase):
    def test_yolov7_has_cpp_postprocess_flags(self):
        from dx_app.core import models

        # The registry deliberately hides models whose optional DXNN assets have
        # not been installed. This test verifies source-runner discovery only.
        with patch.object(
            models,
            "_required_dxnn_exists",
            side_effect=lambda model_file: model_file == "assets/models/yolov7_640x640.dxnn",
        ):
            discovered = models.get_models()

        y = next((m for m in discovered if m['name'].startswith('yolov7')
                  and m.get('category') == 'object_detection'), None)
        self.assertIsNotNone(y, "yolov7 demo model must be present")
        self.assertIn('py_sync_cpp_postprocess', y)
        self.assertIn('py_async_cpp_postprocess', y)
        self.assertTrue(y['py_sync_cpp_postprocess'])   # script exists in example tree

if __name__ == '__main__':
    unittest.main()

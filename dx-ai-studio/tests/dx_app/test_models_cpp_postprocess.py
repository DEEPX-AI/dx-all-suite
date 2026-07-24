import os, sys, unittest
_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, _root); sys.path.insert(0, os.path.join(_root, 'dx_app', 'core'))
sys.path.insert(0, os.path.join(_root, 'shared'))

class TestCppPostprocessFlags(unittest.TestCase):
    def test_yolov7_has_cpp_postprocess_flags(self):
        from dx_app.core.models import get_models   # returns list(models.values())
        models = get_models()
        y = next((m for m in models if m['name'].startswith('yolov7')
                  and m.get('category') == 'object_detection'), None)
        self.assertIsNotNone(y, "yolov7 demo model must be present")
        self.assertIn('py_sync_cpp_postprocess', y)
        self.assertIn('py_async_cpp_postprocess', y)
        self.assertTrue(y['py_sync_cpp_postprocess'])   # script exists in example tree

if __name__ == '__main__':
    unittest.main()

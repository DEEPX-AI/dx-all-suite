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

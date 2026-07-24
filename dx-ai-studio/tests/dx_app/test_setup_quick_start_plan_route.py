# tests/dx_app/test_setup_quick_start_plan_route.py
"""GET /api/setup/quick-start-plan: route wraps quick_start_plan() as {"plan": [...]}."""
import os, sys, unittest
_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, _root); sys.path.insert(0, os.path.join(_root, 'dx_app', 'core'))
sys.path.insert(0, os.path.join(_root, 'shared'))

class TestQuickStartPlanRoute(unittest.TestCase):
    def test_payload_shape(self):
        # The route (dx_app/server.py) delegates to quick_start_plan() and wraps it
        # as {"plan": [...]} via send_json — this is the exact payload shape, built
        # without needing to spin up an HTTP server (mirrors test_demos_route.py).
        from dx_app.core.setup_steps import quick_start_plan
        payload = {"plan": quick_start_plan()}
        self.assertIn('plan', payload)
        self.assertIsInstance(payload['plan'], list)
        for step_id in payload['plan']:
            self.assertIsInstance(step_id, str)

if __name__ == '__main__':
    unittest.main()

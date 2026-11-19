# tests/dx_app/test_quick_start.py
"""Demo Quick Start chain: quick_start_plan() skip logic."""
import os, sys, unittest
from unittest.mock import patch
_root=os.path.join(os.path.dirname(__file__),'..','..')
sys.path.insert(0,_root); sys.path.insert(0,os.path.join(_root,'dx_app','core'))
sys.path.insert(0,os.path.join(_root,'shared'))

class TestQuickStartPlan(unittest.TestCase):
    def test_skips_satisfied_steps(self):
        from dx_app.core import setup_steps
        fake={"dx-app-deps":{"ok":True},"dx-rt-deps":{"ok":True},"dx-rt-build":{"ok":False},
              "dx-driver":{"ok":True},"dx-app-build":{"ok":False},"dx-app-setup":{"ok":False},
              "inference-venv":{"ok":True}}
        with patch.object(setup_steps,'setup_status',return_value=fake):
            plan=setup_steps.quick_start_plan()
        self.assertEqual(plan,["dx-rt-build","dx-app-build","dx-app-setup"])

    def test_all_done_empty_plan(self):
        from dx_app.core import setup_steps
        done={k:{"ok":True} for k in
              ["dx-app-deps","dx-rt-deps","dx-rt-build","dx-driver","dx-app-build","dx-app-setup","inference-venv"]}
        with patch.object(setup_steps,'setup_status',return_value=done):
            self.assertEqual(setup_steps.quick_start_plan(),[])

    def test_quick_start_includes_python_inference_deps(self):
        """Without it a "done" Quick Start left no numpy+cv2+dx_engine interpreter: Use Default crashed."""
        from dx_app.core import setup_steps
        fake={k:{"ok":True} for k in ["dx-app-deps","dx-rt-deps","dx-rt-build","dx-driver","dx-app-build","dx-app-setup"]}
        fake["inference-venv"]={"ok":False}
        with patch.object(setup_steps,'setup_status',return_value=fake):
            self.assertEqual(setup_steps.quick_start_plan(),["inference-venv"])

    def test_python_deps_run_after_runtime_and_driver(self):
        from dx_app.core import setup_steps
        order=setup_steps._QUICK_ORDER
        self.assertGreater(order.index("inference-venv"),order.index("dx-rt-build"))
        self.assertGreater(order.index("inference-venv"),order.index("dx-driver"))

if __name__=='__main__':
    unittest.main()

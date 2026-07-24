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
              "dx-driver":{"ok":True},"dx-app-build":{"ok":False},"dx-app-setup":{"ok":False}}
        with patch.object(setup_steps,'setup_status',return_value=fake):
            plan=setup_steps.quick_start_plan()
        self.assertEqual(plan,["dx-rt-build","dx-app-build","dx-app-setup"])

    def test_all_done_empty_plan(self):
        from dx_app.core import setup_steps
        done={k:{"ok":True} for k in
              ["dx-app-deps","dx-rt-deps","dx-rt-build","dx-driver","dx-app-build","dx-app-setup"]}
        with patch.object(setup_steps,'setup_status',return_value=done):
            self.assertEqual(setup_steps.quick_start_plan(),[])

if __name__=='__main__':
    unittest.main()

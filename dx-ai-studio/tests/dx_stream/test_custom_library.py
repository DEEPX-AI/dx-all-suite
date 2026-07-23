"""custom_library.py 테스트"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestCustomLibraryModule:
    def test_module_importable(self):
        from core.custom_library import CustomLibraryManager
        mgr = CustomLibraryManager()
        assert callable(mgr.list_libraries)
        assert callable(mgr.get_available_so)

    def test_list_libraries_returns_list(self):
        from core.custom_library import CustomLibraryManager
        mgr = CustomLibraryManager()
        result = mgr.list_libraries()
        assert isinstance(result, list)

    def test_get_available_so_returns_list(self):
        from core.custom_library import CustomLibraryManager
        mgr = CustomLibraryManager()
        result = mgr.get_available_so()
        assert isinstance(result, list)
        # Each entry should be a dict with 'name' key
        for item in result:
            assert "name" in item

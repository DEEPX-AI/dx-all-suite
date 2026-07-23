#!/usr/bin/env python3
"""DX-APP 경로/파일명 보안 테스트 — Phase 5 Task 1.1.

Audit IDs: 1, 2, 3, 4, 5, 18, 85, 86, 87, 88
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# shared / core 접근 경로 추가
_STUDIO_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_STUDIO_DIR))
sys.path.insert(0, str(_STUDIO_DIR / "shared"))
sys.path.insert(0, str(_STUDIO_DIR / "dx_app"))
sys.path.insert(0, str(_STUDIO_DIR / "dx_app" / "core"))


# 1. _resolve_under  — 경로 허용 목록 헬퍼
class TestResolveUnder(unittest.TestCase):
    """_resolve_under 헬퍼가 허용된 루트만 통과시키는지 검증."""

    def _get_fn(self):
        from dx_app_security import resolve_under
        return resolve_under

    def test_valid_subpath(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        result = fn(str(root / "test_security_paths.py"), (root,))
        self.assertEqual(result, root / "test_security_paths.py")

    def test_traversal_rejected(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        with self.assertRaises(ValueError):
            fn("/etc/passwd", (root,))

    def test_relative_traversal_rejected(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        with self.assertRaises(ValueError):
            fn(str(root / ".." / ".." / "etc" / "passwd"), (root,))

    def test_root_itself_allowed(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        result = fn(str(root), (root,))
        self.assertEqual(result, root)

    def test_symlink_under_root_allowed_when_target_outside(self):
        fn = self._get_fn()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "assets"
            videos = root / "videos"
            outside = Path(tmp) / "outside"
            outside.mkdir()
            videos.mkdir(parents=True)
            target = outside / "obb.mp4"
            target.write_bytes(b"video")
            link = videos / "obb.mp4"
            link.symlink_to(target)
            result = fn(str(link), (root,))
            self.assertEqual(result, link)
            self.assertTrue(result.is_file())


# 1b. resolve_existing_path — 파일 OR 디렉터리 허용 (reid/embedding pair dir)
class TestResolveExistingPath(unittest.TestCase):
    """resolve_existing_path가 루트 안의 디렉터리를 허용하되 탈출은 막는지 검증."""

    def _get_fn(self):
        from dx_app_security import resolve_existing_path
        return resolve_existing_path

    def test_directory_accepted(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        sub = root  # the test dir itself is a directory under root
        self.assertEqual(fn(str(sub), (root,)), root)

    def test_file_accepted(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        f = root / "test_security_paths.py"
        self.assertEqual(fn(str(f), (root,)), f)

    def test_traversal_rejected(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        with self.assertRaises(ValueError):
            fn("/etc", (root,))

    def test_missing_path_rejected(self):
        fn = self._get_fn()
        root = Path(__file__).resolve().parent
        with self.assertRaises(ValueError):
            fn(str(root / "does_not_exist_xyz"), (root,))


# 2. sanitize_filename — 업로드 파일명 안전 처리
class TestSanitizeFilename(unittest.TestCase):
    """업로드 파일명에서 경로 구분자 및 위험 패턴을 제거."""

    def _get_fn(self):
        from dx_app_security import sanitize_filename
        return sanitize_filename

    def test_plain_name_unchanged(self):
        fn = self._get_fn()
        self.assertEqual(fn("model.onnx", (".onnx",)), "model.onnx")

    def test_traversal_stripped(self):
        fn = self._get_fn()
        result = fn("../../evil.onnx", (".onnx",))
        self.assertEqual(result, "evil.onnx")

    def test_backslash_traversal_stripped(self):
        fn = self._get_fn()
        result = fn("..\\..\\evil.onnx", (".onnx",))
        self.assertEqual(result, "evil.onnx")

    def test_disallowed_extension_rejected(self):
        fn = self._get_fn()
        with self.assertRaises(ValueError):
            fn("payload.sh", (".onnx",))

    def test_empty_name_rejected(self):
        fn = self._get_fn()
        with self.assertRaises(ValueError):
            fn("", (".onnx",))

    def test_dot_only_rejected(self):
        fn = self._get_fn()
        with self.assertRaises(ValueError):
            fn("..", (".onnx",))


# 3. safe_content_disposition — 다운로드 헤더 안전 처리
class TestSafeContentDisposition(unittest.TestCase):
    """Content-Disposition 헤더 값에서 파일명을 안전하게 인용."""

    def _get_fn(self):
        from dx_app_security import safe_content_disposition
        return safe_content_disposition

    def test_simple_name(self):
        fn = self._get_fn()
        result = fn("attachment", "report.csv")
        self.assertIn('filename="report.csv"', result)

    def test_quotes_escaped(self):
        fn = self._get_fn()
        result = fn("inline", 'my "file".onnx')
        self.assertNotIn('"file"', result.split("filename=")[1].replace('\\"', ''))

    def test_traversal_in_name_stripped(self):
        fn = self._get_fn()
        result = fn("attachment", "../../etc/passwd")
        self.assertIn("passwd", result)
        self.assertNotIn("..", result)


# 5. fs_list / fs_read 경로 제한 (filesystem.py)
class TestFsListRestriction(unittest.TestCase):
    """fs_list 가 허용된 루트 외부를 거부해야 함."""

    def test_root_listing_rejected(self):
        from filesystem import fs_list
        result = fs_list("/")
        self.assertIn("error", result)

    def test_etc_listing_rejected(self):
        from filesystem import fs_list
        result = fs_list("/etc")
        self.assertIn("error", result)


class TestFsReadRestriction(unittest.TestCase):
    """fs_read API가 허용된 루트 외부 파일 읽기를 거부해야 함."""

    def test_etc_passwd_read_rejected_via_route(self):
        import server

        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "GET"
        handler.url_path = "/api/fs/read"
        handler.query = {"path": ["/etc/passwd"]}
        handler.handle_chat_routes = lambda _engine: False
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})

        handler.route()

        self.assertEqual(captured.get("code"), 403)
        self.assertIn("outside allowed roots", captured.get("data", {}).get("error", ""))


# 6. /outputs/ 경로 순회 차단
class TestOutputsTraversal(unittest.TestCase):
    """/outputs/../secret.txt 같은 경로 순회 요청을 403으로 거부."""

    def test_traversal_outside_outputs_dir_returns_403(self):
        import server

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs_dir = Path(tmpdir) / "outputs"
            outputs_dir.mkdir()
            # outputs 디렉토리 밖에 비밀 파일 생성
            secret = Path(tmpdir) / "secret.txt"
            secret.write_text("TOP SECRET")

            captured = {}
            handler = object.__new__(server.Handler)
            handler.command = "GET"
            handler.url_path = "/outputs/../secret.txt"
            handler.query = {}
            handler.handle_chat_routes = lambda _engine: False
            handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
            handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
            handler.send_response = lambda code: captured.update({"code": code})
            handler.send_header = lambda *a: None
            handler.end_headers = lambda: None
            handler.wfile = MagicMock()

            with patch.object(server, "OUTPUTS_DIR", outputs_dir):
                handler.route()

            self.assertEqual(captured.get("code"), 403,
                             f"Expected 403 for traversal but got {captured}")


class TestFileRouteTraversal(unittest.TestCase):
    """/file/ 경로도 DX_APP_ROOT 밖으로 나가면 403으로 거부해야 함."""

    def test_file_route_traversal_outside_dx_app_root_returns_403(self):
        import server

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "dx_app_root"
            root.mkdir()
            secret = Path(tmpdir) / "secret.txt"
            secret.write_text("TOP SECRET")

            captured = {"body": b""}
            handler = object.__new__(server.Handler)
            handler.command = "GET"
            handler.url_path = "/file/../secret.txt"
            handler.query = {}
            handler.handle_chat_routes = lambda _engine: False
            handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
            handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
            handler.send_response = lambda code: captured.update({"code": code})
            handler.send_header = lambda *a: None
            handler.end_headers = lambda: None
            handler.wfile = MagicMock()

            with patch.object(server, "DX_APP_ROOT", root):
                handler.route()

            self.assertEqual(captured.get("code"), 403,
                             f"Expected 403 for /file/ traversal but got {captured}")
            handler.wfile.write.assert_not_called()


# 7. /api/fs/read 존재 오라클 제거
class TestFsReadExistenceOracle(unittest.TestCase):
    """허용 루트 밖 경로는 존재 여부와 무관하게 항상 403을 반환해야 함."""

    def test_missing_outside_path_returns_403_not_404(self):
        import server

        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "GET"
        handler.url_path = "/api/fs/read"
        handler.query = {"path": ["/etc/__definitely_missing_phase5__"]}
        handler.handle_chat_routes = lambda _engine: False
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})

        handler.route()

        self.assertEqual(captured.get("code"), 403,
                         f"Expected 403 for outside missing path, got {captured}")


class TestLabNoHardcodedPassword(unittest.TestCase):
    def test_no_dev_password_symbol_or_literal(self):
        root = Path(__file__).resolve().parent.parent.parent
        config_src = (root / "dx_app" / "core" / "config.py").read_text()
        developer_src = (root / "dx_app" / "core" / "developer.py").read_text()
        assert "DEV_PASSWORD" not in config_src
        assert "DEV_PASSWORD" not in developer_src
        assert "02230301" not in config_src + developer_src

    def test_no_public_extract_sentinel(self):
        root = Path(__file__).resolve().parent.parent.parent
        developer_src = (root / "dx_app" / "core" / "developer.py").read_text()
        server_src = (root / "dx_app" / "server.py").read_text()
        assert "__public__" not in developer_src
        assert "__public__" not in server_src


class TestPhase7PathResolvers(unittest.TestCase):
    def test_resolve_existing_file_under_allowed_root(self):
        from dx_app_security import resolve_existing_file
        root = Path(__file__).resolve().parent
        result = resolve_existing_file(str(root / "test_security_paths.py"), (root,), (".py",))
        self.assertEqual(result, root / "test_security_paths.py")

    def test_resolve_existing_file_rejects_extension(self):
        from dx_app_security import resolve_existing_file
        root = Path(__file__).resolve().parent
        with self.assertRaises(ValueError):
            resolve_existing_file(str(root / "test_security_paths.py"), (root,), (".onnx",))

    def test_resolve_output_child_rejects_absolute_and_traversal(self):
        from dx_app_security import resolve_output_child
        root = Path(__file__).resolve().parent
        for bad in ("/tmp/evil", "../../evil", "nested/../../evil"):
            with self.assertRaises(ValueError):
                resolve_output_child(bad, root)


class TestPhase7RoutePathValidation(unittest.TestCase):
    def _post_route(self, path, payload, headers=None):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "POST"
        handler.url_path = path
        handler.query = {}
        handler.headers = headers or {}
        handler.handle_chat_routes = lambda _engine: False
        handler.read_json_body = lambda: payload
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        return captured

    def test_extract_rejects_outside_model_path(self):
        captured = self._post_route("/api/extract", {"model_path": "/etc/passwd", "lang": "both"})
        self.assertIn(captured.get("code"), (400, 403))

    def test_dev_extract_requires_lab_session(self):
        captured = self._post_route("/api/dev/extract", {"model_path": "/etc/passwd"})
        self.assertEqual(captured.get("code"), 403)

    def test_serve_onnx_rejects_outside_path(self):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "GET"
        handler.url_path = "/api/serve_onnx"
        handler.query = {"path": ["/etc/passwd"]}
        handler.handle_chat_routes = lambda _engine: False
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        self.assertIn(captured.get("code"), (400, 403))


class TestPhase7ConfirmationChecks(unittest.TestCase):
    def _post_route(self, path, payload, headers=None):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "POST"
        handler.url_path = path
        handler.query = {}
        handler.headers = headers or {}
        handler.handle_chat_routes = lambda _engine: False
        handler.read_json_body = lambda: payload
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        return captured

    def test_delete_requires_confirmation(self):
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/delete_model",
            {"model_name": "test_model", "lang": "both"},
            headers={"X-Lab-Token": tok}
        )
        self.assertIn(captured.get("code"), (400,))

    def test_git_push_requires_confirmation(self):
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/git_commit",
            {"message": "test", "push": True},
            headers={"X-Lab-Token": tok}
        )
        self.assertIn(captured.get("code"), (400,))


class TestOverwriteConfirmation(unittest.TestCase):
    """dev_add / dev_new_task must reject overwrites unless confirm_overwrite=True."""

    def test_dev_new_task_rejects_overwrite_without_confirm(self):
        """기존 파일이 존재할 때 confirm_overwrite=False → 400 반환."""
        from developer import lab_session, dev_new_task
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            cpp_common = Path(tmpdir) / "src" / "cpp_example" / "common"
            proc_dir = cpp_common / "processors"
            proc_dir.mkdir(parents=True)
            # Pre-create a file that would be generated
            (proc_dir / "my_task_postprocessor.hpp").write_text("existing")
            with patch("developer.CPP_DIR", Path(tmpdir) / "src" / "cpp_example"), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)):
                result = dev_new_task(tok, "my_task", lang="cpp", confirm_overwrite=False)
        self.assertIn("error", result)
        self.assertEqual(result.get("status"), 400)

    def test_dev_new_task_allows_overwrite_with_confirm(self):
        """기존 파일이 존재해도 confirm_overwrite=True → 정상 생성."""
        from developer import lab_session, dev_new_task
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            cpp_common = Path(tmpdir) / "src" / "cpp_example" / "common"
            proc_dir = cpp_common / "processors"
            proc_dir.mkdir(parents=True)
            (proc_dir / "ow_task_postprocessor.hpp").write_text("existing")
            with patch("developer.CPP_DIR", Path(tmpdir) / "src" / "cpp_example"), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)):
                result = dev_new_task(tok, "ow_task", lang="cpp", confirm_overwrite=True)
        self.assertTrue(result.get("ok"), result)

    def test_dev_new_task_no_conflict_passes(self):
        """기존 파일이 없으면 confirm_overwrite=False 도 정상."""
        from developer import lab_session, dev_new_task
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("developer.CPP_DIR", Path(tmpdir) / "src" / "cpp_example"), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)):
                result = dev_new_task(tok, "brand_new", lang="cpp", confirm_overwrite=False)
        self.assertTrue(result.get("ok"), result)

    def test_dev_add_rejects_overwrite_without_confirm(self):
        """기존 모델 디렉토리가 존재할 때 confirm_overwrite=False → 400 반환."""
        from developer import lab_session, dev_add
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            cpp_dir = Path(tmpdir) / "src" / "cpp_example"
            cat_dir = cpp_dir / "object_detection" / "test_model"
            cat_dir.mkdir(parents=True)
            with patch("developer.CPP_DIR", cpp_dir), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)), \
                 patch("developer.SCRIPTS_DIR", Path(tmpdir) / "scripts"):
                # Create dummy script so the "not found" check passes
                scripts = Path(tmpdir) / "scripts"
                scripts.mkdir(exist_ok=True)
                (scripts / "add_model.sh").write_text("#!/bin/bash\n")
                result = dev_add(tok, "test_model", "object_detection", "cpp",
                                 "object_detection", "", confirm_overwrite=False)
        self.assertIn("error", result)
        self.assertEqual(result.get("status"), 400)

    def test_dev_add_allows_overwrite_with_confirm(self):
        """기존 디렉토리 있어도 confirm_overwrite=True → 스크립트 실행."""
        from developer import lab_session, dev_add
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            cpp_dir = Path(tmpdir) / "src" / "cpp_example"
            cat_dir = cpp_dir / "object_detection" / "test_model2"
            cat_dir.mkdir(parents=True)
            scripts = Path(tmpdir) / "scripts"
            scripts.mkdir(exist_ok=True)
            (scripts / "add_model.sh").write_text("#!/bin/bash\necho ok")
            with patch("developer.CPP_DIR", cpp_dir), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)), \
                 patch("developer.SCRIPTS_DIR", scripts):
                result = dev_add(tok, "test_model2", "object_detection", "cpp",
                                 "object_detection", "", confirm_overwrite=True)
        # Should proceed to run script (ok or error from script, but no 400)
        self.assertNotEqual(result.get("status"), 400)

    def test_dev_add_rejects_traversal_category(self):
        """category는 알려진 카테고리여야 하며 경로 순회를 허용하지 않는다."""
        from developer import lab_session, dev_add
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts = Path(tmpdir) / "scripts"
            scripts.mkdir()
            (scripts / "add_model.sh").write_text("#!/bin/bash\necho ok")
            with patch("developer.CPP_DIR", Path(tmpdir) / "src" / "cpp_example"), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)), \
                 patch("developer.SCRIPTS_DIR", scripts):
                result = dev_add(tok, "test_model", "object_detection", "cpp",
                                 "../victim", "", confirm_overwrite=True)
        self.assertEqual(result.get("status"), 400)
        self.assertIn("category", result.get("error", "").lower())

    def test_dev_add_rejects_traversal_model_name(self):
        """model_name은 경로 컴포넌트로 쓰이므로 경로 순회를 허용하지 않는다."""
        from developer import lab_session, dev_add
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts = Path(tmpdir) / "scripts"
            scripts.mkdir()
            (scripts / "add_model.sh").write_text("#!/bin/bash\necho ok")
            with patch("developer.CPP_DIR", Path(tmpdir) / "src" / "cpp_example"), \
                 patch("developer.PY_DIR", Path(tmpdir) / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", Path(tmpdir)), \
                 patch("developer.SCRIPTS_DIR", scripts):
                result = dev_add(tok, "../../victim", "object_detection", "cpp",
                                 "object_detection", "", confirm_overwrite=True)
        self.assertEqual(result.get("status"), 400)
        self.assertIn("model name", result.get("error", "").lower())

    def test_dev_delete_rejects_traversal_model_name_without_deleting(self):
        """delete 확인 문자열만으로는 model_name 경로 순회를 허용하지 않는다."""
        from developer import lab_session, dev_delete
        tok = lab_session()["token"]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cpp_dir = root / "src" / "cpp_example"
            (cpp_dir / "object_detection").mkdir(parents=True)
            victim = root / "src" / "victim_dir"
            victim.mkdir(parents=True)
            with patch("developer.CPP_DIR", cpp_dir), \
                 patch("developer.PY_DIR", root / "src" / "python_example"), \
                 patch("developer.DX_APP_ROOT", root):
                result = dev_delete(tok, "../../victim_dir", lang="cpp",
                                    confirm="delete:../../victim_dir")
            self.assertTrue(victim.exists(), "Traversal target must not be deleted")
        self.assertEqual(result.get("status"), 400)
        self.assertIn("model name", result.get("error", "").lower())

    def test_server_passes_confirm_overwrite_to_new_task(self):
        """server.py가 dev_new_task에 confirm_overwrite를 전달하는지 소스 코드 검증."""
        root = Path(__file__).resolve().parent.parent.parent
        server_src = (root / "dx_app" / "server.py").read_text()
        # Find the route handler (path=="/api/dev/new_task") not the set definition
        idx = server_src.index('path=="/api/dev/new_task"')
        snippet = server_src[idx:idx+300]
        self.assertIn("confirm_overwrite", snippet)


class TestRunInferenceUploadPathValidation(unittest.TestCase):
    def test_upload_path_outside_allowed_roots_rejected(self):
        import inference
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            model = root / "model.dxnn"
            model.write_bytes(b"dummy")
            with patch.object(inference, "DX_APP_ROOT", root), \
                 patch.object(inference, "BUILD_DIR", root), \
                 patch.object(inference, "ASSETS_DIR", root), \
                 patch.object(inference, "SAMPLE_DIR", root), \
                 patch.object(inference, "OUTPUTS_DIR", root):
                result = inference.run_inference(
                    model_name="m", category="classification", model_file="model.dxnn",
                    input_type="image", upload_path="/etc/passwd"
                )
        self.assertIn("error", result)
        self.assertIn("outside", result["error"].lower())


class TestPublicInferenceRouteValidation(unittest.TestCase):
    """Public inference routes must reject unsafe path-derived inputs before execution."""

    def _post_route(self, path, payload, headers=None):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "POST"
        handler.url_path = path
        handler.query = {}
        handler.headers = headers or {}
        handler.handle_chat_routes = lambda _engine: False
        handler.read_json_body = lambda: payload
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        return captured

    def test_model_input_roots_include_asset_models_symlink_target(self):
        import server

        self.assertIn(server.ASSETS_DIR / "models", server.MODEL_INPUT_ROOTS)

    @patch("server.run_inference")
    def test_run_rejects_traversal_category_before_inference(self, mock_run):
        mock_run.return_value = {"ok": True}
        captured = self._post_route("/api/run", {
            "model_name": "safe_model",
            "category": "../etc",
            "model_file": "assets/models/safe_model.dxnn",
        })
        self.assertEqual(captured.get("code"), 400)
        mock_run.assert_not_called()

    @patch("server.run_inference")
    def test_run_accepts_symlinked_video_under_assets(self, mock_run):
        import config
        import server

        mock_run.return_value = {"ok": True}
        video = config.DX_APP_ROOT / "assets" / "videos" / "obb.mp4"
        if not video.is_file():
            self.skipTest(f"sample video missing: {video}")
        captured = self._post_route("/api/run", {
            "model_name": "yolo26n_obb",
            "category": "obb_detection",
            "model_file": "assets/models/yolo26n-obb.dxnn",
            "lang": "cpp",
            "variant": "async",
            "input_type": "video",
            "video_path": "assets/videos/obb.mp4",
        })
        self.assertEqual(captured.get("code"), 200, captured.get("data"))
        mock_run.assert_called_once()
        self.assertIn(server.DX_APP_ROOT, server.TEST_RUN_INPUT_ROOTS)

    @patch("server.run_inference")
    def test_run_rejects_outside_model_file_before_inference(self, mock_run):
        mock_run.return_value = {"ok": True}
        captured = self._post_route("/api/run", {
            "model_name": "safe_model",
            "category": "classification",
            "model_file": "/etc/passwd",
        })
        self.assertIn(captured.get("code"), (400, 403))
        mock_run.assert_not_called()

    @patch("server.run_multi")
    def test_run_multi_rejects_nested_traversal_category_before_inference(self, mock_run_multi):
        mock_run_multi.return_value = []
        captured = self._post_route("/api/run_multi", {
            "requests": [{
                "model_name": "safe_model",
                "category": "../etc",
                "model_file": "assets/models/safe_model.dxnn",
            }],
        })
        self.assertEqual(captured.get("code"), 400)
        mock_run_multi.assert_not_called()

    @patch("server.run_inference_live")
    def test_run_live_rejects_traversal_model_name_before_inference(self, mock_live):
        mock_live.return_value = {"job_id": "x"}
        captured = self._post_route("/api/run_live", {
            "model_name": "../safe_model",
            "category": "classification",
            "model_file": "assets/models/safe_model.dxnn",
        })
        self.assertEqual(captured.get("code"), 400)
        mock_live.assert_not_called()


class TestLegacyBackupSourceRemoval(unittest.TestCase):
    """Tracked backup server source must not retain removed auth bypass code."""

    def test_server_backup_source_removed(self):
        root = Path(__file__).resolve().parent.parent.parent
        self.assertFalse((root / "dx_app" / "server.py.bak").exists())



class TestCrossOriginLabSession(unittest.TestCase):
    """lab_session must reject non-local cross-origin callers."""

    def test_no_origin_succeeds(self):
        from developer import lab_session
        res = lab_session(origin=None)
        self.assertTrue(res.get("ok"))
        self.assertIn("token", res)

    def test_localhost_origin_succeeds(self):
        from developer import lab_session
        res = lab_session(origin="http://localhost:8080")
        self.assertTrue(res.get("ok"))

    def test_127_origin_succeeds(self):
        from developer import lab_session
        res = lab_session(origin="http://127.0.0.1:3000")
        self.assertTrue(res.get("ok"))

    def test_remote_origin_rejected(self):
        from developer import lab_session
        res = lab_session(origin="https://evil.example.com")
        self.assertEqual(res.get("status"), 403)
        self.assertNotIn("token", res)


class TestCrossOriginLabMutatingRoute(unittest.TestCase):
    """Lab mutating routes must reject hostile Origin even with valid token."""

    def _post_route(self, path, payload, headers=None):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "POST"
        handler.url_path = path
        handler.query = {}
        handler.headers = headers or {}
        handler.handle_chat_routes = lambda _engine: False
        handler.read_json_body = lambda: payload
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        return captured

    def test_add_model_rejects_remote_origin(self):
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/add_model",
            {"model_name": "x"},
            headers={"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
        )
        self.assertEqual(captured.get("code"), 403)

    def test_add_model_allows_no_origin(self):
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/add_model",
            {"model_name": "x"},
            headers={"X-Lab-Token": tok}
        )
        # Should not be 403 for origin reasons (may be other error)
        self.assertNotEqual(captured.get("code"), 403)

    def test_xdevtoken_not_accepted_on_lab_route(self):
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/delete_model",
            {"model_name": "x", "lang": "both"},
            headers={"X-Dev-Token": tok}
        )
        # Token sent via X-Dev-Token should be rejected on Lab routes (403 = no session)
        self.assertEqual(captured.get("code"), 403)


class TestBoundedSessionEviction(unittest.TestCase):
    """Generating >256 sessions must not clear all tokens; must evict oldest only."""

    def test_overflow_retains_recent_evicts_oldest(self):
        from config import _lab_sessions, _lab_lock, _LAB_SESSION_MAX
        from developer import lab_session

        # Save original state
        with _lab_lock:
            orig = dict(_lab_sessions)
            _lab_sessions.clear()

        try:
            tokens = []
            for _ in range(_LAB_SESSION_MAX + 10):
                res = lab_session()
                tokens.append(res["token"])

            from developer import lab_check
            # The most recent token should still be valid
            self.assertTrue(lab_check(tokens[-1]))
            # The oldest tokens should be evicted
            self.assertFalse(lab_check(tokens[0]))
            # Session count should not exceed max
            with _lab_lock:
                self.assertLessEqual(len(_lab_sessions), _LAB_SESSION_MAX)
        finally:
            with _lab_lock:
                _lab_sessions.clear()
                _lab_sessions.update(orig)


class TestHostileRefererLabSession(unittest.TestCase):
    """lab/session must reject hostile Referer when Origin is absent."""

    def _get_route(self, path, headers=None):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "GET"
        handler.url_path = path
        handler.query = {}
        handler.headers = headers or {}
        handler.handle_chat_routes = lambda _engine: False
        handler.read_json_body = lambda: {}
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        return captured

    def test_hostile_referer_no_origin_rejected_session(self):
        """GET /api/lab/session must reject hostile Referer when Origin absent."""
        captured = self._get_route("/api/lab/session", headers={
            "Referer": "https://evil.example.com/page"
        })
        self.assertEqual(captured.get("code"), 403)

    def test_no_origin_no_referer_allowed_session(self):
        """GET /api/lab/session must allow absent Origin + absent Referer."""
        captured = self._get_route("/api/lab/session", headers={})
        self.assertNotEqual(captured.get("code"), 403)


class TestHostileRefererLabMutating(unittest.TestCase):
    """Lab mutating routes must reject hostile Referer."""

    def _post_route(self, path, payload, headers=None):
        import server
        captured = {}
        handler = object.__new__(server.Handler)
        handler.command = "POST"
        handler.url_path = path
        handler.query = {}
        handler.headers = headers or {}
        handler.handle_chat_routes = lambda _engine: False
        handler.read_json_body = lambda: payload
        handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
        handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
        handler.route()
        return captured

    def test_hostile_referer_on_lab_mutating_route(self):
        """Lab mutating route must reject hostile Referer even with valid token."""
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/add_model",
            {"model_name": "x"},
            headers={
                "X-Lab-Token": tok,
                "Referer": "https://evil.example.com/page",
            }
        )
        self.assertEqual(captured.get("code"), 403)

    def test_local_referer_no_origin_allowed(self):
        """Lab mutating route must allow local Referer when Origin absent."""
        from developer import lab_session
        tok = lab_session()["token"]
        captured = self._post_route(
            "/api/dev/add_model",
            {"model_name": "x"},
            headers={
                "X-Lab-Token": tok,
                "Referer": "http://localhost:8080/index.html",
            }
        )
        # Should not be 403 for referer reasons
        self.assertNotEqual(captured.get("code"), 403)




if __name__ == "__main__":
    unittest.main()

"""SDK Document API safety contracts.

Tests the /api/sdk-doc endpoint for path validation, traversal prevention,
and allowlist enforcement.
"""
from __future__ import annotations

import importlib.util
import json
import re
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
STATIC = ROOT / "launcher" / "static"


def _load_launcher_module():
    spec = importlib.util.spec_from_file_location(
        "dx_launcher_under_test",
        ROOT / "launcher" / "launcher.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_launcher_handler():
    return _load_launcher_module().LauncherHandler


@pytest.fixture(scope="module")
def launcher_server():
    LauncherHandler = _load_launcher_handler()
    server = ThreadingHTTPServer(("127.0.0.1", 0), LauncherHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _find_existing_md_path() -> str:
    """Find a registered markdown path that actually exists on disk."""
    data = json.loads((STATIC / "sdk-library-data.json").read_text(encoding="utf-8"))
    suite_root = ROOT.parent  # dx-all-suite level
    for drawer in data.get("drawers", []):
        for section in drawer.get("sections", []):
            for file_info in section.get("files", []):
                path = file_info.get("path", "")
                if path.endswith(".md"):
                    if (suite_root / path).is_file():
                        return path
    return ""


def _find_registered_pdf_path() -> str:
    data = json.loads((STATIC / "sdk-library-data.json").read_text(encoding="utf-8"))
    for drawer in data.get("drawers", []):
        for section in drawer.get("sections", []):
            for file_info in section.get("files", []):
                path = file_info.get("path", "")
                if path.endswith(".pdf"):
                    return path
    return ""


@pytest.fixture()
def existing_md_path():
    """Find a registered markdown path at test time, not import time."""
    path = _find_existing_md_path()
    if not path:
        pytest.skip("No existing md file found in sdk-library-data.json")
    return path


@pytest.fixture()
def registered_pdf_path():
    path = _find_registered_pdf_path()
    if not path:
        pytest.skip("No registered PDF file found in sdk-library-data.json")
    return path


class TestSdkDocApiSafety:
    """SDK document API must validate paths and enforce the allowlist."""

    def _get(self, base_url: str, path_param: str) -> int:
        url = f"{base_url}/api/sdk-doc?{urlencode({'path': path_param})}"
        try:
            resp = urlopen(url, timeout=5)
            return resp.status
        except HTTPError as e:
            return e.code

    def _get_no_param(self, base_url: str) -> int:
        url = f"{base_url}/api/sdk-doc"
        try:
            resp = urlopen(url, timeout=5)
            return resp.status
        except HTTPError as e:
            return e.code

    def test_registered_md_returns_200(self, launcher_server, existing_md_path):
        """Registered document path returns 200 with text/plain."""
        url = f"{launcher_server}/api/sdk-doc?{urlencode({'path': existing_md_path})}"
        resp = urlopen(url, timeout=5)
        assert resp.status == 200
        ct = resp.headers.get("Content-Type", "")
        assert "text/plain" in ct

    def test_unknown_path_returns_404(self, launcher_server):
        assert self._get(launcher_server, "nonexistent/fake-doc.md") == 404

    def test_empty_path_returns_400(self, launcher_server):
        assert self._get(launcher_server, "") == 400

    def test_no_path_param_returns_400(self, launcher_server):
        assert self._get_no_param(launcher_server) == 400

    def test_absolute_path_returns_400(self, launcher_server):
        assert self._get(launcher_server, "/etc/passwd") == 400

    def test_dotdot_traversal_returns_400(self, launcher_server):
        assert self._get(launcher_server, "../../etc/passwd") == 400

    def test_encoded_traversal_returns_400(self, launcher_server):
        """URL-encoded ../ must also be rejected."""
        # Send raw percent-encoded path without double-encoding
        url = f"{launcher_server}/api/sdk-doc?path=%2e%2e%2fPROJECT_CONTEXT.md"
        try:
            resp = urlopen(url, timeout=5)
            status = resp.status
        except HTTPError as e:
            status = e.code
        assert status == 400

    def test_path_not_in_allowlist_returns_404(self, launcher_server):
        """Even if file exists, must be in sdk-library-data.json allowlist."""
        assert self._get(launcher_server, "launcher/launcher.py") == 404



def test_sdk_doc_allowlist_loader_is_cached():
    module = _load_launcher_module()
    first = module.LauncherHandler._load_sdk_doc_paths()
    second = module.LauncherHandler._load_sdk_doc_paths()
    assert first is second
    assert first


class TestSdkPdfStatusApi:
    """PDF status API must prevent raw iframe 404s without weakening path safety."""

    def _get_status(self, base_url: str, path_param: str) -> tuple[int, dict]:
        url = f"{base_url}/api/sdk-pdf-status?{urlencode({'path': path_param})}"
        resp = urlopen(url, timeout=5)
        return resp.status, json.loads(resp.read().decode("utf-8"))

    def _get_error(self, base_url: str, path_param: str) -> int:
        url = f"{base_url}/api/sdk-pdf-status?{urlencode({'path': path_param})}"
        try:
            resp = urlopen(url, timeout=5)
            return resp.status
        except HTTPError as e:
            return e.code

    def test_registered_pdf_reports_packaged_availability(
        self, launcher_server, registered_pdf_path
    ):
        status, data = self._get_status(launcher_server, registered_pdf_path)
        expected_available = (STATIC / registered_pdf_path).is_file()

        assert status == 200
        assert data["path"] == registered_pdf_path
        assert data["available"] is expected_available
        if expected_available:
            assert data["url"] == f"/static/{registered_pdf_path}"
        else:
            assert data["reason"] == "missing"
            assert "url" not in data

    def test_packaged_pdf_static_head_returns_200(
        self, launcher_server, registered_pdf_path
    ):
        assert (STATIC / registered_pdf_path).is_file()

        url = f"{launcher_server}/static/{quote(registered_pdf_path)}"
        request = Request(url, method="HEAD")
        resp = urlopen(request, timeout=5)

        assert resp.status == 200
        assert resp.headers.get_content_type() == "application/pdf"

    def test_unknown_pdf_returns_404(self, launcher_server):
        assert self._get_error(launcher_server, "pdfs/not-registered.pdf") == 404

    def test_registered_markdown_path_returns_404(self, launcher_server, existing_md_path):
        assert self._get_error(launcher_server, existing_md_path) == 404

    def test_empty_pdf_path_returns_400(self, launcher_server):
        assert self._get_error(launcher_server, "") == 400

    def test_absolute_pdf_path_returns_400(self, launcher_server):
        assert self._get_error(launcher_server, "/tmp/file.pdf") == 400

    def test_dotdot_pdf_traversal_returns_400(self, launcher_server):
        assert self._get_error(launcher_server, "pdfs/../secret.pdf") == 400

    def test_backslash_pdf_path_returns_400(self, launcher_server):
        assert self._get_error(launcher_server, r"pdfs\\secret.pdf") == 400


def _find_existing_doc_image() -> str:
    """Find a doc-relative image (resolved suite-root path) that exists on disk."""
    data = json.loads((STATIC / "sdk-library-data.json").read_text(encoding="utf-8"))
    suite_root = ROOT.parent
    for drawer in data.get("drawers", []):
        for section in drawer.get("sections", []):
            for file_info in section.get("files", []):
                path = file_info.get("path", "")
                if not path.endswith(".md") or not (suite_root / path).is_file():
                    continue
                text = (suite_root / path).read_text(encoding="utf-8", errors="ignore")
                doc_dir = path.rsplit("/", 1)[0] if "/" in path else ""
                for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
                    src = m.group(1).strip()
                    if re.match(r"^(https?:|data:|/)", src, re.I):
                        continue
                    parts = doc_dir.split("/") if doc_dir else []
                    for seg in src.split("/"):
                        if seg in ("", "."):
                            continue
                        if seg == "..":
                            if parts:
                                parts.pop()
                            continue
                        parts.append(seg)
                    resolved = "/".join(parts)
                    if resolved.lower().rsplit(".", 1)[-1] in (
                        "png", "jpg", "jpeg", "gif", "svg", "webp"
                    ) and (suite_root / resolved).is_file():
                        return resolved
    return ""


class TestSdkDocImageApi:
    """SDK doc image endpoint serves doc-relative images safely."""

    def _get(self, base_url: str, path_param: str) -> int:
        url = f"{base_url}/api/sdk-doc-image?{urlencode({'path': path_param})}"
        try:
            return urlopen(url, timeout=5).status
        except HTTPError as e:
            return e.code

    def test_registered_doc_image_returns_200(self, launcher_server):
        img = _find_existing_doc_image()
        if not img:
            pytest.skip("No doc-relative image found on disk")
        url = f"{launcher_server}/api/sdk-doc-image?{urlencode({'path': img})}"
        resp = urlopen(url, timeout=5)
        assert resp.status == 200
        assert resp.headers.get("Content-Type", "").startswith("image/")

    def test_non_image_extension_returns_404(self, launcher_server):
        assert self._get(launcher_server, "dx-compiler/README.md") == 404

    def test_dotdot_traversal_returns_400(self, launcher_server):
        assert self._get(launcher_server, "../secret.png") == 400

    def test_absolute_path_returns_400(self, launcher_server):
        assert self._get(launcher_server, "/tmp/x.png") == 400

    def test_missing_image_returns_404(self, launcher_server):
        assert self._get(launcher_server, "dx-compiler/does-not-exist-xyz.png") == 404

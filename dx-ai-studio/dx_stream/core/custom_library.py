"""커스텀 후처리 라이브러리 관리 — 목록/업로드/빌드.

SDK의 custom_library/postprocess_library/ 구조를 GUI에서 관리한다.
"""
from __future__ import annotations

import subprocess
import threading
from pathlib import Path
from dx_stream.core.config import DX_STREAM_SRC

POSTPROC_LIB_DIR = DX_STREAM_SRC / "custom_library" / "postprocess_library"
INSTALLED_SO_DIR = Path("/usr/local/share/gstdxstream/lib")

_build_log = ""
_build_done = True
_build_lock = threading.Lock()


class CustomLibraryManager:
    def list_libraries(self) -> list[dict]:
        """postprocess_library/ 하위 디렉토리 목록 반환."""
        if not POSTPROC_LIB_DIR.exists():
            return []
        libs = []
        for d in sorted(POSTPROC_LIB_DIR.iterdir()):
            if d.is_dir() and (d / "meson.build").exists():
                so_file = list(d.glob("builddir/*.so"))
                libs.append({
                    "name": d.name,
                    "path": str(d),
                    "has_meson": True,
                    "built": len(so_file) > 0,
                    "so_file": str(so_file[0]) if so_file else None,
                })
        return libs

    def get_available_so(self) -> list[dict]:
        """설치된 .so 파일 목록 반환."""
        if not INSTALLED_SO_DIR.exists():
            return []
        return [
            {"name": f.name, "path": str(f), "size": f.stat().st_size}
            for f in sorted(INSTALLED_SO_DIR.glob("*.so"))
        ]

    @staticmethod
    def _reject_traversal(component: str, label: str) -> None:
        """Reject path components that could escape POSTPROC_LIB_DIR/<name>/."""
        if not component or "/" in component or "\\" in component or \
                component.startswith(".") or ".." in component:
            raise ValueError(f"Invalid {label}: {component!r}")

    def save_upload(self, name: str, files: dict[str, str]) -> dict:
        """업로드된 소스 파일을 postprocess_library/<name>/에 저장.

        files: {"filename": "content"} 딕셔너리 (Base64 디코딩 후).
        """
        self._reject_traversal(name, "library name")
        target_dir = POSTPROC_LIB_DIR / name
        target_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for filename, content in files.items():
            self._reject_traversal(filename, "file name")
            filepath = target_dir / filename
            filepath.write_text(content)
            saved.append(str(filepath))
        return {"name": name, "path": str(target_dir), "files": saved}

    def build(self, name: str):
        """meson setup + compile — 백그라운드 스레드."""
        global _build_log, _build_done

        self._reject_traversal(name, "library name")
        target_dir = POSTPROC_LIB_DIR / name
        if not (target_dir / "meson.build").exists():
            raise FileNotFoundError(f"meson.build not found in {target_dir}")

        with _build_lock:
            _build_log = ""
            _build_done = False

        def _run():
            global _build_log, _build_done
            try:
                for cmd_label, cmd in [
                    ("meson setup", ["meson", "setup", "builddir", "--prefix=/usr/local", "--buildtype=release"]),
                    ("meson compile", ["meson", "compile", "-C", "builddir"]),
                    # sudo meson install — copies .so to /usr/local/share/gstdxstream/lib/
                    # Required for GStreamer to discover the postprocess library at runtime.
                    ("meson install", ["sudo", "meson", "install", "-C", "builddir"]),
                ]:
                    with _build_lock:
                        _build_log += f"\n=== {cmd_label} ===\n"
                    proc = subprocess.Popen(
                        cmd, cwd=str(target_dir),
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, bufsize=1
                    )
                    for line in proc.stdout:
                        with _build_lock:
                            _build_log += line
                    proc.wait()
                    if proc.returncode != 0:
                        with _build_lock:
                            _build_log += f"\n[ERROR] {cmd_label} failed with code {proc.returncode}\n"
                            _build_done = True
                        return

                with _build_lock:
                    _build_log += "\n✅ Build successful\n"
                    _build_done = True
            except Exception as e:
                with _build_lock:
                    _build_log += f"\n[ERROR] {e}\n"
                    _build_done = True

        threading.Thread(target=_run, daemon=True).start()

    @staticmethod
    def get_build_log() -> dict:
        with _build_lock:
            return {"log": _build_log, "done": _build_done}

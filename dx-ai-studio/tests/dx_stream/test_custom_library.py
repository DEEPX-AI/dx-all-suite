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


# --- Behavioural contracts (the smoke tests above only check shapes) ---------

import pytest  # noqa: E402


@pytest.fixture()
def lib_dirs(tmp_path, monkeypatch):
    """Redirect both roots into tmp_path so nothing touches the real SDK tree."""
    from core import custom_library as CL

    src = tmp_path / "postprocess_library"
    inst = tmp_path / "installed"
    src.mkdir()
    inst.mkdir()
    monkeypatch.setattr(CL, "POSTPROC_LIB_DIR", src)
    monkeypatch.setattr(CL, "INSTALLED_SO_DIR", inst)
    return CL, src, inst


class TestTraversalGuard:
    """save_upload writes attacker-supplied names straight onto disk, so the guard
    is the only thing keeping a write inside POSTPROC_LIB_DIR/<name>/."""

    @pytest.mark.parametrize("bad", [
        "../escape", "a/b", "a\\b", ".hidden", "..", "", "x/../../etc",
    ])
    def test_library_name_is_rejected(self, lib_dirs, bad):
        CL, src, _ = lib_dirs
        with pytest.raises(ValueError, match="Invalid library name"):
            CL.CustomLibraryManager().save_upload(bad, {"a.c": "x"})
        assert list(src.iterdir()) == [], "a rejected name must not create a directory"

    @pytest.mark.parametrize("bad", ["../out.c", "sub/dir.c", "..", ".rc"])
    def test_file_name_is_rejected(self, lib_dirs, bad):
        CL, src, _ = lib_dirs
        with pytest.raises(ValueError, match="Invalid file name"):
            CL.CustomLibraryManager().save_upload("mylib", {bad: "x"})

    def test_escape_attempt_writes_nothing_outside_the_target(self, lib_dirs, tmp_path):
        CL, src, _ = lib_dirs
        before = sorted(p.name for p in tmp_path.iterdir())
        with pytest.raises(ValueError):
            CL.CustomLibraryManager().save_upload("ok", {"../../pwned.c": "x"})
        assert sorted(p.name for p in tmp_path.iterdir()) == before
        assert not (tmp_path / "pwned.c").exists()


class TestSaveUpload:
    def test_writes_files_and_reports_their_paths(self, lib_dirs):
        CL, src, _ = lib_dirs
        got = CL.CustomLibraryManager().save_upload(
            "mylib", {"postprocess.cpp": "int main(){}", "meson.build": "project()"})
        assert got["name"] == "mylib"
        assert (src / "mylib" / "postprocess.cpp").read_text() == "int main(){}"
        assert sorted(Path(p).name for p in got["files"]) == ["meson.build", "postprocess.cpp"]

    def test_re_upload_overwrites_in_place(self, lib_dirs):
        CL, src, _ = lib_dirs
        mgr = CL.CustomLibraryManager()
        mgr.save_upload("mylib", {"a.c": "v1"})
        mgr.save_upload("mylib", {"a.c": "v2"})
        assert (src / "mylib" / "a.c").read_text() == "v2"


class TestInstalledMatching:
    """The SDK ships stock libraries pre-installed and never leaves a source
    builddir, so matching a source dir to an installed .so is what stops every
    stock library from reporting "Not built"."""

    def _mk(self, src, name, with_builddir_so=False):
        d = src / name
        d.mkdir()
        (d / "meson.build").write_text("project()")
        if with_builddir_so:
            (d / "builddir").mkdir()
            (d / "builddir" / f"libpostprocess_{name}.so").write_bytes(b"\x7fELF")

    def test_installed_so_marks_a_source_dir_as_built(self, lib_dirs):
        CL, src, inst = lib_dirs
        self._mk(src, "yolo26_depth")
        (inst / "libpostprocess_yolo26depth.so").write_bytes(b"\x7fELF")
        lib = CL.CustomLibraryManager().list_libraries()[0]
        assert lib["built"] is True and lib["installed"] is True

    def test_builddir_so_counts_as_built_even_without_install(self, lib_dirs):
        CL, src, _ = lib_dirs
        self._mk(src, "mylib", with_builddir_so=True)
        lib = CL.CustomLibraryManager().list_libraries()[0]
        assert lib["built"] is True
        assert lib["installed"] is False, "a local build is not an install"

    def test_unbuilt_library_reports_not_built(self, lib_dirs):
        CL, src, _ = lib_dirs
        self._mk(src, "brandnew")
        lib = CL.CustomLibraryManager().list_libraries()[0]
        assert lib["built"] is False and lib["so_file"] is None

    def test_directory_without_meson_build_is_not_a_library(self, lib_dirs):
        CL, src, _ = lib_dirs
        (src / "notalib").mkdir()
        assert CL.CustomLibraryManager().list_libraries() == []

    def test_normalisation_ignores_case_and_punctuation(self, lib_dirs):
        CL, _, _ = lib_dirs
        norm = CL.CustomLibraryManager._norm
        assert norm("Object_Classification") == "objectclassification"
        assert norm("YoloV5S-6") == "yolov5s6"
        assert norm("") == ""

    def test_empty_name_never_matches(self, lib_dirs):
        """_norm("") is falsy and must bail out — otherwise the `in` test below
        would make an empty name match the first installed .so."""
        CL, _, _ = lib_dirs
        mgr = CL.CustomLibraryManager()
        assert mgr._installed_match("", {"anything": "/x.so"}) is None
        assert mgr._installed_match("!!!", {"anything": "/x.so"}) is None

    def test_matching_is_substring_based_in_both_directions(self, lib_dirs):
        """Documented behaviour: object_class matches objectclassification and
        vice versa. It is deliberately loose, which also means a very short
        library name can match an unrelated .so — pinned here so a future
        tightening is a conscious change, not an accident."""
        CL, _, _ = lib_dirs
        mgr = CL.CustomLibraryManager()
        installed = {"objectclassification": "/a.so", "yolov5s6": "/b.so"}
        assert mgr._installed_match("object_class", installed) == "/a.so"
        assert mgr._installed_match("YoloV5S", installed) == "/b.so"
        assert mgr._installed_match("totally_unrelated", installed) is None


class TestBuild:
    def test_build_rejects_traversal_before_touching_disk(self, lib_dirs):
        CL, _, _ = lib_dirs
        with pytest.raises(ValueError, match="Invalid library name"):
            CL.CustomLibraryManager().build("../evil")

    def test_build_requires_meson_build(self, lib_dirs):
        CL, src, _ = lib_dirs
        (src / "nomeson").mkdir()
        with pytest.raises(FileNotFoundError, match="has no meson.build"):   # no server path in the message
            CL.CustomLibraryManager().build("nomeson")

    def test_get_build_log_shape(self, lib_dirs):
        CL, _, _ = lib_dirs
        log = CL.CustomLibraryManager.get_build_log()
        assert set(log) == {"log", "done"}
        assert isinstance(log["log"], str) and isinstance(log["done"], bool)


class TestAvailableSo:
    def test_lists_installed_so_with_size(self, lib_dirs):
        CL, _, inst = lib_dirs
        (inst / "libpostprocess_a.so").write_bytes(b"1234")
        (inst / "notashared.txt").write_text("ignore me")
        got = CL.CustomLibraryManager().get_available_so()
        assert [g["name"] for g in got] == ["libpostprocess_a.so"]
        assert got[0]["size"] == 4

    def test_missing_install_dir_returns_empty(self, lib_dirs, tmp_path, monkeypatch):
        CL, _, _ = lib_dirs
        monkeypatch.setattr(CL, "INSTALLED_SO_DIR", tmp_path / "gone")
        assert CL.CustomLibraryManager().get_available_so() == []


class _FakeProc:
    """Stand-in for subprocess.Popen: yields canned stdout lines, then a returncode."""

    def __init__(self, lines, returncode=0):
        self.stdout = iter(lines)
        self._returncode = returncode
        self.returncode = None

    def wait(self):
        self.returncode = self._returncode
        return self.returncode


def _wait_for_build(CL, timeout=5.0):
    """Block until the build thread flips done, or fail loudly."""
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        log = CL.CustomLibraryManager.get_build_log()
        if log["done"]:
            return log
        time.sleep(0.01)
    raise AssertionError("build thread never finished")


class TestBuildExecution:
    """build() runs meson in a daemon thread and the GUI polls get_build_log().
    If the log or the failure branch regresses, a broken build looks like a
    successful one in the UI — these pin both outcomes. Popen is always faked:
    the real command list ends in `sudo meson install`.
    """

    @pytest.fixture(autouse=True)
    def _no_real_sudo(self, monkeypatch):
        """The sudo check runs `sudo -n true` for real — answer it here (passwordless host)."""
        import os
        from core import custom_library as CL
        monkeypatch.setattr(CL, "_sudo_env", lambda password=None: (dict(os.environ), lambda: None))

    @pytest.fixture()
    def ready_lib(self, lib_dirs):
        CL, src, _ = lib_dirs
        d = src / "mylib"
        d.mkdir()
        (d / "meson.build").write_text("project()")
        return CL, d

    def test_successful_build_runs_setup_compile_install_in_order(self, ready_lib, monkeypatch):
        CL, d = ready_lib
        calls = []

        def _popen(cmd, **kwargs):
            calls.append((cmd, kwargs.get("cwd")))
            return _FakeProc([f"line for {cmd[1]}\n"])

        monkeypatch.setattr(CL.subprocess, "Popen", _popen)
        CL.CustomLibraryManager().build("mylib")
        log = _wait_for_build(CL)

        assert [c[0][:2] for c in calls] == [
            ["meson", "setup"], ["meson", "compile"], ["sudo", "meson"],
        ]
        assert all(cwd == str(d) for _, cwd in calls), "meson must run inside the library dir"
        assert "✅ Build successful" in log["log"]
        for label in ("meson setup", "meson compile", "meson install"):
            assert f"=== {label} ===" in log["log"]

    def test_failure_stops_the_chain_and_reports_the_exit_code(self, ready_lib, monkeypatch):
        CL, _ = ready_lib
        calls = []

        def _popen(cmd, **kwargs):
            calls.append(cmd)
            return _FakeProc(["configuring...\n"], returncode=2)

        monkeypatch.setattr(CL.subprocess, "Popen", _popen)
        CL.CustomLibraryManager().build("mylib")
        log = _wait_for_build(CL)

        assert len(calls) == 1, "a failed meson setup must not proceed to compile/install"
        assert "[ERROR] meson setup failed with code 2" in log["log"]
        assert "✅ Build successful" not in log["log"]

    def test_child_stdout_is_streamed_into_the_log(self, ready_lib, monkeypatch):
        CL, _ = ready_lib
        monkeypatch.setattr(
            CL.subprocess, "Popen",
            lambda cmd, **k: _FakeProc(["compiling foo.cpp\n", "linking\n"]),
        )
        CL.CustomLibraryManager().build("mylib")
        log = _wait_for_build(CL)
        assert "compiling foo.cpp" in log["log"] and "linking" in log["log"]

    def test_popen_raising_is_captured_not_lost(self, ready_lib, monkeypatch):
        """meson missing from PATH must surface in the log, not vanish in a
        daemon thread where nobody sees the traceback."""
        CL, _ = ready_lib

        def _boom(*a, **k):
            raise FileNotFoundError("meson: command not found")

        monkeypatch.setattr(CL.subprocess, "Popen", _boom)
        CL.CustomLibraryManager().build("mylib")
        log = _wait_for_build(CL)
        assert "[ERROR]" in log["log"] and "meson: command not found" in log["log"]

    def test_build_resets_the_log_from_the_previous_run(self, ready_lib, monkeypatch):
        CL, _ = ready_lib
        monkeypatch.setattr(CL.subprocess, "Popen", lambda cmd, **k: _FakeProc(["first\n"]))
        CL.CustomLibraryManager().build("mylib")
        _wait_for_build(CL)
        monkeypatch.setattr(CL.subprocess, "Popen", lambda cmd, **k: _FakeProc(["second\n"]))
        CL.CustomLibraryManager().build("mylib")
        log = _wait_for_build(CL)
        assert "second" in log["log"]
        assert "first" not in log["log"], "a new build must not append to the old log"


class TestBuildNeedsSudoForInstall:
    """`sudo meson install` ran with no TTY and no askpass: on any host that asks for a password
    the build died at the install step ("a terminal is required"). The password now comes from the
    page, as Stream Setup does it, and the build refuses up front when it is needed but missing."""

    @pytest.fixture()
    def ready_lib(self, lib_dirs):
        CL, src, _ = lib_dirs
        d = src / "mylib"
        d.mkdir()
        (d / "meson.build").write_text("project()")
        return CL

    def test_a_password_is_asked_for_before_anything_runs(self, ready_lib, monkeypatch):
        CL = ready_lib
        import shared.sudo_askpass as SA
        monkeypatch.setattr(SA, "preauthorize_sudo", lambda password=None, env=None: "a password is required")
        monkeypatch.setattr(CL.subprocess, "Popen", lambda *a, **k: (_ for _ in ()).throw(AssertionError("ran")))
        with pytest.raises(CL.SudoRequired):
            CL.CustomLibraryManager().build("mylib")

    def test_a_wrong_password_is_refused_and_cleaned_up(self, ready_lib, monkeypatch):
        CL = ready_lib
        import shared.sudo_askpass as SA
        cleaned = []
        monkeypatch.setattr(SA, "preauthorize_sudo",
                            lambda password=None, env=None: "Sorry, try again" if password else "required")
        monkeypatch.setattr(SA, "configure_sudo_env", lambda env, password=None: lambda: cleaned.append(1))
        with pytest.raises(CL.SudoAuthFailed):
            CL.CustomLibraryManager().build("mylib", sudo_password="wrong")
        assert cleaned == [1]

    def test_the_install_step_gets_the_askpass_environment(self, ready_lib, monkeypatch):
        CL = ready_lib
        import shared.sudo_askpass as SA
        seen, cleaned = [], []
        monkeypatch.setattr(SA, "preauthorize_sudo",
                            lambda password=None, env=None: None if password else "required")

        def _configure(env, password=None):
            env["SUDO_ASKPASS"] = "/tmp/askpass"
            return lambda: cleaned.append(1)

        monkeypatch.setattr(SA, "configure_sudo_env", _configure)
        monkeypatch.setattr(CL.subprocess, "Popen",
                            lambda cmd, **k: seen.append(k.get("env", {}).get("SUDO_ASKPASS")) or _FakeProc(["ok\n"]))
        CL.CustomLibraryManager().build("mylib", sudo_password="pw")
        _wait_for_build(CL)
        assert seen == ["/tmp/askpass"] * 3
        assert cleaned == [1], "the askpass shim must be removed when the build ends"


def test_the_build_route_answers_401_and_404_with_a_reason(lib_dirs, monkeypatch):
    import json
    import urllib.error
    import urllib.request
    from tests.server_helpers import start_module_server
    import shared.sudo_askpass as SA

    CL, src, _ = lib_dirs
    (src / "mylib").mkdir()
    (src / "mylib" / "meson.build").write_text("project()")
    monkeypatch.setattr(SA, "preauthorize_sudo", lambda password=None, env=None: "a password is required")
    srv, port = start_module_server("dx_stream")
    try:
        def post(path, body=None):
            req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method="POST",
                                         data=json.dumps(body or {}).encode(),
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read())

        code, body = post("/api/custom-library/mylib/build")
        assert (code, body["error"]) == (401, "need_sudo")
        code, body = post("/api/custom-library/nolib/build")
        assert code == 404 and "meson.build" in body["message"]
    finally:
        srv.shutdown()

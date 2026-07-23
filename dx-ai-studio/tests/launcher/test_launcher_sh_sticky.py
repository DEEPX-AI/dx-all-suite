"""launcher.sh: module-port claim loop removed (sub-servers self-assign via :0);
launcher's own port is sticky (.launcher-port)."""
from pathlib import Path

SH = (Path(__file__).resolve().parents[2] / "launcher.sh").read_text(encoding="utf-8")


def test_no_module_port_claim_loop():
    # the per-module DX_*_PORT export loop is obsolete (ephemeral :0) and must be gone
    assert "DX_STREAM_PORT:8093" not in SH
    assert "DX_ZOO_PORT:8094" not in SH
    assert "DX_AGENT_PORT:8099" not in SH


def test_default_launcher_port_is_8890():
    assert "PORT=8890" in SH
    assert "LAUNCHER_PORT = _port(\"DX_LAUNCHER_PORT\", 8890)" in (
        Path(__file__).resolve().parents[2] / "launcher" / "launcher.py"
    ).read_text(encoding="utf-8")


def test_legacy_sticky_8888_is_ignored():
    assert 'STICKY_PORT" == "8888"' in SH
    # remembers/reuses the launcher port across runs
    assert ".launcher-port" in SH


def test_keeps_loud_url_banner():
    # the persisted URL (.launcher-url) stays discoverable
    assert ".launcher-url" in SH


def test_sh_does_not_print_clickable_url_before_python():
    # VS Code-remote auto-links terminal URLs and forwards the instant the link appears.
    # launcher.sh must NOT emit a clickable http://localhost URL before python binds the
    # port (that forwards to a dead port → cached-broken tunnel → "won't open"). The live
    # banner is launcher.py's job now — printed right after bind.
    for line in SH.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if ("echo" in s or "printf" in s) and "http://localhost" in s:
            raise AssertionError(f"launcher.sh prints a clickable URL before bind: {line!r}")


def test_launcher_py_binds_before_boot_and_prints_banner():
    PY = (Path(__file__).resolve().parents[2] / "launcher" / "launcher.py").read_text(encoding="utf-8")
    # Bind host is now resolved (DX_BIND_LOCAL/DX_BIND_HOST → _bind_host, default 0.0.0.0)
    # rather than a hardcoded "0.0.0.0"; anchor on the constructor call itself.
    bind_idx = PY.index('_LauncherServer((_bind_host')
    boot_idx = PY.index("show_boot_progress(")  # the call, not the import line
    start_idx = PY.index("start_sub_server(_name")
    ready_idx = PY.index("_STUDIO_READY = True")
    assert bind_idx < boot_idx, "launcher must bind the port before the boot progress"
    assert bind_idx < start_idx, "launcher must bind the port before starting sub-servers"
    assert boot_idx < ready_idx, "studio_ready must flip only after boot progress"
    assert "OPEN THE STUDIO" in PY, "launcher.py must print the live URL banner"
    assert "serve_forever" in PY and "daemon=True" in PY, "serve must run in a daemon thread"

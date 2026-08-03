"""Regression tests for unified dxstream plugin discovery."""
from __future__ import annotations

import os


def test_finds_plugin_from_environment_and_prepends_it(monkeypatch, tmp_path):
    from dx_stream.core import gst_env

    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin = plugin_dir / gst_env.PLUGIN_SO
    plugin.write_bytes(b"plugin")
    monkeypatch.setattr(gst_env, "_KNOWN_DIRS", ())
    monkeypatch.setattr(gst_env, "_SEARCH_ROOTS", ())
    monkeypatch.setenv("GST_PLUGIN_PATH", str(plugin_dir))

    assert gst_env.find_dxstream_plugin() == plugin
    assert gst_env.plugin_dir() == str(plugin.parent)
    assert gst_env.augmented_env({"GST_PLUGIN_PATH": "/other"})[
        "GST_PLUGIN_PATH"
    ].split(os.pathsep)[0] == str(plugin.parent)


def test_explicit_plugin_path_takes_precedence_over_known_locations(
    monkeypatch, tmp_path
):
    from dx_stream.core import gst_env

    known_dir = tmp_path / "known"
    custom_dir = tmp_path / "custom"
    known_dir.mkdir()
    custom_dir.mkdir()
    (known_dir / gst_env.PLUGIN_SO).write_bytes(b"known")
    custom_plugin = custom_dir / gst_env.PLUGIN_SO
    custom_plugin.write_bytes(b"custom")

    monkeypatch.setattr(gst_env, "_KNOWN_DIRS", (str(known_dir),))
    monkeypatch.setattr(gst_env, "_SEARCH_ROOTS", ())
    monkeypatch.setenv("GST_PLUGIN_PATH", str(custom_dir))

    assert gst_env.find_dxstream_plugin() == custom_plugin
    assert gst_env.plugin_dir() == str(custom_dir)


def test_canonical_plugin_lookup_ignores_inherited_override(monkeypatch, tmp_path):
    from dx_stream.core import gst_env

    inherited_dir = tmp_path / "inherited"
    installed_dir = tmp_path / "installed"
    inherited_dir.mkdir()
    installed_dir.mkdir()
    inherited = inherited_dir / gst_env.PLUGIN_SO
    canonical = installed_dir / gst_env.PLUGIN_SO
    inherited.write_bytes(b"inherited")
    canonical.write_bytes(b"canonical")
    monkeypatch.setattr(gst_env, "_KNOWN_DIRS", (str(installed_dir),))
    monkeypatch.setattr(gst_env, "_SEARCH_ROOTS", ())
    monkeypatch.setenv("GST_PLUGIN_PATH", str(inherited_dir))

    try:
        resolved = gst_env.find_dxstream_plugin(prefer_environment=False)
    except TypeError:
        resolved = None

    assert resolved == canonical
    assert gst_env.augmented_env(prefer_environment=False)["GST_PLUGIN_PATH"] == str(
        installed_dir
    )


def test_unchanged_environment_when_no_plugin_exists(monkeypatch):
    from dx_stream.core import gst_env

    monkeypatch.setattr(gst_env, "_KNOWN_DIRS", ())
    monkeypatch.setattr(gst_env, "_SEARCH_ROOTS", ())
    monkeypatch.delenv("GST_PLUGIN_PATH", raising=False)
    base = {"GST_PLUGIN_PATH": "/other", "KEEP": "value"}

    assert gst_env.find_dxstream_plugin() is None
    assert gst_env.plugin_dir() is None
    assert gst_env.plugin_available() is False
    assert gst_env.augmented_env(base) == base


def test_refresh_plugin_environment_scans_initialized_gst_registry(monkeypatch, tmp_path):
    from dx_stream.core import gst_env

    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / gst_env.PLUGIN_SO).write_bytes(b"plugin")
    monkeypatch.setattr(gst_env, "_KNOWN_DIRS", ())
    monkeypatch.setattr(gst_env, "_SEARCH_ROOTS", ())
    monkeypatch.setenv("GST_PLUGIN_PATH", str(plugin_dir))

    scanned = []

    class FakeRegistry:
        @staticmethod
        def get():
            return FakeRegistry

        @staticmethod
        def scan_path(path):
            scanned.append(path)
            return True

    class FakeGst:
        Registry = FakeRegistry

    refresh = getattr(gst_env, "refresh_plugin_environment", None)
    assert callable(refresh)
    assert refresh(FakeGst) == str(plugin_dir)
    assert os.environ["GST_PLUGIN_PATH"].split(os.pathsep)[0] == str(plugin_dir)
    assert scanned == [str(plugin_dir)]


def test_refresh_plugin_environment_accepts_pre_registered_dxinfer(monkeypatch, tmp_path, caplog):
    from dx_stream.core import gst_env

    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / gst_env.PLUGIN_SO).write_bytes(b"plugin")
    monkeypatch.setattr(gst_env, "_KNOWN_DIRS", ())
    monkeypatch.setattr(gst_env, "_SEARCH_ROOTS", ())
    monkeypatch.setenv("GST_PLUGIN_PATH", str(plugin_dir))

    class FakeRegistry:
        @staticmethod
        def get():
            return FakeRegistry

        @staticmethod
        def scan_path(_path):
            return False

    class FakeElementFactory:
        @staticmethod
        def find(name):
            return object() if name == "dxinfer" else None

    class FakeGst:
        Registry = FakeRegistry
        ElementFactory = FakeElementFactory

    with caplog.at_level("WARNING"):
        assert gst_env.refresh_plugin_environment(FakeGst) == str(plugin_dir)

    assert not any("found no plugin" in message for message in caplog.messages)

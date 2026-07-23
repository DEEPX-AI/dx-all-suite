"""Watchdog recovery tests for STAB-1.

Tests that the launcher watchdog:
- marks a missing module dead on first failed health check
- attempts restart within configured deadline
- returns module unavailable state after repeated failures
- respects configurable poll/deadline thresholds
"""
import os
import sys
import time
import json
import threading
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root is importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


class TestWatchdogState(unittest.TestCase):
    """Test watchdog tracking and failure detection."""

    def setUp(self):
        # Use lower thresholds for testing
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.2"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop
        _watchdog_stop()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_marks_dead_on_first_failed_health_check(self):
        """Watchdog marks a module dead when its health check first fails."""
        from launcher.launcher import (
            _watchdog_registry, _watchdog_check_once, _register_module,
        )
        # Register a fake module with a port that is definitely not open
        _register_module("test_mod", port=59991, cwd="/fake", proc=MagicMock(
            poll=MagicMock(return_value=1),  # process exited
            pid=99999,
        ))
        _watchdog_check_once()
        entry = _watchdog_registry["test_mod"]
        self.assertEqual(entry["status"], "dead")

    def test_restart_attempted_within_deadline(self):
        """Restart is attempted within the configured deadline from detection."""
        from launcher.launcher import (
            _watchdog_registry, _watchdog_check_once, _register_module,
            _WATCHDOG_RESTART_DEADLINE_SECONDS,
        )
        mock_proc = MagicMock(
            poll=MagicMock(return_value=1),
            pid=99998,
        )
        _register_module("test_restart", port=59992, cwd="/fake", proc=mock_proc)
        t0 = time.monotonic()
        _watchdog_check_once()
        entry = _watchdog_registry["test_restart"]
        self.assertEqual(entry["status"], "dead")
        # restart_at must be set within the deadline window
        deadline = _WATCHDOG_RESTART_DEADLINE_SECONDS()
        self.assertIsNotNone(entry.get("restart_at"))
        self.assertLessEqual(entry["restart_at"] - t0, deadline + 1)

    def test_unavailable_after_repeated_failures(self):
        """After max restart attempts, module is marked unavailable."""
        from launcher.launcher import (
            _watchdog_registry, _watchdog_check_once, _register_module,
            WATCHDOG_MAX_RESTARTS,
        )
        mock_proc = MagicMock(
            poll=MagicMock(return_value=1),
            pid=99997,
        )
        _register_module("test_fail", port=59993, cwd="/fake", proc=mock_proc)
        # Simulate repeated restart failures
        entry = _watchdog_registry["test_fail"]
        entry["restart_count"] = WATCHDOG_MAX_RESTARTS
        entry["restart_window_start"] = time.monotonic()
        _watchdog_check_once()
        self.assertEqual(entry["status"], "unavailable")

    def test_override_poll_deadline_thresholds(self):
        """Environment variables override default poll/deadline thresholds."""
        from launcher.launcher import (
            _WATCHDOG_POLL_SECONDS, _WATCHDOG_RESTART_DEADLINE_SECONDS,
        )
        self.assertAlmostEqual(_WATCHDOG_POLL_SECONDS(), 0.2, places=1)
        self.assertAlmostEqual(_WATCHDOG_RESTART_DEADLINE_SECONDS(), 1.0, places=1)


class TestRestartEndpoint(unittest.TestCase):
    """Test POST /api/modules/<module_key>/restart endpoint."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.2"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop
        _watchdog_stop()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_restart_valid_module(self):
        """POST /api/modules/<key>/restart triggers restart for a known module."""
        from launcher.launcher import (
            _register_module, _watchdog_registry,
            _handle_module_restart, _LAUNCHER_PROXY_PORTS,
        )
        # Register a fake module that's in _LAUNCHER_PROXY_PORTS
        key = "dx_app"
        port = _LAUNCHER_PROXY_PORTS[key]
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=99996)
        _register_module(key, port=port, cwd="/fake", proc=mock_proc)

        # Simulate restart handler logic (unit test, no HTTP)
        entry = _watchdog_registry[key]
        entry["status"] = "unavailable"
        result = _handle_module_restart(key)
        self.assertTrue(result["ok"])
        self.assertEqual(result["module"], key)

    def test_restart_unknown_module_rejected(self):
        """Restart of unknown module key returns error."""
        from launcher.launcher import _handle_module_restart
        result = _handle_module_restart("totally_fake_module")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_restart_only_known_release_modules(self):
        """Only modules in _LAUNCHER_PROXY_PORTS are restartable."""
        from launcher.launcher import _handle_module_restart, _LAUNCHER_PROXY_PORTS
        for key in _LAUNCHER_PROXY_PORTS:
            # All known modules should not error with "unknown module"
            result = _handle_module_restart(key)
            # It may fail for other reasons (no proc registered), but NOT "unknown module"
            if not result["ok"]:
                self.assertNotIn("unknown module", result.get("error", "").lower())


class TestModuleStatusAPI(unittest.TestCase):
    """Test that watchdog status is exposed in health API."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.2"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop
        _watchdog_stop()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_watchdog_status_in_module_status(self):
        """get_module_status returns watchdog state for registered modules."""
        from launcher.launcher import (
            _register_module, _watchdog_registry, get_module_watchdog_status,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=None), pid=99995)
        _register_module("dx_stream", port=59994, cwd="/fake", proc=mock_proc)
        status = get_module_watchdog_status("dx_stream")
        self.assertIn("status", status)
        self.assertEqual(status["status"], "alive")

    def test_status_includes_path(self):
        """Status response must include a 'path' field (proxy path)."""
        from launcher.launcher import (
            _register_module, get_module_watchdog_status,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=None), pid=99990)
        _register_module("dx_app", port=59994, cwd="/fake/dx_app", proc=mock_proc)
        status = get_module_watchdog_status("dx_app")
        self.assertIn("path", status)
        self.assertEqual(status["path"], "/app/")


class TestModuleKeyAliases(unittest.TestCase):
    """Test that short JS module keys (app, stream, zoo, …) map correctly
    to the internal dx_* keys used by the watchdog."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.2"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop
        _watchdog_stop()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_alias_mapping_exists(self):
        """MODULE_KEY_ALIASES must map all JS short keys to dx_* keys."""
        from launcher.launcher import MODULE_KEY_ALIASES
        expected = {
            "app": "dx_app",
            "stream": "dx_stream",
            "zoo": "dx_modelzoo",
            "compiler": "dx_compiler",
            "planner": "dx_planner",
            "benchmark": "dx_benchmark",
        }
        for short, canonical in expected.items():
            self.assertEqual(MODULE_KEY_ALIASES.get(short), canonical,
                             f"Alias '{short}' should map to '{canonical}'")

    def test_status_via_short_key(self):
        """get_module_watchdog_status resolves short key to canonical entry."""
        from launcher.launcher import (
            _register_module, get_module_watchdog_status,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=None), pid=99989)
        _register_module("dx_app", port=59991, cwd="/fake/dx_app", proc=mock_proc)
        status = get_module_watchdog_status("app")
        self.assertEqual(status["status"], "alive")
        self.assertEqual(status["module"], "dx_app")

    def test_restart_via_short_key(self):
        """_handle_module_restart accepts short JS key and restarts correctly."""
        from launcher.launcher import (
            _register_module, _handle_module_restart, _LAUNCHER_PROXY_PORTS,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=99988)
        _register_module("dx_app", port=_LAUNCHER_PROXY_PORTS["dx_app"],
                         cwd="/fake/dx_app", proc=mock_proc)
        from launcher.launcher import _watchdog_registry
        _watchdog_registry["dx_app"]["status"] = "unavailable"
        result = _handle_module_restart("app")
        self.assertTrue(result["ok"])
        self.assertEqual(result["module"], "dx_app")

    def test_dx_prefix_keys_still_work(self):
        """Existing dx_* keys must continue to work."""
        from launcher.launcher import (
            _register_module, get_module_watchdog_status, _handle_module_restart,
            _LAUNCHER_PROXY_PORTS,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=None), pid=99987)
        _register_module("dx_stream", port=_LAUNCHER_PROXY_PORTS["dx_stream"],
                         cwd="/fake/dx_stream", proc=mock_proc)
        status = get_module_watchdog_status("dx_stream")
        self.assertEqual(status["status"], "alive")
        result = _handle_module_restart("dx_stream")
        self.assertTrue(result["ok"])

    def test_status_path_via_short_key(self):
        """Status queried via short key should include correct proxy path."""
        from launcher.launcher import (
            _register_module, get_module_watchdog_status,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=None), pid=99986)
        _register_module("dx_modelzoo", port=59993, cwd="/fake/dx_modelzoo", proc=mock_proc)
        status = get_module_watchdog_status("zoo")
        self.assertIn("path", status)
        self.assertEqual(status["path"], "/zoo/")


class TestWatchdogRestartFiring(unittest.TestCase):
    """C-1 / C-2 regression: restart_at must not be reset on every poll."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.1"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "0.1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop
        _watchdog_stop()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_repeated_check_cycles_fire_restart(self):
        """C-1: Repeated _watchdog_check_once + _watchdog_do_restarts must
        eventually call _do_module_restart when the deadline elapses."""
        from launcher.launcher import (
            _register_module, _watchdog_check_once, _watchdog_do_restarts,
        )
        mock_proc = MagicMock(
            poll=MagicMock(return_value=1),  # process exited
            pid=88801,
        )
        _register_module("test_c1", port=59901, cwd="/fake", proc=mock_proc)

        with patch("launcher.launcher._do_module_restart") as mock_restart:
            # Simulate several poll cycles; deadline is 0.1 s
            for _ in range(10):
                _watchdog_check_once()
                _watchdog_do_restarts()
                time.sleep(0.05)

            self.assertGreaterEqual(mock_restart.call_count, 1,
                                    "restart must fire after deadline elapses")

    def test_check_once_skips_restarting_status(self):
        """Minor: _watchdog_check_once should skip entries with status=='restarting'."""
        from launcher.launcher import (
            _register_module, _watchdog_check_once, _watchdog_registry,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=88803)
        _register_module("test_skip", port=59903, cwd="/fake", proc=mock_proc)

        with patch("launcher.launcher._watchdog_lock", threading.Lock()):
            _watchdog_registry["test_skip"]["status"] = "restarting"
            _watchdog_check_once()
            # Status must remain 'restarting', not changed to 'dead'
            self.assertEqual(_watchdog_registry["test_skip"]["status"], "restarting")


class TestWatchdogConcurrencySafety(unittest.TestCase):
    """I-A / I-B / I-C: concurrency and atomicity fixes for watchdog."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.1"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "0.1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop
        _watchdog_stop()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_double_do_restarts_calls_restart_only_once(self):
        """I-A: Two concurrent _watchdog_do_restarts for the same due entry
        must invoke _do_module_restart exactly once (no double-restart)."""
        from launcher.launcher import (
            _register_module, _watchdog_registry,
            _watchdog_check_once, _watchdog_do_restarts, _watchdog_lock,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77001)
        _register_module("test_double", port=59801, cwd="/fake", proc=mock_proc)

        # Make the entry due for restart
        entry = _watchdog_registry["test_double"]
        with _watchdog_lock:
            entry["status"] = "dead"
            entry["restart_at"] = time.monotonic() - 1  # already past due

        with patch("launcher.launcher._do_module_restart") as mock_restart:
            # Call _watchdog_do_restarts twice in quick succession
            _watchdog_do_restarts()
            _watchdog_do_restarts()

            self.assertEqual(mock_restart.call_count, 1,
                             "_do_module_restart must be called exactly once, "
                             "not twice for the same due entry")

    def test_double_do_restarts_threaded(self):
        """I-A threaded: Two threads calling _watchdog_do_restarts simultaneously
        for the same due entry must result in exactly one _do_module_restart call."""
        from launcher.launcher import (
            _register_module, _watchdog_registry,
            _watchdog_do_restarts, _watchdog_lock,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77002)
        _register_module("test_thread", port=59802, cwd="/fake", proc=mock_proc)

        entry = _watchdog_registry["test_thread"]
        with _watchdog_lock:
            entry["status"] = "dead"
            entry["restart_at"] = time.monotonic() - 1

        barrier = threading.Barrier(2, timeout=5)
        with patch("launcher.launcher._do_module_restart") as mock_restart:
            def worker():
                barrier.wait()
                _watchdog_do_restarts()

            t1 = threading.Thread(target=worker)
            t2 = threading.Thread(target=worker)
            t1.start()
            t2.start()
            t1.join(timeout=5)
            t2.join(timeout=5)

            self.assertEqual(mock_restart.call_count, 1,
                             "Only one thread should win the restart race")

    def test_check_once_does_not_overwrite_restarting_to_dead(self):
        """I-B: _watchdog_check_once must not change a 'restarting' entry to
        'dead' or schedule a restart_at for it."""
        from launcher.launcher import (
            _register_module, _watchdog_check_once, _watchdog_registry,
            _watchdog_lock,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77003)
        _register_module("test_ib", port=59803, cwd="/fake", proc=mock_proc)

        entry = _watchdog_registry["test_ib"]
        with _watchdog_lock:
            entry["status"] = "restarting"
            entry["restart_at"] = None

        _watchdog_check_once()

        self.assertEqual(entry["status"], "restarting",
                         "restarting status must not be overwritten to dead")
        self.assertIsNone(entry["restart_at"],
                          "restart_at must not be set for a restarting entry")

    def test_check_once_concurrent_does_not_overwrite_restarting(self):
        """I-B concurrent: If _do_module_restart sets 'restarting' between
        snapshot and lock acquisition, _watchdog_check_once must not
        overwrite it back to 'dead'."""
        from launcher.launcher import (
            _register_module, _watchdog_registry, _watchdog_lock,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77004)
        _register_module("test_ib2", port=59804, cwd="/fake", proc=mock_proc)
        entry = _watchdog_registry["test_ib2"]

        # Simulate: check_once snapshots status as 'dead', then before it
        # acquires lock to write, another thread sets 'restarting'.
        # After check_once finishes, status must still be 'restarting'.
        original_check_once = None
        from launcher import launcher as L

        # We'll directly test the locked section: set status to restarting
        # right before check_once would write 'dead', verify it's preserved.
        with _watchdog_lock:
            entry["status"] = "dead"
            entry["restart_at"] = None

        # Call check_once which should detect dead and try to write
        # But we intercept: set 'restarting' during the call
        call_count = [0]
        original_is_port_open = L._is_port_open

        def fake_is_port_open(port):
            # On first call for our port, simulate concurrent restart
            if port == 59804:
                call_count[0] += 1
                if call_count[0] == 1:
                    with _watchdog_lock:
                        entry["status"] = "restarting"
            return False

        with patch.object(L, "_is_port_open", side_effect=fake_is_port_open):
            from launcher.launcher import _watchdog_check_once
            _watchdog_check_once()

        self.assertEqual(entry["status"], "restarting",
                         "check_once must re-check status inside lock and not "
                         "overwrite 'restarting' back to 'dead'")

    def test_c2_regression_direct_restart_at_preserved(self):
        """I-C: Directly test that an already-set restart_at is not pushed out
        by _watchdog_check_once. This replaces the vacuous C-2 test."""
        from launcher.launcher import (
            _register_module, _watchdog_check_once, _watchdog_registry,
            _watchdog_lock, _WATCHDOG_RESTART_DEADLINE_SECONDS,
        )
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77005)
        _register_module("test_ic", port=59805, cwd="/fake", proc=mock_proc)

        entry = _watchdog_registry["test_ic"]
        # Set restart_at to an immediate value (simulating manual restart)
        immediate_restart = time.monotonic()
        with _watchdog_lock:
            entry["status"] = "dead"
            entry["restart_at"] = immediate_restart

        # Now call check_once — it sees the module is dead but restart_at is set
        _watchdog_check_once()

        # restart_at must NOT be pushed to now + deadline
        deadline = _WATCHDOG_RESTART_DEADLINE_SECONDS()
        self.assertIsNotNone(entry["restart_at"],
                             "restart_at must not be cleared")
        self.assertLessEqual(entry["restart_at"], immediate_restart + 0.1,
                             "restart_at must not be pushed to now + deadline; "
                             "existing value must be preserved")

    def test_handle_restart_skips_when_already_restarting(self):
        """I-1: _handle_module_restart must not stomp an in-flight restart.
        If status is 'restarting', it should return ok without scheduling
        another restart_at or calling _watchdog_do_restarts."""
        from launcher.launcher import (
            _register_module, _watchdog_registry,
            _handle_module_restart, _LAUNCHER_PROXY_PORTS, _watchdog_lock,
        )
        key = "dx_app"
        port = _LAUNCHER_PROXY_PORTS[key]
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77010)
        _register_module(key, port=port, cwd="/fake", proc=mock_proc)

        entry = _watchdog_registry[key]
        with _watchdog_lock:
            entry["status"] = "restarting"
            entry["restart_at"] = None  # already claimed by watchdog

        with patch("launcher.launcher._do_module_restart") as mock_restart, \
             patch("launcher.launcher._watchdog_do_restarts") as mock_do_restarts:
            result = _handle_module_restart(key)

        # Must indicate restart already in progress
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "restarting")

        # Must NOT have scheduled a new restart_at
        self.assertIsNone(entry["restart_at"],
                          "restart_at must remain None when restart is in-flight")

        # Must NOT have called _watchdog_do_restarts (no second restart)
        mock_do_restarts.assert_not_called()

    def test_manual_restart_resets_window_start(self):
        """Minor: _handle_module_restart should reset restart_window_start
        along with decrementing restart_count to avoid re-saturation."""
        from launcher.launcher import (
            _register_module, _watchdog_registry,
            _handle_module_restart, _LAUNCHER_PROXY_PORTS, _watchdog_lock,
        )
        key = "dx_app"
        port = _LAUNCHER_PROXY_PORTS[key]
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=77006)
        _register_module(key, port=port, cwd="/fake", proc=mock_proc)

        entry = _watchdog_registry[key]
        with _watchdog_lock:
            entry["restart_count"] = 2
            entry["restart_window_start"] = time.monotonic() - 10
            entry["status"] = "unavailable"

        with patch("launcher.launcher._do_module_restart"):
            _handle_module_restart(key)

        # After manual restart, restart_window_start is fresh (not the old -10s value)
        self.assertIsNotNone(entry["restart_window_start"],
                             "restart_window_start should be set after manual restart")
        self.assertGreater(entry["restart_window_start"],
                           time.monotonic() - 1,
                           "restart_window_start should be fresh, not stale")


class TestStopAllSafety(unittest.TestCase):
    """Minor: stop_all must not crash if _procs is mutated during iteration."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.1"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "0.1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop, _procs
        _watchdog_stop()
        _procs.clear()
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_stop_all_iterates_snapshot(self):
        """stop_all should iterate a snapshot of _procs to avoid RuntimeError
        from dict mutation during iteration."""
        from launcher.launcher import _procs
        import launcher.launcher as L

        # Add some fake procs
        for i in range(3):
            p = MagicMock()
            p.poll.return_value = None
            p.pid = 90000 + i
            p.wait.return_value = None
            _procs[f"fake_{i}"] = p

        # Patch os.killpg and os.getpgid to no-op
        with patch("os.killpg"), patch("os.getpgid", return_value=90000):
            # This should not raise RuntimeError
            try:
                L.stop_all()
            except RuntimeError as e:
                if "dictionary changed size" in str(e):
                    self.fail("stop_all must not raise RuntimeError from dict mutation")
                raise


class TestProcsKeyConsistency(unittest.TestCase):
    """I-2: _procs must not accumulate stale display-name entries after restart."""

    def setUp(self):
        os.environ["DX_WATCHDOG_POLL_SECONDS"] = "0.1"
        os.environ["DX_WATCHDOG_RESTART_DEADLINE_SECONDS"] = "0.1"

    def tearDown(self):
        from launcher.launcher import _watchdog_stop, _procs
        _watchdog_stop()
        # Clean up any test keys from _procs
        for k in list(_procs.keys()):
            if "DX App" in k or k == "dx_app":
                del _procs[k]
        os.environ.pop("DX_WATCHDOG_POLL_SECONDS", None)
        os.environ.pop("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", None)

    def test_stale_display_name_removed_after_restart(self):
        """After watchdog restart via canonical key, the stale display-name
        entry in _procs should be cleaned up."""
        from launcher.launcher import (
            _register_module, _procs, _do_module_restart, _watchdog_registry,
        )
        # Simulate initial boot: _procs has display name
        display_name = "DX App"
        canonical = "dx_app"
        mock_proc = MagicMock(poll=MagicMock(return_value=1), pid=88810)
        _procs[display_name] = mock_proc
        _register_module(canonical, port=59910, cwd="/fake", proc=mock_proc)

        entry = _watchdog_registry[canonical]
        entry["status"] = "dead"

        # Mock start_sub_server so it adds _procs[canonical]
        with patch("launcher.launcher.start_sub_server") as mock_start, \
             patch("launcher.launcher._wait_for_port", return_value=True), \
             patch("launcher.launcher._is_port_open", return_value=False):
            new_proc = MagicMock(poll=MagicMock(return_value=None), pid=88811)
            mock_start.return_value = True
            _procs[canonical] = new_proc  # simulate what start_sub_server does

            _do_module_restart(canonical, entry)

            # Stale display-name entry must not remain
            self.assertNotIn(display_name, _procs,
                             "Stale display-name key must be removed from _procs")
            # Canonical key should exist
            self.assertIn(canonical, _procs)


class TestRetryModuleLaunchContract(unittest.TestCase):
    """I-1: retryModuleLaunch must only call restartModule for watchdog-unavailable."""

    JS_PATH = Path(__file__).resolve().parents[2] / "launcher" / "static" / "launcher-app-frame.js"

    def _read_retry_body(self):
        """Return the source text of the retryModuleLaunch function."""
        src = self.JS_PATH.read_text()
        import re
        m = re.search(r'function retryModuleLaunch\b[^{]*\{', src)
        self.assertIsNotNone(m, "retryModuleLaunch function not found")
        start = m.start()
        depth = 0
        body_start = m.end() - 1
        for i in range(body_start, len(src)):
            if src[i] == '{':
                depth += 1
            elif src[i] == '}':
                depth -= 1
                if depth == 0:
                    return src[start:i + 1]
        self.fail("Could not find closing brace for retryModuleLaunch")

    def test_restart_only_for_watchdog_unavailable(self):
        """retryModuleLaunch must gate restartModule on watchdog-unavailable reason."""
        body = self._read_retry_body()
        # The function must check the reason parameter before calling restartModule
        self.assertIn("watchdog-unavailable", body,
                       "retryModuleLaunch must check for 'watchdog-unavailable' before calling restartModule")

    def test_non_watchdog_retry_skips_restart(self):
        """For non-watchdog failures (load-timeout/error), retryModuleLaunch
        should re-show app without calling restartModule."""
        body = self._read_retry_body()
        # Must accept a reason parameter
        import re
        sig = re.search(r'function retryModuleLaunch\(([^)]+)\)', body)
        self.assertIsNotNone(sig, "retryModuleLaunch must accept a reason parameter")
        params = sig.group(1)
        self.assertIn("reason", params,
                       "retryModuleLaunch signature must include a 'reason' parameter")


class TestRestartModulePlainFetch(unittest.TestCase):
    """Source contract: restartModule() uses local no-auth plain fetch."""

    JS_PATH = Path(__file__).resolve().parents[2] / "launcher" / "static" / "launcher-app-frame.js"

    def _read_restart_body(self):
        """Return the source text of the restartModule function."""
        src = self.JS_PATH.read_text()
        # Extract function body between 'function restartModule' and next top-level function/closing
        import re
        m = re.search(r'function restartModule\b[^{]*\{', src)
        self.assertIsNotNone(m, "restartModule function not found in source")
        start = m.start()
        # Find matching closing brace
        depth = 0
        body_start = m.end() - 1  # the opening brace
        for i in range(body_start, len(src)):
            if src[i] == '{':
                depth += 1
            elif src[i] == '}':
                depth -= 1
                if depth == 0:
                    return src[start:i + 1]
        self.fail("Could not find closing brace for restartModule")

    def test_restart_uses_plain_fetch(self):
        """restartModule must call plain fetch now that Startup PIN auth is removed."""
        body = self._read_restart_body()
        self.assertIn("return fetch(url, {", body)
        self.assertNotIn("DXAuth", body)

    def test_restart_preserves_post_credentials_and_json_parse(self):
        """restartModule must preserve the local restart request contract."""
        body = self._read_restart_body()
        self.assertIn("method: 'POST'", body)
        self.assertIn("credentials: 'same-origin'", body)
        self.assertIn("headers: { 'Content-Type': 'application/json' }", body)
        self.assertIn("return r.json();", body)


if __name__ == "__main__":
    unittest.main()

"""Tests for ChatEngine orchestrator."""

import os
import tempfile

# Set config dir BEFORE importing chat modules
os.environ["DX_CHAT_CONFIG_DIR"] = tempfile.mkdtemp()

import shutil
import unittest
from unittest.mock import Mock, patch

from shared.chat.config import save_config, get_config_path, load_config, _cached_config
from shared.chat.engine import ChatEngine
from shared.chat.providers import ChatAPIError


def _reset_config_cache():
    """Reset the config module's internal cache."""
    import shared.chat.config as cfg
    cfg._cached_config = None
    cfg._cached_mtime = 0.0


def _patch_engine_stream_chat(engine, mock_stream):
    """Patch the exact provider function referenced by this engine instance."""
    return patch.dict(engine.stream.__globals__, {"stream_chat": mock_stream})


class TestChatEngineNoConfig(unittest.TestCase):
    """Tests when no API config is set."""

    def setUp(self):
        self.config_dir = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.config_dir
        _reset_config_cache()
        self.engine = ChatEngine(app_name="dx_app")

    def tearDown(self):
        shutil.rmtree(self.config_dir, ignore_errors=True)
        _reset_config_cache()

    def test_stream_without_config_uses_fallback(self):
        tokens = list(self.engine.stream("안녕하세요"))
        self.assertTrue(len(tokens) > 0)
        text = "".join(tokens)
        self.assertTrue(len(text) > 0)

    def test_config_status_no_key(self):
        status = self.engine.get_config_status()
        self.assertEqual(status, {"configured": False})

    def test_error_response_points_to_chat_settings(self):
        text = "".join(self.engine._error_response("RuntimeError", "network", lang="en"))
        self.assertIn("chat settings", text)
        self.assertNotIn("Launcher Settings", text)


class TestChatEngineWithConfig(unittest.TestCase):
    """Tests when API config is set."""

    def setUp(self):
        self.config_dir = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.config_dir
        _reset_config_cache()
        save_config(provider="openai", api_key="sk-test123456", model="gpt-4o-mini")
        self.engine = ChatEngine(app_name="dx_app")

    def tearDown(self):
        shutil.rmtree(self.config_dir, ignore_errors=True)
        _reset_config_cache()

    def test_stream_calls_provider(self):
        mock_stream = Mock()
        mock_stream.return_value = iter(["Hello", " world"])
        with _patch_engine_stream_chat(self.engine, mock_stream):
            tokens = list(self.engine.stream("test question"))
        self.assertEqual(tokens, ["Hello", " world"])

    def test_stream_falls_back_on_api_error(self):
        mock_stream = Mock()
        mock_stream.side_effect = ChatAPIError("invalid_api_key", "bad key", 401)
        with _patch_engine_stream_chat(self.engine, mock_stream):
            tokens = list(self.engine.stream("test question"))
        self.assertTrue(len(tokens) > 0)
        text = "".join(tokens)
        self.assertIn("API", text)

    def test_stream_falls_back_on_unexpected_error(self):
        mock_stream = Mock()
        mock_stream.side_effect = RuntimeError("network")
        with _patch_engine_stream_chat(self.engine, mock_stream):
            tokens = list(self.engine.stream("test question"))
        self.assertTrue(len(tokens) > 0)
        text = "".join(tokens)
        self.assertTrue(len(text) > 0)

    def test_config_status_with_key(self):
        status = self.engine.get_config_status()
        self.assertTrue(status["configured"])
        self.assertEqual(status["provider"], "openai")
        self.assertEqual(status["model"], "gpt-4o-mini")
        self.assertIn("••••", status["api_key"])

    def test_config_status_includes_launcher_settings_fields(self):
        _reset_config_cache()
        save_config(
            provider="custom",
            api_key="sk-test123456",
            model="local-model",
            endpoint="http://localhost:11434/v1",
            temperature=0.42,
        )

        status = self.engine.get_config_status()

        self.assertTrue(status["configured"])
        self.assertEqual(status["provider"], "custom")
        self.assertEqual(status["model"], "local-model")
        self.assertIn("••••", status["api_key"])
        self.assertEqual(status["endpoint"], "http://localhost:11434/v1")
        self.assertEqual(status["temperature"], 0.42)


class TestContextCallback(unittest.TestCase):
    """Tests for context_callback integration."""

    def setUp(self):
        self.config_dir = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.config_dir
        _reset_config_cache()
        save_config(provider="openai", api_key="sk-test123456", model="gpt-4o-mini")

    def tearDown(self):
        shutil.rmtree(self.config_dir, ignore_errors=True)
        _reset_config_cache()

    def test_context_injected(self):
        mock_stream = Mock()
        mock_stream.return_value = iter(["ok"])

        def my_context():
            return {"device": "DX-M1", "status": "running"}

        engine = ChatEngine(app_name="dx_app", context_callback=my_context)
        with _patch_engine_stream_chat(engine, mock_stream):
            list(engine.stream("현재 상태는?"))

        # Verify stream_chat was called and system message contains context
        mock_stream.assert_called_once()
        messages = mock_stream.call_args[1].get("messages") or mock_stream.call_args[0][3]
        system_msg = messages[0]["content"]
        self.assertIn("DX-M1", system_msg)
        self.assertIn("running", system_msg)

    def test_broken_callback_doesnt_crash(self):
        mock_stream = Mock()
        mock_stream.return_value = iter(["ok"])

        def broken_callback():
            raise ValueError("callback broke")

        engine = ChatEngine(app_name="dx_app", context_callback=broken_callback)
        with _patch_engine_stream_chat(engine, mock_stream):
            tokens = list(engine.stream("test"))
        self.assertEqual(tokens, ["ok"])


if __name__ == "__main__":
    unittest.main()

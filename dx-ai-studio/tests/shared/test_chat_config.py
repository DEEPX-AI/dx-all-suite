"""Tests for shared.chat.config module."""

import json
import os
import stat
import tempfile
import unittest

# Each test class creates its own temp dir via DX_CHAT_CONFIG_DIR


class TestLoadConfigNoFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.tmp
        # Reset module-level cache
        import shared.chat.config as cfg
        cfg._cached_config = None
        cfg._cached_mtime = 0.0

    def tearDown(self):
        os.environ.pop("DX_CHAT_CONFIG_DIR", None)

    def test_no_file_returns_none(self):
        from shared.chat.config import load_config
        self.assertIsNone(load_config())


class TestSaveAndLoad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.tmp
        import shared.chat.config as cfg
        cfg._cached_config = None
        cfg._cached_mtime = 0.0

    def tearDown(self):
        os.environ.pop("DX_CHAT_CONFIG_DIR", None)

    def test_save_and_load(self):
        from shared.chat.config import save_config, load_config
        save_config(
            provider="openai",
            api_key="sk-test123",
            model="gpt-4",
            endpoint="https://api.openai.com",
            temperature=0.5,
        )
        cfg = load_config()
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["provider"], "openai")
        self.assertEqual(cfg["api_key"], "sk-test123")
        self.assertEqual(cfg["model"], "gpt-4")
        self.assertEqual(cfg["endpoint"], "https://api.openai.com")
        self.assertEqual(cfg["temperature"], 0.5)

    def test_file_permission_0600(self):
        from shared.chat.config import save_config, get_config_path
        save_config(provider="openai", api_key="key", model="gpt-4")
        path = get_config_path()
        mode = path.stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)


class TestCorruptedFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.tmp
        import shared.chat.config as cfg
        cfg._cached_config = None
        cfg._cached_mtime = 0.0

    def tearDown(self):
        os.environ.pop("DX_CHAT_CONFIG_DIR", None)

    def test_corrupted_file_returns_none(self):
        from shared.chat.config import load_config, get_config_path
        path = get_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{invalid json!!!", encoding="utf-8")
        self.assertIsNone(load_config())


class TestMtimeCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DX_CHAT_CONFIG_DIR"] = self.tmp
        import shared.chat.config as cfg
        cfg._cached_config = None
        cfg._cached_mtime = 0.0

    def tearDown(self):
        os.environ.pop("DX_CHAT_CONFIG_DIR", None)

    def test_mtime_cache(self):
        from shared.chat.config import save_config, load_config
        save_config(provider="openai", api_key="key", model="gpt-4")
        first = load_config()
        second = load_config()
        self.assertIs(first, second)


class TestMaskApiKey(unittest.TestCase):
    def test_mask_none(self):
        from shared.chat.config import mask_api_key
        self.assertIsNone(mask_api_key(None))

    def test_mask_short_key(self):
        from shared.chat.config import mask_api_key
        result = mask_api_key("abcdefgh")  # 8 chars
        self.assertIn("••", result)
        self.assertTrue(result.startswith("a"))
        self.assertTrue(result.endswith("h"))

    def test_mask_long_key(self):
        from shared.chat.config import mask_api_key
        result = mask_api_key("sk-1234567890abcdef")
        self.assertEqual(result, "sk-••••cdef")


if __name__ == "__main__":
    unittest.main()

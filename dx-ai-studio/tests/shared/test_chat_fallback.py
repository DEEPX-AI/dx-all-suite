"""Tests for shared.chat.fallback module."""

import unittest

from shared.chat.fallback import (
    COMMON_RULES,
    DEFAULT_RESPONSE,
    SETUP_BANNER,
    FallbackEngine,
)

SUPPORTED_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW")


class TestCommonGreeting(unittest.TestCase):
    def test_common_greeting_ko(self):
        engine = FallbackEngine()
        result = engine.respond("안녕하세요", lang="ko")
        self.assertIn("DX Assistant", result["reply"])
        self.assertTrue(result["is_fallback"])

    def test_common_greeting_en(self):
        engine = FallbackEngine()
        result = engine.respond("hello", lang="en")
        self.assertIn("DX Assistant", result["reply"])
        self.assertTrue(result["is_fallback"])


class TestCommonHelp(unittest.TestCase):
    def test_common_help_ko(self):
        engine = FallbackEngine()
        result = engine.respond("도움말", lang="ko")
        self.assertIn("DX AI Studio", result["reply"])

    def test_common_help_en(self):
        engine = FallbackEngine()
        result = engine.respond("help", lang="en")
        self.assertIn("DX AI Studio", result["reply"])


class TestAppSpecificRule(unittest.TestCase):
    def test_app_specific_rule_dict(self):
        app_rules = [
            (["모델", "model"], {
                "ko": "앱 전용 모델 관련 답변입니다.",
                "en": "App-specific model response.",
            }),
        ]
        engine = FallbackEngine(app_rules=app_rules)
        result_ko = engine.respond("모델 목록 알려줘", lang="ko")
        self.assertIn("앱 전용 모델 관련 답변입니다.", result_ko["reply"])
        result_en = engine.respond("show model list", lang="en")
        self.assertIn("App-specific model response.", result_en["reply"])

    def test_app_specific_rule_str_fallback(self):
        app_rules = [
            (["모델", "model"], "Plain string response"),
        ]
        engine = FallbackEngine(app_rules=app_rules)
        result = engine.respond("모델 목록", lang="en")
        self.assertIn("Plain string response", result["reply"])


class TestNoMatchDefault(unittest.TestCase):
    def test_no_match_default_ko(self):
        engine = FallbackEngine()
        result = engine.respond("xyzzy 무작위", lang="ko")
        self.assertIn("API 키를 설정하시면", result["reply"])
        self.assertIn(DEFAULT_RESPONSE["ko"], result["reply"])

    def test_no_match_default_en(self):
        engine = FallbackEngine()
        result = engine.respond("xyzzy random", lang="en")
        self.assertIn("chat settings", result["reply"])
        self.assertNotIn("Launcher Settings", result["reply"])
        self.assertIn(DEFAULT_RESPONSE["en"], result["reply"])


class TestResponseHasBanner(unittest.TestCase):
    def test_response_has_banner_ko(self):
        engine = FallbackEngine()
        for msg in ["안녕", "도움말", "xyzzy 무작위"]:
            result = engine.respond(msg, lang="ko")
            self.assertTrue(
                result["reply"].startswith(SETUP_BANNER["ko"]),
                f"Response for '{msg}' should start with Korean SETUP_BANNER",
            )

    def test_response_has_banner_en(self):
        engine = FallbackEngine()
        for msg in ["hello", "help", "xyzzy random"]:
            result = engine.respond(msg, lang="en")
            self.assertTrue(
                result["reply"].startswith(SETUP_BANNER["en"]),
                f"Response for '{msg}' should start with English SETUP_BANNER",
            )


class TestIsFallbackAlwaysTrue(unittest.TestCase):
    def test_is_fallback_always_true(self):
        engine = FallbackEngine()
        for msg in ["안녕", "help", "xyzzy 무작위"]:
            result = engine.respond(msg)
            self.assertTrue(result["is_fallback"])


class TestSuggestionsPresent(unittest.TestCase):
    def test_suggestions_ko(self):
        engine = FallbackEngine()
        result = engine.respond("안녕", lang="ko")
        self.assertIsInstance(result["suggestions"], list)
        self.assertGreater(len(result["suggestions"]), 0)

    def test_suggestions_en(self):
        engine = FallbackEngine()
        result = engine.respond("hello", lang="en")
        self.assertIsInstance(result["suggestions"], list)
        self.assertGreater(len(result["suggestions"]), 0)
        self.assertIn("What does this app do?", result["suggestions"])

    def test_default_suggestions(self):
        engine = FallbackEngine()
        result = engine.respond("xyzzy random", lang="en")
        self.assertIn("Hello", result["suggestions"])


class TestCaseInsensitive(unittest.TestCase):
    def test_case_insensitive(self):
        engine = FallbackEngine()
        result = engine.respond("HELLO")
        self.assertIn("DX Assistant", result["reply"])

    def test_app_specific_rule_keywords_are_case_insensitive(self):
        app_rules = [(["DxInfer"], {"en": "DxInfer response."})]
        engine = FallbackEngine(app_rules=app_rules)
        result = engine.respond("how does dxinfer work", lang="en")
        self.assertIn("DxInfer response.", result["reply"])


class TestAsciiKeywordMatching(unittest.TestCase):
    def test_short_ascii_keywords_do_not_match_inside_words(self):
        engine = FallbackEngine()
        result = engine.respond("this should describe the app", lang="en")
        self.assertNotIn("Hello!", result["reply"])

    def test_long_ascii_keywords_keep_substring_matching(self):
        app_rules = [
            (["pipeline"], {"en": "Pipeline response."}),
            (["webrtc"], {"en": "WebRTC response."}),
            (["gstreamer"], {"en": "GStreamer response."}),
        ]
        engine = FallbackEngine(app_rules=app_rules)
        cases = {
            "build pipelines": "Pipeline response.",
            "inspect webrtcbin": "WebRTC response.",
            "gstreamer-based graph": "GStreamer response.",
        }
        for message, expected in cases.items():
            result = engine.respond(message, lang="en")
            self.assertIn(expected, result["reply"], f"message={message!r}")


class TestDefaultLangIsEnglish(unittest.TestCase):
    def test_default_lang(self):
        engine = FallbackEngine()
        result = engine.respond("hello")
        self.assertIn(SETUP_BANNER["en"], result["reply"])


class TestFiveLanguageFallbackContracts(unittest.TestCase):
    def test_setup_banner_and_default_response_cover_all_supported_languages(self):
        for lang in SUPPORTED_LANGS:
            self.assertIn(lang, SETUP_BANNER)
            self.assertIn(lang, DEFAULT_RESPONSE)
            self.assertIsInstance(SETUP_BANNER[lang], str)
            self.assertGreater(len(SETUP_BANNER[lang]), 0)
            self.assertIsInstance(DEFAULT_RESPONSE[lang], str)
            self.assertGreater(len(DEFAULT_RESPONSE[lang]), 0)

    def test_common_rules_cover_all_supported_languages(self):
        for _keywords, response in COMMON_RULES:
            for lang in SUPPORTED_LANGS:
                self.assertIn(lang, response)
                self.assertIsInstance(response[lang], str)
                self.assertGreater(len(response[lang]), 0)

    def test_suggestions_are_localized_for_all_supported_languages(self):
        expected_fragments = {
            "en": "Hello",
            "ko": "안녕",
            "ja": "こんにちは",
            "zh-CN": "你好",
            "zh-TW": "你好",
        }
        engine = FallbackEngine()
        for lang, fragment in expected_fragments.items():
            result = engine.respond("xyzzy random", lang=lang)
            self.assertTrue(result["suggestions"])
            self.assertTrue(
                any(fragment in suggestion for suggestion in result["suggestions"]),
                f"{lang} suggestions should contain {fragment!r}: {result['suggestions']}",
            )

    def test_app_specific_rule_dict_missing_language_falls_back_to_english(self):
        app_rules = [
            (["model"], {"en": "English-only app response."}),
        ]
        engine = FallbackEngine(app_rules=app_rules)
        result = engine.respond("model help", lang="ja")
        self.assertIn("English-only app response.", result["reply"])

    def test_app_specific_rule_dict_requested_language_without_english_does_not_raise(self):
        app_rules = [(["model"], {"ja": "日本語だけの応答です。"})]
        engine = FallbackEngine(app_rules=app_rules)
        result = engine.respond("model help", lang="ja")
        self.assertIn("日本語だけの応答です。", result["reply"])

    def test_app_specific_rule_dict_empty_response_does_not_raise(self):
        app_rules = [(["model"], {})]
        engine = FallbackEngine(app_rules=app_rules)
        result = engine.respond("model help", lang="ja")
        self.assertTrue(result["is_fallback"])
        self.assertIn("---", result["reply"])


class TestLocalizedSuggestionTriggers(unittest.TestCase):
    def test_localized_greeting_suggestions_trigger_greeting_rule(self):
        cases = {
            "ja": ("こんにちは", "DeepX Edge AI"),
            "zh-CN": ("你好", "DeepX Edge AI"),
            "zh-TW": ("你好", "DeepX Edge AI"),
        }
        engine = FallbackEngine()
        for lang, (message, expected) in cases.items():
            result = engine.respond(message, lang=lang)
            self.assertIn(expected, result["reply"])
            self.assertTrue(result["suggestions"])

    def test_localized_help_suggestions_trigger_help_rule(self):
        cases = {
            "ja": ("ヘルプ", "主な機能"),
            "zh-CN": ("帮助", "主要功能"),
            "zh-TW": ("說明", "主要功能"),
        }
        engine = FallbackEngine()
        for lang, (message, expected) in cases.items():
            result = engine.respond(message, lang=lang)
            self.assertIn(expected, result["reply"])


class TestAppPurposeSuggestionRouting(unittest.TestCase):
    def test_app_purpose_suggestions_route_to_help_not_greeting_or_default(self):
        cases = {
            "en": ("What does this app do?", "key features"),
            "ja": ("このアプリは何ができますか？", "主な機能"),
            "zh-CN": ("这个应用能做什么？", "主要功能"),
            "zh-TW": ("這個應用可以做什麼？", "主要功能"),
        }
        engine = FallbackEngine()
        for lang, (message, expected) in cases.items():
            result = engine.respond(message, lang=lang)
            self.assertIn(expected, result["reply"],
                f"lang={lang}: expected help response with '{expected}'")
            self.assertNotIn("Hello!", result["reply"],
                f"lang={lang}: should not match greeting")

if __name__ == "__main__":
    unittest.main()

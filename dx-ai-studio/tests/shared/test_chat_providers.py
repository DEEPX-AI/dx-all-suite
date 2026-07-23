"""Tests for shared.chat.providers module."""

import json
import unittest
from unittest.mock import Mock, patch

from shared.chat.providers import (
    ChatAPIError,
    build_anthropic_request,
    build_google_request,
    build_openai_request,
    parse_anthropic_sse_line,
    parse_google_sse_line,
    parse_openai_sse_line,
    stream_chat,
)


def _patch_stream_chat_http(mock_stream):
    """Patch the exact HTTP helper referenced by the imported stream_chat."""
    return patch.dict(stream_chat.__globals__, {"_http_stream": mock_stream})




class TestParseOpenAISSE(unittest.TestCase):
    def test_normal_delta(self):
        line = 'data: {"choices":[{"delta":{"content":"hello"}}]}'
        self.assertEqual(parse_openai_sse_line(line), "hello")

    def test_done(self):
        line = "data: [DONE]"
        self.assertIsNone(parse_openai_sse_line(line))

    def test_empty_delta(self):
        line = 'data: {"choices":[{"delta":{}}]}'
        self.assertEqual(parse_openai_sse_line(line), "")

    def test_non_data_line(self):
        self.assertEqual(parse_openai_sse_line("event: ping"), "")


class TestParseAnthropicSSE(unittest.TestCase):
    def test_content_block_delta(self):
        payload = {
            "type": "content_block_delta",
            "delta": {"type": "text_delta", "text": "world"},
        }
        line = f"data: {json.dumps(payload)}"
        self.assertEqual(parse_anthropic_sse_line(line), "world")

    def test_non_text_event(self):
        payload = {"type": "message_start"}
        line = f"data: {json.dumps(payload)}"
        self.assertEqual(parse_anthropic_sse_line(line), "")

    def test_non_data_line(self):
        self.assertEqual(parse_anthropic_sse_line("event: message_start"), "")


class TestParseGoogleSSE(unittest.TestCase):
    def test_normal_candidate(self):
        payload = {
            "candidates": [
                {"content": {"parts": [{"text": "hi"}]}}
            ]
        }
        line = f"data: {json.dumps(payload)}"
        self.assertEqual(parse_google_sse_line(line), "hi")

    def test_empty_candidates(self):
        line = 'data: {"candidates":[]}'
        self.assertEqual(parse_google_sse_line(line), "")

    def test_non_data_line(self):
        self.assertEqual(parse_google_sse_line("event: keep-alive"), "")




class TestBuildOpenAIRequest(unittest.TestCase):
    def test_default_url(self):
        req = build_openai_request("sk-key", "gpt-4", [{"role": "user", "content": "hi"}])
        self.assertEqual(req["url"], "https://api.openai.com/v1/chat/completions")

    def test_auth_header(self):
        req = build_openai_request("sk-key", "gpt-4", [])
        self.assertEqual(req["headers"]["Authorization"], "Bearer sk-key")

    def test_stream_true(self):
        req = build_openai_request("sk-key", "gpt-4", [])
        body = json.loads(req["body"])
        self.assertTrue(body["stream"])

    def test_custom_endpoint(self):
        req = build_openai_request(
            "sk-key", "gpt-4", [],
            endpoint="https://my-server.example.com/v1/chat/completions",
        )
        self.assertEqual(req["url"], "https://my-server.example.com/v1/chat/completions")


class TestBuildAnthropicRequest(unittest.TestCase):
    def test_system_extracted(self):
        msgs = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "hi"},
        ]
        req = build_anthropic_request("ak-key", "claude-3", msgs)
        body = json.loads(req["body"])
        self.assertEqual(body["system"], "You are helpful")
        self.assertEqual(len(body["messages"]), 1)
        self.assertEqual(body["messages"][0]["role"], "user")

    def test_headers(self):
        req = build_anthropic_request("ak-key", "claude-3", [])
        self.assertEqual(req["headers"]["x-api-key"], "ak-key")
        self.assertEqual(req["headers"]["anthropic-version"], "2023-06-01")

    def test_stream_and_max_tokens(self):
        req = build_anthropic_request("ak-key", "claude-3", [])
        body = json.loads(req["body"])
        self.assertTrue(body["stream"])
        self.assertEqual(body["max_tokens"], 4096)


class TestBuildGoogleRequest(unittest.TestCase):
    def test_url_contains_key_and_model(self):
        req = build_google_request("gk-key", "gemini-pro", [])
        self.assertIn("gemini-pro", req["url"])
        self.assertIn("key=gk-key", req["url"])
        self.assertIn("alt=sse", req["url"])

    def test_message_format(self):
        msgs = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        req = build_google_request("gk-key", "gemini-pro", msgs)
        body = json.loads(req["body"])
        self.assertIn("systemInstruction", body)
        self.assertEqual(body["systemInstruction"]["parts"][0]["text"], "sys")
        self.assertEqual(len(body["contents"]), 2)
        self.assertEqual(body["contents"][0]["role"], "user")
        self.assertEqual(body["contents"][1]["role"], "model")




class TestStreamChatErrors(unittest.TestCase):
    def test_401_invalid_api_key(self):
        mock_stream = Mock()
        mock_stream.side_effect = ChatAPIError("invalid_api_key", "Invalid API key", 401)
        with _patch_stream_chat_http(mock_stream):
            with self.assertRaises(ChatAPIError) as ctx:
                list(stream_chat("openai", "bad-key", "gpt-4", []))
        self.assertEqual(ctx.exception.error_type, "invalid_api_key")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_429_rate_limit(self):
        mock_stream = Mock()
        mock_stream.side_effect = ChatAPIError("rate_limit", "Rate limit exceeded", 429)
        with _patch_stream_chat_http(mock_stream):
            with self.assertRaises(ChatAPIError) as ctx:
                list(stream_chat("openai", "key", "gpt-4", []))
        self.assertEqual(ctx.exception.error_type, "rate_limit")
        self.assertEqual(ctx.exception.status_code, 429)




class TestStreamChat(unittest.TestCase):
    def test_openai_yields_tokens(self):
        mock_stream = Mock()
        mock_stream.return_value = iter([
            'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            'data: {"choices":[{"delta":{"content":" world"}}]}',
            "data: [DONE]",
        ])
        with _patch_stream_chat_http(mock_stream):
            tokens = list(stream_chat("openai", "k", "gpt-4", []))
        self.assertEqual(tokens, ["Hello", " world"])

    def test_custom_uses_endpoint(self):
        mock_stream = Mock()
        mock_stream.return_value = iter([
            'data: {"choices":[{"delta":{"content":"ok"}}]}',
            "data: [DONE]",
        ])
        with _patch_stream_chat_http(mock_stream):
            list(stream_chat("custom", "k", "m", [], endpoint="https://my.api/v1/chat/completions"))
        call_args = mock_stream.call_args
        self.assertEqual(call_args[0][0], "https://my.api/v1/chat/completions")

    def test_github_uses_fixed_endpoint(self):
        mock_stream = Mock()
        mock_stream.return_value = iter([
            'data: {"choices":[{"delta":{"content":"hi"}}]}',
            "data: [DONE]",
        ])
        with _patch_stream_chat_http(mock_stream):
            list(stream_chat("github", "ghp_testtoken", "gpt-4o-mini", []))
        call_args = mock_stream.call_args
        self.assertIn("models.inference.ai.azure.com", call_args[0][0])

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            list(stream_chat("bad_provider", "k", "m", []))


if __name__ == "__main__":
    unittest.main()

"""P2: 범용 로컬/자체호스팅 LLM provider (OpenAI 호환, 키 불필요) + 모델 조회.

로컬 런타임(Ollama/llama.cpp/LM Studio/vLLM 등)은 대부분 OpenAI 호환 API를 노출하므로
provider="local"은 사용자가 지정한 base URL로 OpenAI 스타일 요청을 보낸다. API 키 불필요.
"""
import json
from unittest.mock import patch

from shared.chat import providers
from shared.chat.providers import stream_chat, local_chat_url, discover_local_models


def _patch_http(mock_stream):
    return patch.dict(stream_chat.__globals__, {"_http_stream": mock_stream})


class TestLocalChatUrl:
    def test_bare_host_gets_v1_chat_completions(self):
        assert local_chat_url("http://localhost:11434") == "http://localhost:11434/v1/chat/completions"

    def test_v1_suffix_gets_chat_completions(self):
        assert local_chat_url("http://localhost:1234/v1") == "http://localhost:1234/v1/chat/completions"

    def test_full_url_unchanged(self):
        u = "http://host:8000/v1/chat/completions"
        assert local_chat_url(u) == u

    def test_empty_defaults_to_ollama(self):
        assert local_chat_url("") == "http://localhost:11434/v1/chat/completions"


class TestLocalProviderDispatch:
    def test_local_in_builders(self):
        assert "local" in providers._BUILDERS and "local" in providers._PARSERS

    def test_local_streams_without_api_key(self):
        captured = {}

        def fake_http(url, headers, body, timeout=120):
            captured["url"] = url
            yield 'data: {"choices":[{"delta":{"content":"hi"}}]}'
            yield "data: [DONE]"

        with _patch_http(fake_http):
            out = list(stream_chat(
                provider="local", api_key="", model="qwen2.5",
                messages=[{"role": "user", "content": "x"}],
                endpoint="http://localhost:11434",
            ))
        assert out == ["hi"]
        assert captured["url"] == "http://localhost:11434/v1/chat/completions"


class TestDiscoverLocalModels:
    def test_openai_models_endpoint(self):
        payload = json.dumps({"data": [{"id": "qwen2.5"}, {"id": "deepseek-r1"}]}).encode()

        class R:
            status = 200
            def read(self): return payload
            def __enter__(self): return self
            def __exit__(self, *a): return False

        with patch.object(providers.urllib.request, "urlopen", lambda *a, **k: R()):
            models = discover_local_models("http://localhost:1234")
        assert "qwen2.5" in models and "deepseek-r1" in models

    def test_ollama_tags_fallback(self):
        ollama = json.dumps({"models": [{"name": "llama3"}, {"name": "deepseek-r1:7b"}]}).encode()
        calls = {"n": 0}

        class R:
            def __init__(self, body): self._b = body
            def read(self): return self._b
            def __enter__(self): return self
            def __exit__(self, *a): return False

        def fake_urlopen(req, *a, **k):
            calls["n"] += 1
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if "/v1/models" in url:
                raise OSError("no openai endpoint")
            return R(ollama)

        with patch.object(providers.urllib.request, "urlopen", fake_urlopen):
            models = discover_local_models("http://localhost:11434")
        assert "llama3" in models and "deepseek-r1:7b" in models

    def test_returns_empty_on_total_failure(self):
        def boom(*a, **k):
            raise OSError("down")
        with patch.object(providers.urllib.request, "urlopen", boom):
            assert discover_local_models("http://localhost:9999") == []

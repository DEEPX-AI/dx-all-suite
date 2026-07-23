"""Tests for shared.chat.prompt_builder."""

import pytest
from shared.chat.prompt_builder import (
    extract_keywords,
    parse_sections,
    match_sections,
    build_system_prompt,
)

SAMPLE_MD = """## [section:overview] 개요
이것은 개요입니다.

## [section:compile,빌드,build] 컴파일
컴파일 관련 내용입니다.

## [section:error,에러,오류] 에러 대응
에러 해결 방법입니다.

## [section:install,설치,setup] 설치
설치 방법입니다.
"""


class TestParseSections:
    def test_parse_all_sections(self):
        sections = parse_sections(SAMPLE_MD)
        assert len(sections) == 4

        assert sections[0]["tag"] == "overview"
        assert sections[0]["keywords"] == ["overview"]
        assert sections[0]["title"] == "개요"
        assert "개요입니다" in sections[0]["content"]

        assert sections[1]["tag"] == "compile"
        assert sections[1]["keywords"] == ["compile", "빌드", "build"]
        assert sections[1]["title"] == "컴파일"

        assert sections[2]["tag"] == "error"
        assert sections[2]["keywords"] == ["error", "에러", "오류"]
        assert sections[2]["title"] == "에러 대응"

        assert sections[3]["tag"] == "install"
        assert sections[3]["keywords"] == ["install", "설치", "setup"]
        assert sections[3]["title"] == "설치"

    def test_empty_input(self):
        assert parse_sections("") == []


class TestExtractKeywords:
    def test_removes_stopwords(self):
        result = extract_keywords("이 모델을 어떻게 컴파일 하나요?")
        assert "이" not in result
        assert "어떻게" not in result
        # Should keep meaningful words
        assert "모델을" in result or "모델" in result or "컴파일" in result

    def test_lowercases(self):
        result = extract_keywords("COMPILE Error")
        assert "compile" in result
        assert "error" in result


class TestMatchSections:
    def setup_method(self):
        self.sections = parse_sections(SAMPLE_MD)

    def test_exact_match(self):
        matched = match_sections(self.sections, "컴파일 에러")
        tags = [s["tag"] for s in matched]
        # Should match both compile (via synonym) and error (via synonym)
        assert "compile" in tags or "error" in tags

    def test_synonym_match(self):
        matched = match_sections(self.sections, "build failed")
        tags = [s["tag"] for s in matched]
        assert "compile" in tags

    def test_fuzzy_match(self):
        matched = match_sections(self.sections, "컴팡일 방법")
        tags = [s["tag"] for s in matched]
        assert "compile" in tags

    def test_no_match_returns_overview(self):
        matched = match_sections(self.sections, "xyzzy random garbage")
        tags = [s["tag"] for s in matched]
        assert "overview" in tags
        assert len(matched) <= 3

    def test_respects_max_sections(self):
        matched = match_sections(self.sections, "컴파일 에러 설치", max_sections=2)
        assert len(matched) <= 2


class TestBuildSystemPrompt:
    def test_includes_base_and_app(self, tmp_path):
        knowledge = tmp_path / "knowledge"
        knowledge.mkdir()
        (knowledge / "base.md").write_text("BASE CONTENT", encoding="utf-8")
        (knowledge / "myapp.md").write_text(SAMPLE_MD, encoding="utf-8")

        result = build_system_prompt(
            knowledge, "myapp", "컴파일 방법",
            runtime_context={"current_model": "yolov8"},
        )
        assert "BASE CONTENT" in result
        assert "컴파일" in result
        assert "current_model" in result
        assert "yolov8" in result

    def test_missing_app_md(self, tmp_path):
        knowledge = tmp_path / "knowledge"
        knowledge.mkdir()
        (knowledge / "base.md").write_text("BASE ONLY", encoding="utf-8")

        result = build_system_prompt(knowledge, "nonexistent", "hello")
        assert "BASE ONLY" in result

    def test_missing_base_md(self, tmp_path):
        knowledge = tmp_path / "knowledge"
        knowledge.mkdir()

        result = build_system_prompt(
            knowledge, "noapp", "hello",
            runtime_context={"status": "ok"},
        )
        assert len(result) > 0
        assert "status" in result

    def test_runtime_context_injected(self, tmp_path):
        knowledge = tmp_path / "knowledge"
        knowledge.mkdir()
        (knowledge / "base.md").write_text("base", encoding="utf-8")

        result = build_system_prompt(
            knowledge, "x", "hello",
            runtime_context={"current_model": "yolov8"},
        )
        assert "current_model" in result
        assert "yolov8" in result

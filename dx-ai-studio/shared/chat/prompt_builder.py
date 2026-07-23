"""Prompt builder with section-based knowledge injection."""
from __future__ import annotations

import re
import difflib
from pathlib import Path

SYNONYMS = {
    "compile":  ["컴파일", "빌드", "변환", "build", "convert", "onnx", "dxnn"],
    "error":    ["에러", "오류", "실패", "안됨", "안돼", "문제", "fail", "bug", "crash"],
    "model":    ["모델", "네트워크", "network", "weights"],
    "install":  ["설치", "셋업", "setup", "다운로드", "download"],
    "speed":    ["속도", "느림", "빠르", "성능", "fps", "latency", "throughput"],
    "pipeline": ["파이프라인", "스트림", "gstreamer", "gst", "pipe"],
    "hardware": ["하드웨어", "npu", "cpu", "보드", "장치", "디바이스", "device"],
    "thermal":  ["열", "온도", "발열", "쿨링", "냉각", "throttle", "temperature"],
    "inference":["추론", "실행", "run", "predict", "infer"],
    "video":    ["비디오", "영상", "카메라", "camera", "stream", "rtsp"],
}

STOPWORDS = {
    "이", "가", "은", "는", "을", "를", "의", "에", "에서", "로", "으로",
    "와", "과", "도", "만", "까지", "부터", "에서", "하다", "되다", "있다",
    "없다", "이다", "아니다", "그", "저", "이것", "그것", "어떻게", "왜",
    "뭐", "무엇", "어디", "the", "a", "an", "is", "are", "was", "were",
    "do", "does", "did", "how", "what", "why", "where", "can", "could",
    "i", "me", "my", "it", "this", "that", "to", "in", "on", "for",
}

# Pre-build reverse synonym lookup: synonym_word -> canonical_keyword
_SYNONYM_REVERSE: dict[str, str] = {}
for _canonical, _syns in SYNONYMS.items():
    for _s in _syns:
        _SYNONYM_REVERSE[_s.lower()] = _canonical


def extract_keywords(text: str) -> list[str]:
    """Split text, remove stopwords, return lowercased keywords."""
    tokens = re.split(r'[\s,;:!?\.\(\)\[\]\{\}\"\']+', text)
    return [
        t.lower()
        for t in tokens
        if t and t.lower() not in STOPWORDS
    ]


_SECTION_RE = re.compile(r'^## \[section:([^\]]+)\]\s+(.+)$', re.MULTILINE)


def parse_sections(md_text: str) -> list[dict]:
    """Parse markdown with ``## [section:kw1,kw2,...] Title`` headers."""
    matches = list(_SECTION_RE.finditer(md_text))
    if not matches:
        return []

    sections: list[dict] = []
    for i, m in enumerate(matches):
        keywords = [k.strip() for k in m.group(1).split(",")]
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        content = md_text[start:end].strip()
        sections.append({
            "tag": keywords[0],
            "keywords": keywords,
            "title": title,
            "content": content,
        })
    return sections


def match_sections(
    sections: list[dict],
    user_message: str,
    max_sections: int = 4,
) -> list[dict]:
    """Score and select the most relevant sections for a user message."""
    user_kws = extract_keywords(user_message)
    if not sections:
        return []

    # Collect all section keywords for fuzzy matching pool
    all_section_kws: list[str] = []
    for sec in sections:
        all_section_kws.extend(sec["keywords"])
    all_section_kws = list(set(all_section_kws))

    scores: dict[int, int] = {i: 0 for i in range(len(sections))}
    for ukw in user_kws:
        canonical = _SYNONYM_REVERSE.get(ukw)

        for i, sec in enumerate(sections):
            sec_kws_lower = [k.lower() for k in sec["keywords"]]
            if ukw in sec_kws_lower:
                scores[i] += 1
                continue
            if canonical and canonical in sec_kws_lower:
                scores[i] += 1
                continue
            close = difflib.get_close_matches(ukw, sec_kws_lower, n=1, cutoff=0.7)
            if close:
                scores[i] += 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    has_match = ranked[0][1] > 0 if ranked else False

    if not has_match:
        # Fallback: overview + first 2 other sections
        result: list[dict] = []
        for sec in sections:
            if sec["tag"] == "overview":
                result.append(sec)
                break
        for sec in sections:
            if sec["tag"] != "overview" and len(result) < 3:
                result.append(sec)
        return result[:max_sections]

    matched = [sections[i] for i, score in ranked if score > 0]

    # Always include overview if available and not already present
    overview = None
    for sec in sections:
        if sec["tag"] == "overview":
            overview = sec
            break

    if overview and overview not in matched:
        matched.insert(0, overview)

    return matched[:max_sections]


# mtime-keyed caches so unchanged knowledge files aren't re-read/re-parsed on
# every chat message. Keyed by (path, mtime): a file rewrite (e.g. the
# launcher-boot resync or a "refresh knowledge" action) changes its mtime,
# which naturally invalidates the stale entry — no explicit TTL needed.
# Old entries for the same path are dropped so the dict can't grow unbounded
# across repeated edits of the same file.
_text_cache: dict[tuple[str, float], str] = {}
_sections_cache: dict[tuple[str, float], list[dict]] = {}


def _cached_read_text(path: Path) -> str:
    """``path.read_text()``, cached by (path, mtime)."""
    mtime = path.stat().st_mtime
    key = (str(path), mtime)
    cached = _text_cache.get(key)
    if cached is not None:
        return cached
    text = path.read_text(encoding="utf-8")
    for stale in [k for k in _text_cache if k[0] == key[0] and k != key]:
        del _text_cache[stale]
    _text_cache[key] = text
    return text


def _cached_parse_sections(path: Path) -> list[dict]:
    """``parse_sections(path.read_text())``, cached by (path, mtime)."""
    mtime = path.stat().st_mtime
    key = (str(path), mtime)
    cached = _sections_cache.get(key)
    if cached is not None:
        return cached
    sections = parse_sections(path.read_text(encoding="utf-8"))
    for stale in [k for k in _sections_cache if k[0] == key[0] and k != key]:
        del _sections_cache[stale]
    _sections_cache[key] = sections
    return sections


def build_system_prompt(
    knowledge_dir: Path,
    app_name: str,
    user_message: str,
    runtime_context: dict | None = None,
) -> str:
    """Assemble a system prompt from knowledge docs and runtime context."""
    parts: list[str] = []

    base_path = knowledge_dir / "base.md"
    if base_path.exists():
        parts.append(_cached_read_text(base_path).strip())

    app_path = knowledge_dir / f"{app_name}.md"
    if app_path.exists():
        sections = _cached_parse_sections(app_path)
        matched = match_sections(sections, user_message)
        for sec in matched:
            parts.append(f"## {sec['title']}\n{sec['content']}")

    # 2.5 SDK knowledge (auto-generated from the .deepx warehouse), section-matched.
    sdk_path = knowledge_dir / "sdk_knowledge.md"
    if sdk_path.exists():
        try:
            sdk_sections = _cached_parse_sections(sdk_path)
        except OSError:
            sdk_sections = []
        for sec in match_sections(sdk_sections, user_message, max_sections=3):
            parts.append(f"## {sec['title']}\n{sec['content']}")

    if runtime_context:
        lines = [f"- {k}: {v}" for k, v in runtime_context.items()]
        parts.append("## 현재 상태\n" + "\n".join(lines))

    return "\n\n".join(parts)

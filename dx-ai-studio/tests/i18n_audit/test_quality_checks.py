"""여섯 언어 감사는 지금 **칸이 채워졌는지** 만 본다. 그 위의 층이 비어 있었다.

classify.py 가 내는 결함은 두 종류뿐이다:

    missing-language   키가 비었다
    stale-copy         영어와 글자 그대로 같다

그래서 "findings 0건" 은 **"번역 테이블에 빈 칸이 없다"** 는 뜻이지
**"사용자가 어색한 문구를 안 본다"** 는 뜻이 아니다. 실제로 4249건을 훑어보니
기계가 잡을 수 있는 결함이 남아 있었다(2026-09-21 실측):

    용어 불일치      254건 (최초 289 에서 결정 불필요분 35건 처리)   같은 영어가 화면마다 다르게 번역된다
                            Dashboard[zh-CN] 仪表板/仪表盘, Task[ko] 작업/태스크
    길이 폭주         22건   번역이 영어의 2.2배를 넘어 UI 를 넘칠 위험
    플레이스홀더 깨짐    0건   (이미 깨끗 — 그래도 계약으로 고정한다)

세 번째 층(문법·어투가 자연스러운가)은 기계로 판정할 수 없다. 여기서 시도하지
않는다 — 통과했는데 실제로는 어색한 "가짜 안전감" 이 지금의 0건보다 나쁘다.
대신 원어민이 볼 목록을 만드는 데까지가 이 파일의 몫이다.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]



def _rec(en, lang=None, value=None, source_file="a.js", **texts):
    """AuditRecord 를 테스트에서 간단히 만든다 (필수 필드가 많다)."""
    from tools.i18n_audit.schema import AuditRecord

    t = {"en": en}
    if lang:
        t[lang] = value
    t.update(texts)
    return AuditRecord(module="m", surface="s", route_or_state="/", source_file=source_file,
                       selector_or_key="k", text_role="label", texts=t)


def _records():
    from tools.i18n_audit.extractors import extract_inventory
    from tools.i18n_audit.tutorial_copy import extract_tutorial_records

    return extract_inventory(ROOT) + extract_tutorial_records(ROOT)


class TestTerminologyStaysConsistent:
    def test_the_checker_exists(self):
        from tools.i18n_audit.classify import classify_terminology_drift  # noqa: F401

    def test_the_same_english_translated_two_ways_is_reported(self):
        from tools.i18n_audit.classify import classify_terminology_drift
        recs = [_rec("Dashboard", "ko", "대시보드", source_file="a.js"),
                _rec("Dashboard", "ko", "계기판", source_file="b.js")]
        findings = classify_terminology_drift(recs)
        assert findings, "같은 영어가 다르게 번역됐는데 보고하지 않는다"
        assert all(f.issue_type == "terminology-drift" for f in findings)
        blob = " ".join(f.message for f in findings)
        assert "대시보드" in blob and "계기판" in blob, "어떤 번역들이 갈렸는지 말해야 한다"

    def test_one_consistent_translation_is_not_reported(self):
        from tools.i18n_audit.classify import classify_terminology_drift
        recs = [_rec("Dashboard", "ko", "대시보드", source_file=f"{i}.js") for i in range(3)]
        assert classify_terminology_drift(recs) == []

    def test_short_strings_are_left_alone(self):
        """'ID' 나 'OK' 같은 짧은 것은 문맥마다 달라도 정상이다."""
        from tools.i18n_audit.classify import classify_terminology_drift
        recs = [_rec("ID", "ko", "아이디", source_file="a.js"),
                _rec("ID", "ko", "식별자", source_file="b.js")]
        assert classify_terminology_drift(recs) == []


class TestTranslationsDoNotBlowUpInLength:
    def test_the_checker_exists(self):
        from tools.i18n_audit.classify import classify_length_overflow  # noqa: F401

    def test_a_translation_far_longer_than_english_is_reported(self):
        from tools.i18n_audit.classify import classify_length_overflow
        rec = _rec('Warmup Runs', 'es', 'Ejecuciones de calentamiento previo')
        findings = classify_length_overflow([rec])
        assert findings and findings[0].issue_type == "length-overflow"

    def test_a_similar_length_translation_is_not_reported(self):
        from tools.i18n_audit.classify import classify_length_overflow
        rec = _rec('Warmup Runs', 'ko', '워밍업 실행')
        assert classify_length_overflow([rec]) == []

    def test_cjk_is_not_penalised_for_being_short(self):
        """중국어는 영어보다 **짧다**. 길이 검사가 그것을 결함으로 세면 안 된다."""
        from tools.i18n_audit.classify import classify_length_overflow
        rec = _rec('Warmup Runs', 'zh-CN', '预热运行')
        assert classify_length_overflow([rec]) == []


class TestPlaceholdersSurviveTranslation:
    def test_the_checker_exists(self):
        from tools.i18n_audit.classify import classify_placeholder_mismatch  # noqa: F401

    def test_a_dropped_placeholder_is_reported(self):
        from tools.i18n_audit.classify import classify_placeholder_mismatch
        rec = _rec('Found {n} models', 'ko', '모델을 찾았습니다')
        findings = classify_placeholder_mismatch([rec])
        assert findings and findings[0].issue_type == "placeholder-mismatch"

    def test_a_preserved_placeholder_is_fine(self):
        from tools.i18n_audit.classify import classify_placeholder_mismatch
        rec = _rec('Found {n} models', 'ko', '모델 {n}개를 찾았습니다')
        assert classify_placeholder_mismatch([rec]) == []


class TestTheRealRepositoryIsMeasured:
    """실측값을 계약으로 고정한다 — 줄어드는 방향만 허용하는 ratchet."""

    # 2026-09-21 실측. 고치면 이 수를 내린다. 올리려면 근거가 필요하다.
    #
    # 처음에 143 으로 적었다가 289 로 올렸다. 어림값(143)은 브랜드·약어를 거르지
    # 않고 `len(en) >= 4` 로만 센 것이었고, 실제 검사기는 'ID'·'FPS' 같은 약어를
    # 빼는 대신 'Dashboard' 같은 한 낱말 용어를 **포함** 한다 — 정작 화면마다
    # 갈리기 쉬운 것이 그런 말이라서다. 상한은 어림이 아니라 검사기가 실제로
    # 세는 값이어야 한다.
    # 289 -> 254 (2026-09-21). 결정이 필요 없는 것만 고쳤다:
    #   CJK 공백 통일 25+16건  라틴문자와 한자 사이 공백. 저장소 관행이
    #                          "공백 있음" 이 지배적이라(ja 1561:899, zh 약 2.4:1)
    #                          내 취향이 아니라 다수를 따랐다.
    #   영어로 남은 용어           Sync/Async/SDK Library/Presets — 한국어 화면에
    #                          영어가 그대로 뜨던 것들. 번역본은 이미 다른 모듈에
    #                          있었다.
    # 남은 254건은 제품 결정이 필요하다 — '작업' vs '태스크' 처럼 어느 쪽으로
    # 통일할지는 내가 정할 일이 아니다. /path/to/*.json 같은 placeholder 경로를
    # 번역할지도 마찬가지다.
    # 2026-10-11: 239 — the cap follows the count down (Lab strings reuse the existing Pipeline started / Throughput terms).
    MAX_TERMINOLOGY_DRIFT = 239
    # 23 -> 22 (2026-09-21). **0 을 목표로 삼지 않는다.**
    # 23건을 하나씩 읽어 보니 대부분 정당한 번역이었다:
    #   'Inference timed out' -> 'La inferencia agotó el tiempo de espera'
    # 스페인어가 길 뿐이고, 줄이면 오히려 나빠진다. 게다가 상당수는 버튼 라벨이
    # 아니라 오류 **메시지** 라 길이가 문제되지 않는다.
    # 실제로 고친 것은 하나 — '🔧 Firmware'[es] 가 영어에 없는 'del dispositivo'
    # 를 덧붙이고 있었다(다른 다섯 언어는 전부 한 낱말). dashboard.js:563 의
    # 메트릭 라벨이다.
    # 이 검사의 값은 0 으로 모는 데 있지 않고, **볼 만한 것을 골라 주는 데** 있다.
    # 2026-10-02 +2: 'runner_error' · 'live_deps_missing' (dx_app i18n.js) — 'process_exit' 처럼 영어 쪽이
    # 문장이 아니라 오류 key 라 key 길이와 비교된다. 번역은 한 문장 오류 메시지다.
    MAX_LENGTH_OVERFLOW = 24
    MAX_PLACEHOLDER_MISMATCH = 0

    def test_terminology_drift_does_not_grow(self):
        from tools.i18n_audit.classify import classify_terminology_drift

        n = len(classify_terminology_drift(_records()))
        assert n <= self.MAX_TERMINOLOGY_DRIFT, (
            f"용어 불일치가 {n}건으로 늘었다 (상한 {self.MAX_TERMINOLOGY_DRIFT})")

    def test_length_overflow_does_not_grow(self):
        from tools.i18n_audit.classify import classify_length_overflow

        n = len(classify_length_overflow(_records()))
        assert n <= self.MAX_LENGTH_OVERFLOW, (
            f"길이 폭주가 {n}건으로 늘었다 (상한 {self.MAX_LENGTH_OVERFLOW})")

    def test_placeholders_stay_intact(self):
        from tools.i18n_audit.classify import classify_placeholder_mismatch

        findings = classify_placeholder_mismatch(_records())
        assert len(findings) <= self.MAX_PLACEHOLDER_MISMATCH, (
            "번역이 플레이스홀더를 잃었다:\n  "
            + "\n  ".join(f.message for f in findings[:10]))


class TestServerMessagesAreCounted:
    """서버가 만들어 화면에 그대로 띄우는 영어 문자열.

    config_wizard.js:531 이 이렇게 한다:

        alert(T('Config generation failed: ') + data.error);

    앞은 번역되고 **뒤에 붙는 data.error 는 영어 그대로** 다. 한국어로 쓰던
    사용자는 "설정 생성 실패: Invalid opt_level: 'abc' — must be one of [0, 1]"
    을 본다.

    기존 파이썬 추출기(extractors.py:364)는 dict/list 리터럴 **할당만** 파싱한다.
    번역 테이블은 보지만 `send_error_json(400, "...")` 처럼 함수 인자로 들어간
    문자열은 구조적으로 못 본다. 그래서 감사가 0건이어도 이 91개는 세어지지
    않았다(2026-09-21 실측 92건) — 그중 24개는 2026-09-21 SR-758 작업에서 내가 넣은 것이다.
    """

    # 2026-09-21 실측. 번역하거나 범위를 줄이면 내린다.
    # 어림으로 91 이라 적었다가 검사기가 센 92 로 맞췄다 — f-string 의 리터럴
    # 부분을 이어 붙이는 방식이 어림셈과 한 건 달랐다. 상한은 어림이 아니라
    # 검사기가 세는 값이어야 한다.
    #   dx_compiler 70 · shared 9 · dx_agent_dev 8 · dx_benchmark 3 · launcher 2
    # 92 건 자체는 그대로다 — **서버 코드를 건드리지 않기로** 했기 때문이다.
    # 대신 표시 직전에 프론트가 번역한다(shared/static/server-error-i18n.js,
    # 2026-09-21). 이 상한이 재는 것은 "서버에 영어 문자열이 몇 개인가" 이지
    # "사용자가 영어를 보는가" 가 아니다. 후자는
    # tests/test_server_error_i18n.py 가 본다.
    #
    # 그러므로 이 수를 0 으로 모는 것은 목표가 아니다. 새 메시지가 늘어나는
    # 것만 막는다 — 늘어나면 번역 패턴도 같이 늘려야 한다.
    # 2026-10-01 +2: 원격 접근 거절 ('Host not allowed' · 'Cross-origin request refused', QA COM-A1) —
    # server-error-i18n.js 에 6개 언어 패턴을 같이 넣었다.
    MAX_UNTRANSLATED_SERVER_MESSAGES = 94

    def test_the_extractor_exists(self):
        from tools.i18n_audit.extractors import extract_server_messages  # noqa: F401

    def test_a_send_error_json_string_is_found(self, tmp_path):
        from tools.i18n_audit.extractors import extract_server_messages

        src = 'def h(self):\n    return self.send_error_json(400, "Invalid opt_level")\n'
        found = extract_server_messages(src, module="m", source_file="a.py")
        assert [f.text for f in found] == ["Invalid opt_level"]

    def test_an_fstring_is_found_by_its_literal_parts(self, tmp_path):
        from tools.i18n_audit.extractors import extract_server_messages

        src = 'def h(x):\n    raise ValidationError(f"Invalid opt_level: {x} — must be one of")\n'
        found = extract_server_messages(src, module="m", source_file="a.py")
        assert found and "must be one of" in found[0].text

    def test_internal_strings_are_not_counted(self):
        """로깅이나 예외 메시지 전부를 세면 신호가 묻힌다 — 화면에 닿는 호출만 본다."""
        from tools.i18n_audit.extractors import extract_server_messages

        src = 'import logging\ndef h():\n    logging.info("starting up")\n    raise ValueError("internal")\n'
        assert extract_server_messages(src, module="m", source_file="a.py") == []

    def test_the_repository_count_does_not_grow(self):
        from tools.i18n_audit.extractors import extract_server_messages

        total = 0
        for path in sorted(ROOT.rglob("*.py")):
            rel = str(path.relative_to(ROOT))
            if any(x in rel for x in (".venv", "node_modules", "tests/", "test_", "scripts/", "tools/")):
                continue
            total += len(extract_server_messages(
                path.read_text(encoding="utf-8"), module="?", source_file=rel))
        assert total <= self.MAX_UNTRANSLATED_SERVER_MESSAGES, (
            f"화면에 뜨는 영어 서버 메시지가 {total}개로 늘었다 "
            f"(상한 {self.MAX_UNTRANSLATED_SERVER_MESSAGES})")

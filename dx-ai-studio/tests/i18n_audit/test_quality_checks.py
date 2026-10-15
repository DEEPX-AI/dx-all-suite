"""Translation quality checks above "is every cell filled".

classify.py's base audit reports only two kinds of defects:

    missing-language   the key is empty
    stale-copy         identical to the English text

So "0 findings" means **"the translation table has no empty cells"**, not **"users see
no awkward wording"**. This file adds the defects a machine can still catch:

    terminology drift     the same English translated differently across screens
                          (e.g. Dashboard[zh-CN] 仪表板/仪表盘)
    length overflow       a translation over 2.2x the English, at risk of overflowing the UI
    placeholder mismatch  a translation that drops a {placeholder}

The next layer (are grammar and tone natural?) cannot be judged by a machine and is not
attempted here — checks that pass on awkward copy would give false safety. This file's
job ends at producing a list for native speakers to review.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]



def _rec(en, lang=None, value=None, source_file="a.js", **texts):
    """Build an AuditRecord for a test (it has many required fields)."""
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
        """Short strings such as 'ID' or 'OK' may legitimately differ by context."""
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

    def test_an_error_key_is_not_measured_against_its_message(self):
        """A dictionary entry keyed by an error key ('graph_live_busy') has no English copy of its own: the key is no
        sentence to compare the translated message with."""
        from tools.i18n_audit.classify import classify_length_overflow
        rec = _rec('graph_live_busy', 'es', 'El Graph Composer tiene un en vivo en ejecución; deténgalo primero')
        assert classify_length_overflow([rec]) == []
        rec = _rec('Graph busy', 'es', 'El Graph Composer tiene un en vivo en ejecución; deténgalo primero')
        assert classify_length_overflow([rec]), "copy that only looks short is still measured"

    def test_cjk_is_not_penalised_for_being_short(self):
        """Chinese is **shorter** than English. The length check must not count that as a defect."""
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
    """Pin the measured counts as a contract — a ratchet that only allows going down."""

    # Lower the cap when a fix brings the count down; raising it needs a reason. The cap is
    # what the checker actually counts, not an estimate: it skips abbreviations such as 'ID'
    # and 'FPS' but **includes** one-word terms such as 'Dashboard', because those are the
    # words most likely to drift between screens.
    # What remains needs product decisions — which of two Korean words for "Task" to
    # standardise on, or whether to translate placeholder paths such as /path/to/*.json.
    MAX_TERMINOLOGY_DRIFT = 237
    # **Zero is not the goal.** Most overflows are legitimate translations:
    #   'Inference timed out' -> 'La inferencia agotó el tiempo de espera'
    # Spanish is simply longer, and shortening it would make it worse. Many are error
    # **messages**, not button labels, where length does not matter. Entries keyed by an
    # error key (e.g. 'runner_error', 'live_deps_missing' in dx_app i18n.js) are not measured:
    # the key is no sentence to compare a one-sentence message with.
    # The value of this check is **picking out what is worth a look**, not driving it to 0.
    MAX_LENGTH_OVERFLOW = 14
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
    """English strings the server produces that are shown on screen as-is.

    config_wizard.js does this:

        alert(T('Config generation failed: ') + data.error);

    The prefix is translated, but **the appended data.error stays English**, so a
    Korean user sees a Korean prefix followed by
    "Invalid opt_level: 'abc' — must be one of [0, 1]".

    The translation-table extractor (extractors.py) parses only dict/list literal
    **assignments**, so strings passed as function arguments, such as
    `send_error_json(400, "...")`, are structurally invisible to it. These tests count them.
    """

    # Lower the cap when messages are translated or the scope shrinks. The cap is what the
    # checker counts (f-string literal parts joined), not an estimate.
    # Server code keeps its English messages; the front end translates them just before
    # display (shared/static/server-error-i18n.js). So this cap measures "how many English
    # strings the server has", not "whether users see English" —
    # tests/test_server_error_i18n.py checks the latter.
    #
    # Driving it to 0 is therefore not the goal. It only stops new messages from piling
    # up — a new message needs a matching pattern in server-error-i18n.js.
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
        """Counting every log or exception message would bury the signal — only calls that reach the screen count."""
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

"""Every module's offline assistant answers in all six languages and describes today's screens."""
from __future__ import annotations

import re
from pathlib import Path

from shared.chat import module_fallbacks as mf

ROOT = Path(__file__).resolve().parents[2]
MODULES = ("dx_app", "dx_stream", "dx_modelzoo", "dx_compiler", "dx_planner", "dx_benchmark", "dx_monitor",
           "dx_agent_dev", "dx_edge")


def test_every_module_has_answers_in_all_six_languages():
    assert set(mf.apps()) == set(MODULES)
    for app in MODULES:
        rules = mf.rules(app)
        assert rules, app
        for keywords, answer in rules:
            assert keywords, app
            for lang in mf.LANGS:
                assert answer.get(lang), f"{app} {keywords[0]!r} 에 {lang} 이 없다"


def test_the_answers_do_not_describe_screens_that_are_gone():
    text = repr([mf.rules(a) for a in MODULES])
    for stale in ("Object Detection tab", "Developer tab", "TCO", "340", "Demo tab"):
        assert stale not in text, stale


def test_each_module_uses_the_shared_table():
    for app in MODULES:
        src = (ROOT / app / "server.py").read_text(encoding="utf-8")
        assert f'fallback_rules=_module_fallbacks.rules("{app}")' in src, app


def test_a_japanese_question_gets_a_japanese_answer():
    from shared.chat.fallback import FallbackEngine
    eng = FallbackEngine(app_rules=mf.rules("dx_modelzoo"))
    out = eng.respond("モデルのダウンロード方法は?", lang="ja")["reply"]
    assert re.search(r"[ぁ-んァ-ン]", out) and "Q-Lite" in out


def test_dx_cloud_answers_a_compile_question_with_cloud_compile_not_stack_setup():
    from shared.chat.fallback import FallbackEngine
    eng = FallbackEngine(app_rules=mf.rules("dx_edge"))
    for lang, q in (("en", "How do I compile an ONNX model on my stack?"), ("ko", "스택에서 모델을 컴파일하려면?")):
        out = eng.respond(q, lang=lang)["reply"]
        assert "Upload and compile" in out, (lang, out)
    assert "Check connection" in eng.respond("Which AWS profile does it use?", lang="en")["reply"]

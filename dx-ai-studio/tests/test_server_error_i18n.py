"""English errors produced by the server are translated before they are shown.

Pages display server errors like this:

    alert(T('Config generation failed: ') + data.error);

The prefix is translated, but **the appended data.error is raw English**, so a user
working in another language sees a translated prefix followed by an English sentence:

    <translated prefix>: Invalid opt_level: 'abc' — must be one of [0, 1]

The server call sites are left alone, to avoid touching error-handling paths; the
English→translation step runs **right before display**.

Plain prefix matching only gets half the way — most messages are f-strings with values
**in the middle** (`Invalid opt_level: 'abc' — must be one of [0, 1]`). So the patterns use
capture groups and carry the values over unchanged.

The translated scope is the **input validation messages** — the ones a user sees right
after a bad input. Messages not seen in normal use, such as `Job not found`, stay English.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "shared" / "static" / "server-error-i18n.js"

LANGS = ("ko", "ja", "es", "zh-CN", "zh-TW")


def src() -> str:
    return SRC.read_text(encoding="utf-8")


class TestTheModuleExists:
    def test_the_file_is_there(self):
        assert SRC.is_file(), f"{SRC} 가 없다"

    def test_it_exposes_one_entry_point(self):
        assert "translateServerError" in src()

    def test_it_is_shared_not_per_module(self):
        """Not only dx_compiler shows server errors — it lives in shared/ so other modules
        (dx_agent_dev, dx_benchmark, launcher, shared) use it too."""
        assert SRC.parent.name == "static" and SRC.parent.parent.name == "shared"


class TestPatternsCoverTheValidationMessages:
    """The patterns cover the validation messages the server actually sends."""

    def _patterns(self):
        body = src()
        start = body.index("_SERVER_ERROR_PATTERNS = [")
        end = body.index("\n  ];", start)
        return body[start:end]

    def test_there_are_patterns(self):
        assert self._patterns().count("re:") >= 10, "패턴이 너무 적다"

    def test_every_pattern_has_all_six_languages(self):
        body = self._patterns()
        blocks = re.findall(r"\{\s*re:.*?\n\s*\}", body, re.S)
        assert blocks, "패턴 블록을 못 읽었다"
        missing = []
        for b in blocks:
            for lang in LANGS:
                key = f"'{lang}'" if "-" in lang else lang
                if not re.search(r"(?:'" + re.escape(lang) + r"'|\"" + re.escape(lang)
                                 + r"\"|" + re.escape(lang) + r")\s*:", b):
                    missing.append((b.split("\n")[0][:50], lang))
        assert not missing, f"언어가 빠진 패턴: {missing[:6]}"

    def test_the_fields_users_actually_hit_are_covered(self):
        """Validation messages the config wizard shows routinely."""
        body = self._patterns()
        for token in ("opt_level", "calibration_num", "input_shapes",
                      "preprocessings", "file_extensions", "node names"):
            assert token in body, f"{token} 관련 패턴이 없다"


class TestUnknownMessagesFallThrough:
    """A message missing from the dictionary is shown **as the English original**. Blanking it
    or replacing it with "unknown error" would be worse — the user loses the clue to search for.

    A plain `"return msg" in body` check would pass even with `return ''` added, because of
    another `return msg` elsewhere; the **final path** of the function must be checked.
    """

    def test_the_final_fallback_returns_the_message(self):
        body = src()
        start = body.index("function translateServerError")
        fn = body[start:body.index("\n  }", start)]
        tail = [ln.strip() for ln in fn.splitlines() if ln.strip().startswith("return")]
        assert tail and tail[-1].startswith("return msg"), (
            f"미등록 메시지가 원문으로 나가지 않는다. 마지막 return: {tail[-1:]!r}")

    def test_an_empty_string_is_never_the_fallback(self):
        body = src()
        start = body.index("function translateServerError")
        fn = body[start:body.index("\n  }", start)]
        assert "return '';" not in fn and 'return "";' not in fn, (
            "빈 문자열을 돌려주는 경로가 있다 — 사용자는 오류가 사라진 것으로 본다")


class TestItIsWiredIntoThePagesThatShowServerErrors:
    def test_every_place_that_shows_data_error_passes_it_through(self):
        """A page that skips the wiring stays English. Checks **every line that displays** the
        error, not merely that the function name appears in the file — that weaker check
        misses a call site that bypasses it."""
        import re as _re

        bad = []
        for rel in ("dx_compiler/static/js/config_wizard.js",
                    "dx_compiler/static/js/viewer_panel.js"):
            for i, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
                if not _re.search(r"(alert\(|textContent\s*=).*data\.error", line):
                    continue
                if "_srvErr(" not in line and "translateServerError(" not in line:
                    bad.append(f"{rel}:{i}  {line.strip()[:70]}")
        assert not bad, "서버 오류를 번역 없이 그대로 띄우는 곳:\n  " + "\n  ".join(bad)

    def test_the_compile_progress_box_translates_and_escapes_the_job_error(self):
        """A failed compile / re-quantization job error must be translated and escaped: raw, it
        shows English on a localized page, and markup in a dxcom message would be parsed as HTML."""
        html = (ROOT / "dx_compiler" / "templates" / "index.html").read_text(encoding="utf-8")
        assert "(data.error || 'Unknown error')" not in html
        assert html.count("insertAdjacentHTML('beforeend', _compileJobError(data))") == 2
        helper = html[html.index("function _compileJobError"):]
        helper = helper[:helper.index("}") + 1]
        assert "translateServerError" in helper and "_escErr(" in helper and "T('Unknown error')" in helper

    def test_the_script_is_loaded_by_the_shell(self):
        """Some page must load the script — without it the function is missing and fails silently."""
        hits = [p for p in ROOT.rglob("*.html")
                if ".venv" not in str(p) and "server-error-i18n.js" in p.read_text(encoding="utf-8", errors="ignore")]
        assert hits, "server-error-i18n.js 를 로드하는 페이지가 없다"


class TestThePatternsActuallyMatchWhatTheServerSends:
    """JS cannot run here, so the patterns are ported to Python regexes and matched against
    **real server strings**. If they do not match here, they do not match in the browser.

    Server strings are f-strings with values inside, so the samples fill those values in
    plausibly.
    """

    SAMPLES = [
        # DX Stream runtime contract
        "Runtime contract failed: profile.context",
        "Studio runtime profile is not active and validated.",
        "Run the DX-Runtime Dependencies step in Setup, then try again.",
        "Invalid opt_level: 'abc' — must be one of [0, 1]",
        "Invalid opt_level: empty — must be one of [0, 1]",
        "Invalid calibration_num: -5 — must be a positive number of samples",
        "Invalid calibration_num: True — expected a number",
        "Invalid calibration_num",
        "Invalid calibration_method: '고양이' — must be one of ['ema', 'minmax']",
        "recalibration_method must be one of ['ema', 'iqr', 'minmax']",
        "Invalid input_shapes for 'input.1': -224 — dimensions must be positive integers",
        "Invalid input_shapes for 'input.1': expected a list of dimensions",
        "Invalid input_shapes: expected an object",
        "Invalid preprocessings: expected an array of operations, got dict",
        "Invalid preprocessings[0].normalize.std: contains 0 — normalization divides by std",
        "Invalid preprocessings[0].resize.width: -640 — must be a positive number",
        "Invalid file_extensions: expected a list, got a string. Use ['jpg'], not 'jpg'.",
        "Invalid file_extensions: expected a list, got int",
        "Invalid input_nodes: expected a list of node names, got a string. "
        "A single node must still be a list — use ['ab'], not 'ab'.",
        "Invalid input_nodes: expected a list of node names, got int",
        "Invalid model_path: expected a path string, got int",
        "Invalid enhanced_scheme: not valid JSON — Expecting value",
        "Invalid JSON",
        "Invalid JSON body",
        "Invalid directory path",
        "Unsupported upload file type. Allowed: .json, .onnx",
        "model_path, config_path, and output_dir are required",
        "path parameter required",
        "output_dir is required",
        "temperature must be a number",
        "temperature must be between 0 and 2",
        "model_path is outside the allowed folders",
        "dataset_path (in config) is outside the allowed folders",
        "config_path does not exist",
        "model_path is not a file",
        "dataset_path is not a folder",
        "output_dir is not a valid path",
        "output_dir cannot be a compiler job folder",
        "Host not allowed",
        "Cross-origin request refused",
        # DX-COM's own refusal, shown in the compile progress box (dxcom needs > 8 GB free)
        "Requires available disk size higher than 8 but you have 1.6405487060546875G",
    ]

    @staticmethod
    def _py_patterns():
        """Port JS regex literals to Python regexes. Both are PCRE-like, so the syntax these
        patterns use (`^ $ (.+?) \\( \\)`) carries over unchanged."""
        body = src()
        out = []
        for m in re.finditer(r"re:\s*/\^(.*?)\$/,", body):
            out.append(re.compile("^" + m.group(1) + "$"))
        return out

    def test_the_js_regexes_are_readable(self):
        assert len(self._py_patterns()) >= 30

    def test_every_sample_matches_some_pattern(self):
        pats = self._py_patterns()
        unmatched = [s for s in self.SAMPLES if not any(p.match(s) for p in pats)]
        assert not unmatched, "패턴이 안 무는 실제 서버 메시지:\n  " + "\n  ".join(unmatched)

    # Samples that **two patterns really match**. Order can only be tested with overlapping
    # strings; non-overlapping ones would miss a specific pattern moved to the end.
    OVERLAPPING = [
        ("Invalid opt_level: empty — must be one of [0, 1]", "empty"),
        ("Invalid file_extensions: expected a list, got a string. Use ['jpg'], not 'jpg'.",
         "got a string"),
        ("Invalid input_nodes: expected a list of node names, got a string. "
         "A single node must still be a list — use ['ab'], not 'ab'.", "got a string"),
    ]

    def test_the_more_specific_pattern_is_tried_first(self):
        """Order is everything. A less specific pattern placed first matches first, and the user
        sees a less helpful sentence — e.g. "the opt_level value 'empty' is not allowed" instead
        of "opt_level is empty".
        """
        pats = self._py_patterns()
        for sample, marker in self.OVERLAPPING:
            hits = [i for i, p in enumerate(pats) if p.match(sample)]
            assert len(hits) >= 2, f"겹치는 패턴이 없어졌다 — 이 계약이 무의미해졌다: {sample[:50]}"
            first = pats[hits[0]].pattern
            assert marker in first, (
                f"덜 구체적인 패턴이 먼저 물었다.\n  표본: {sample[:60]}\n"
                f"  먼저 문 것: {first[:80]}\n  기대: {marker!r} 를 포함한 패턴")

    def test_an_unregistered_message_matches_nothing(self):
        """Abnormal paths such as 'Job not found' are not translated — the original must show."""
        pats = self._py_patterns()
        for s in ("Job not found", "Internal server error", "Compilation not complete"):
            assert not any(p.match(s) for p in pats), f"{s!r} 가 패턴에 물렸다"

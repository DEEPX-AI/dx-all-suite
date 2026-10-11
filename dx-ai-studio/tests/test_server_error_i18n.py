"""서버가 만든 영어 오류가 한국어 화면에 그대로 뜨던 것을 번역한다.

config_wizard.js:531 이 이렇게 한다:

    alert(T('Config generation failed: ') + data.error);

앞은 번역되고 **뒤에 붙는 data.error 는 영어 그대로** 다. 한국어로 쓰던
사용자는 이런 문장을 본다:

    설정 생성 실패: Invalid opt_level: 'abc' — must be one of [0, 1]

서버 호출부 92곳은 건드리지 않는다. 오류 처리 경로를 손대는 위험을 피하고,
**표시 직전에** 영어→번역을 통과시킨다.

단순 접두 매칭으로는 반쪽이 된다 — 대부분 f-string 이라 값이 문장 **중간에**
낀다(`Invalid opt_level: 'abc' — must be one of [0, 1]`). 그래서 캡처 그룹이
있는 패턴을 쓰고, 값은 그대로 옮긴다.

번역하는 범위는 **입력 검증 계열 40개** 다(2026-09-21 결정). 사용자가 잘못
입력하면 바로 뜨는 것들이다. `Job not found` 처럼 정상 사용에서 보이지 않는
30개는 영어로 둔다.
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
        """dx_compiler 만의 문제가 아니다 — shared/ 에 둬야 다른 모듈도 쓴다.
        (dx_agent_dev 8건, dx_benchmark 3건, launcher 2건, shared 9건)"""
        assert SRC.parent.name == "static" and SRC.parent.parent.name == "shared"


class TestPatternsCoverTheValidationMessages:
    """서버가 실제로 내는 40개를 패턴이 덮는지 본다."""

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
        """SR-758 작업에서 내가 넣은 검증 메시지들 — 마법사에서 일상적으로 뜬다."""
        body = self._patterns()
        for token in ("opt_level", "calibration_num", "input_shapes",
                      "preprocessings", "file_extensions", "node names"):
            assert token in body, f"{token} 관련 패턴이 없다"


class TestUnknownMessagesFallThrough:
    """사전에 없으면 **영어 원문 그대로** 보여준다. 조용히 비우거나 "알 수 없는
    오류" 로 바꾸면 지금보다 나쁘다 — 사용자가 검색할 단서를 잃는다.

    처음엔 `"return msg" in body` 로 확인했는데, 변이로 `return ''` 을 넣어도
    다른 곳의 `return msg` 때문에 통과했다. 함수의 **마지막 경로** 를 봐야 한다.
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
        """연결을 빠뜨리면 그 화면만 영어로 남는다. 파일에 함수 이름이 있는지가
        아니라 **표시하는 줄마다** 통과시키는지를 본다 — 처음엔 전자로 검사했고,
        호출부를 끊는 변이가 안 잡혔다."""
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
        """A failed compile / re-quantization wrote the job error into the page raw: English on
        a Korean page, and markup in a dxcom message would have been parsed as HTML."""
        html = (ROOT / "dx_compiler" / "templates" / "index.html").read_text(encoding="utf-8")
        assert "(data.error || 'Unknown error')" not in html
        assert html.count("insertAdjacentHTML('beforeend', _compileJobError(data))") == 2
        helper = html[html.index("function _compileJobError"):]
        helper = helper[:helper.index("}") + 1]
        assert "translateServerError" in helper and "_escErr(" in helper and "T('Unknown error')" in helper

    def test_the_script_is_loaded_by_the_shell(self):
        """어느 페이지가 불러오는지 — 로드되지 않으면 함수가 없어 조용히 실패한다."""
        hits = [p for p in ROOT.rglob("*.html")
                if ".venv" not in str(p) and "server-error-i18n.js" in p.read_text(encoding="utf-8", errors="ignore")]
        assert hits, "server-error-i18n.js 를 로드하는 페이지가 없다"


class TestThePatternsActuallyMatchWhatTheServerSends:
    """JS 를 실행할 수 없으므로 패턴을 파이썬 정규식으로 옮겨 **실제 서버 문자열**에
    물려 본다. 여기서 안 물면 브라우저에서도 안 문다.

    서버가 내는 문자열은 f-string 이라 값이 낀다. 그 값을 그럴듯하게 채운
    표본으로 검사한다.
    """

    SAMPLES = [
        # DX Stream 실행 계약 (release audit S-7)
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
        """JS 정규식 리터럴을 파이썬 정규식으로 옮긴다. 둘 다 PCRE 계열이라
        이 패턴들이 쓰는 문법(`^ $ (.+?) \\( \\)`)은 그대로 통한다."""
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

    # 실제로 **두 패턴이 겹치는** 표본. 처음엔 겹치지 않는 문자열로 순서를
    # 검사해서, 구체 패턴을 맨 뒤로 옮기는 변이가 잡히지 않았다.
    OVERLAPPING = [
        ("Invalid opt_level: empty — must be one of [0, 1]", "empty"),
        ("Invalid file_extensions: expected a list, got a string. Use ['jpg'], not 'jpg'.",
         "got a string"),
        ("Invalid input_nodes: expected a list of node names, got a string. "
         "A single node must still be a list — use ['ab'], not 'ab'.", "got a string"),
    ]

    def test_the_more_specific_pattern_is_tried_first(self):
        """순서가 전부다. 덜 구체적인 패턴이 앞에 오면 먼저 물어서, 사용자는
        덜 도움 되는 문장을 본다 — 예를 들어 'opt_level 이 비어 있습니다' 대신
        'opt_level 값 empty 를 쓸 수 없습니다' 가 나온다.
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
        """'Job not found' 같은 비정상 경로는 번역 대상이 아니다 — 원문이 나와야 한다."""
        pats = self._py_patterns()
        for s in ("Job not found", "Internal server error", "Compilation not complete"):
            assert not any(p.match(s) for p in pats), f"{s!r} 가 패턴에 물렸다"

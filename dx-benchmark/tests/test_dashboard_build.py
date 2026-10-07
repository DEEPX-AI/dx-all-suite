"""Tests for dashboard build-time cache-busting (Feature A).

The static dashboard embeds the dataset into index.html and links app.js /
styles.css as separate resources. Without cache-busting, a browser reuses the
cached copies after a rebuild, so a plain reload shows stale data (the reported
"BIOSTAR still visible" confusion). The builder stamps a content hash onto the
asset refs and emits a no-cache meta so a normal reload always reflects a rebuild.
"""
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from benchmark.dashboard_builder import build_static_dashboard
from benchmark.env_fingerprint import _normalize_version
from test_version_resolution import NORMALIZE_CASES

_VER_RE = re.compile(r"(app\.js|styles\.css)\?v=([0-9a-f]{8})\b")
ROOT = Path(__file__).resolve().parents[1]
_EMBEDDED_RE = re.compile(r'id="embedded-dataset"[^>]*>(.*?)</script>', re.S)


def _minimal_dataset(extra_run=None):
    runs = [{"env_id": "hwA", "run_id": "r1", "dx_all_suite_version": "v2.4.0"}]
    if extra_run:
        runs.append(extra_run)
    return {
        "meta": {"generated_at": "2026-07-23"},
        "environments": [{"env_id": "hwA", "latest_run_id": "r1"}],
        "runs": runs,
        "summaries": {"model": [], "e2e_single": [], "e2e_multi_capacity": [], "ort_delta": []},
        "history": {"model": [], "e2e_single": [], "e2e_multi_capacity": []},
        "snapshots": [],
    }


def test_asset_refs_are_cache_busted(tmp_path):
    build_static_dashboard(_minimal_dataset(), tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "__ASSET_VER__" not in html, "build must replace the __ASSET_VER__ token"
    assert re.search(r"app\.js\?v=[0-9a-f]{8}", html), "app.js must carry a ?v=<hash>"
    assert re.search(r"styles\.css\?v=[0-9a-f]{8}", html), "styles.css must carry a ?v=<hash>"


def test_no_cache_meta_present(tmp_path):
    build_static_dashboard(_minimal_dataset(), tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert re.search(r'http-equiv=["\']Cache-Control["\']', html, re.I), \
        "index.html must declare a Cache-Control no-cache meta so a plain reload revalidates"
    assert "no-cache" in html.lower()


def test_asset_version_is_deterministic(tmp_path):
    out1, out2 = tmp_path / "b1", tmp_path / "b2"
    build_static_dashboard(_minimal_dataset(), out1)
    build_static_dashboard(_minimal_dataset(), out2)
    v1 = _VER_RE.search((out1 / "index.html").read_text(encoding="utf-8")).group(2)
    v2 = _VER_RE.search((out2 / "index.html").read_text(encoding="utf-8")).group(2)
    assert v1 == v2, "identical input must yield identical asset hash (no git churn)"


def test_asset_version_tracks_dataset_content(tmp_path):
    out1, out2 = tmp_path / "b1", tmp_path / "b2"
    build_static_dashboard(_minimal_dataset(), out1)
    build_static_dashboard(
        _minimal_dataset(extra_run={"env_id": "hwB", "run_id": "r9", "dx_all_suite_version": "v2.4.0"}),
        out2,
    )
    v1 = _VER_RE.search((out1 / "index.html").read_text(encoding="utf-8")).group(2)
    v2 = _VER_RE.search((out2 / "index.html").read_text(encoding="utf-8")).group(2)
    assert v1 != v2, "changed dataset content must change the asset hash so browsers refetch"


def test_embedded_dataset_preserves_snapshot_protocol(tmp_path):
    """A v2 snapshot's protocol block must survive into the embedded dataset.

    The Version Trend label reads `snap.protocol.version` client-side, so if the
    builder drops the block the label silently degrades to `rt x.y.z` with no
    error anywhere -- exactly the v1/v2 ambiguity this feature exists to remove.
    """
    ds = _minimal_dataset()
    ds["snapshots"] = [{
        "run_id": "r1", "hw_id": "hwA",
        "environment": {"rt_version": "v3.5.0"},
        "protocol": {"version": "v2", "bc_range_lo": 3, "bc_range_hi": 16},
    }]
    build_static_dashboard(ds, tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    embedded = json.loads(_EMBEDDED_RE.search(html).group(1))
    assert embedded["snapshots"][0]["protocol"]["version"] == "v2"


def test_trend_label_reads_protocol_version():
    """`_trendSwLabel` must consult snap.protocol.

    node is unavailable on this host, so this is a source-level guard rather
    than an execution test.
    """
    js = (ROOT / "benchmark" / "dashboard" / "app.js").read_text(encoding="utf-8")
    line = next(l for l in js.split("\n") if "function _trendSwLabel" in l)
    assert "protocol" in line, "_trendSwLabel must read snap.protocol"
    assert "proto " in line, "_trendSwLabel must render a 'proto vN' segment"
    assert "rt " in line, "_trendSwLabel must keep the existing rt segment"


# --- cleanVer <-> _normalize_version parity --------------------------------
#
# `cleanVer` (benchmark/dashboard/app.js) is a SECOND implementation of the
# version-normalization rule that `benchmark/env_fingerprint.py::
# _normalize_version` implements for the stored fingerprint: both drop build
# stamps so two builds of one release stay a single version. Two copies of one
# rule drift -- dx_rt v3.5.0's `(build: 1.d0298f2)` stamp was taught to the
# Python copy first -- so the tests below pin them together.
#
# node is not installed on the dev host, so the always-on parity test does not
# execute the JS: it extracts the `.replace()` chain from app.js and translates
# it to Python. The translation is exact-or-nothing -- `_js_regex_to_python`
# raises on any construct it cannot mirror 1:1, so it can never quietly assert
# an approximation. `test_cleanver_parity_in_real_v8` re-checks the translation
# against a real JS engine wherever headless Chrome is installed.

APP_JS = ROOT / "benchmark" / "dashboard" / "app.js"

# JS \s is ECMA-262 WhiteSpace + LineTerminator; Python's \s omits U+FEFF.
_JS_SPACE = " \\t\\n\\v\\f\\r\\u00a0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000\\ufeff"
# JS '.' excludes all four line terminators; Python's '.' excludes only \n.
_JS_DOT = "[^\\n\\r\\u2028\\u2029]"
_LITERAL_ESCAPES = set(".+*?()[]{}|^$/\\-")

_REPLACE_RE = re.compile(
    r"\.replace\(\s*/((?:[^/\\]|\\.)+)/([a-z]*)\s*,\s*'((?:[^'\\]|\\.)*)'\s*\)"
)


def _js_regex_to_python(body, flags):
    """Translate a JS regex literal body to an equivalent Python pattern.

    Exact or nothing: every construct whose Python meaning differs from its JS
    meaning is rewritten (`$`/`^` are absolute anchors in JS, `\\d` is ASCII-only,
    `\\s` includes U+FEFF, `.` excludes all four line terminators), and anything
    outside the understood subset raises. A silent approximation here would make
    the parity test look stronger than it is.
    """
    if set(flags) - {"i"}:
        raise AssertionError("cannot mirror JS regex flags %r (only 'i')" % flags)
    out, i, n, in_class = [], 0, len(body), False
    while i < n:
        c = body[i]
        if c == "\\":
            if i + 1 >= n:
                raise AssertionError("trailing backslash in /%s/" % body)
            e = body[i + 1]
            i += 2
            if e == "d":
                out.append("0-9" if in_class else "[0-9]")
            elif e == "s":
                out.append(_JS_SPACE if in_class else "[" + _JS_SPACE + "]")
            elif e == "w":
                out.append("A-Za-z0-9_" if in_class else "[A-Za-z0-9_]")
            elif e in _LITERAL_ESCAPES:
                out.append("\\" + e)
            else:
                raise AssertionError("cannot mirror JS escape \\%s in /%s/" % (e, body))
            continue
        if in_class:
            out.append(c)
            in_class = c != "]"
            i += 1
            continue
        if c == "[":
            in_class = True
        elif body.startswith("(?<", i):
            raise AssertionError("cannot mirror lookbehind/named group in /%s/" % body)
        elif c == "$":
            out.append("\\Z")
            i += 1
            continue
        elif c == "^":
            out.append("\\A")
            i += 1
            continue
        elif c == ".":
            out.append(_JS_DOT)
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _cleanver_line():
    js = APP_JS.read_text(encoding="utf-8")
    return next(l for l in js.split("\n") if "function cleanVer(" in l)


def _extract_replace_chain(line):
    steps = _REPLACE_RE.findall(line)
    assert steps, "no .replace() chain found in cleanVer"
    assert line.count(".replace(") == len(steps), (
        "cleanVer contains a .replace() call this test could not parse -- "
        "the parity check would silently skip it"
    )
    return steps


def _translated_cleanver():
    """A Python callable behaving as the cleanVer currently written in app.js."""
    compiled = []
    for body, flags, repl in _extract_replace_chain(_cleanver_line()):
        assert "$" not in repl, "cannot mirror JS $-substitution in replacement %r" % repl
        compiled.append((re.compile(_js_regex_to_python(body, flags),
                                    re.I if "i" in flags else 0), repl))

    def run(value):
        if not isinstance(value, str):
            return value  # mirrors: if (typeof v !== 'string') return v
        for rx, repl in compiled:
            value = rx.sub(repl, value, count=1)  # no /g flag = first match only
        return value

    return run


def _python_display_version(raw):
    """What `cleanVer` must return, derived from the Python rule.

    `cleanVer` renders for display, so on top of the shared rule it drops two
    purely presentational things: the `DXRT ` banner prefix (which the Python
    path strips upstream, in `_get_dxrt_version`) and the leading `v`. Every
    other transformation must agree, and that is what parity means here.
    """
    s = re.sub(r"\ADXRT\s+", "", raw, count=1, flags=re.I)
    s = _normalize_version(s)
    return re.sub(r"\Av(?=[0-9])", "", s, count=1, flags=re.I)


def _in_contract(raw):
    """Shapes the fingerprint can actually record: single-line and trimmed.

    `_get_dxrt_version` keeps line 1 only and `_normalize_version` trims, so no
    padded or multi-line value ever reaches the dataset that `cleanVer` reads.
    The two copies genuinely diverge outside that domain (JS `$` is absolute-end
    where Python's also matches before a trailing newline, and JS does not trim),
    so asserting parity there would be asserting something untrue.
    """
    return raw == raw.strip() and "\n" not in raw and "\r" not in raw


# Driven by the Python rule's own case table, so a case added there is
# automatically required of the JS copy too.
_PARITY_CORPUS = [raw for raw, _expected in NORMALIZE_CASES if _in_contract(raw)] + [
    "DXRT v3.5.0 (build: 1.d0298f2)",  # full banner: only the display side sees this
    "DXRT v3.4.0+fad14d6",             # the v3.4.0 banner it must keep handling
    "v3.5.0 (build: 1+2.d0298f2)",     # '+' inside the stamp: pins the strip ORDER
]


def test_cleanver_strips_paren_build_stamp():
    """`cleanVer` must drop a trailing '(build: ...)' stamp, before the '+' strip.

    dx_rt v3.5.0 reports `DXRT v3.5.0 (build: 1.d0298f2)`; without this, two
    builds of one release render as two versions in the Version Trend chart.
    node is unavailable on this host, so this is a source-level guard, in the
    same style as `test_trend_label_reads_protocol_version`.
    """
    steps = [body for body, _flags, _repl in _extract_replace_chain(_cleanver_line())]
    assert r"\s*\([^)]*\)$" in steps, (
        "cleanVer must strip a trailing parenthesised build stamp, matching "
        "_normalize_version in benchmark/env_fingerprint.py"
    )
    assert steps.index(r"\s*\([^)]*\)$") < steps.index(r"\+.*$"), (
        "the paren strip must run BEFORE the '+' strip: a stamp body containing "
        "'+' would otherwise be cut mid-parenthesis, leaving no ')' for the "
        "')$'-anchored strip to match, and the residue would survive"
    )


def test_cleanver_parity_with_python_normalize_version():
    """The two implementations of the rule must agree, case for case.

    This is the guard against the copies drifting: it reads the live regex chain
    out of app.js, so changing either side without the other turns it red.
    """
    # The case the whole fix exists for must survive the in-contract filter.
    assert "v3.5.0 (build: 1.d0298f2)" in _PARITY_CORPUS
    clean_ver = _translated_cleanver()
    mismatches = [
        (raw, clean_ver(raw), _python_display_version(raw))
        for raw in _PARITY_CORPUS
        if clean_ver(raw) != _python_display_version(raw)
    ]
    assert not mismatches, "cleanVer (app.js) and _normalize_version disagree:\n" + "\n".join(
        "  %r -> js %r != python %r" % m for m in mismatches
    )


def test_cleanver_ignores_non_strings():
    """The `typeof v !== 'string'` guard: a missing field passes straight through."""
    clean_ver = _translated_cleanver()
    for value in (None, 42, True, {}, []):
        assert clean_ver(value) is value


def _chrome():
    for exe in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(exe)
        if found:
            return found
    return None


def _run_cleanver_in_chrome(chrome, tmp_path, inputs):
    """Call the real cleanVer in headless Chrome; None if the browser cannot run."""
    page = tmp_path / "harness.html"
    page.write_text(
        '<!doctype html><body><pre id="out"></pre>\n'
        '<script src="file://%s"></script>\n<script>\n'
        "var M = String.fromCharCode(2);\nvar CASES = %s;\nvar res = [], err = null;\n"
        "try { for (var i = 0; i < CASES.length; i++) res.push(cleanVer(CASES[i])); }\n"
        "catch (e) { err = String(e); }\n"
        "document.getElementById('out').textContent =\n"
        "  M + JSON.stringify({fn: typeof cleanVer, err: err, res: res}) + M;\n"
        "</script></body>" % (APP_JS, json.dumps(inputs)),
        encoding="utf-8",
    )
    try:
        dom = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--allow-file-access-from-files", "--virtual-time-budget=5000",
             "--user-data-dir=%s" % (tmp_path / "profile"),
             "--dump-dom", "file://%s" % page],
            capture_output=True, text=True, timeout=120,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    found = re.search("\x02(.*?)\x02", dom, re.S)
    if not found:
        return None  # browser present but sandboxed/unable to render: not a failure
    payload = json.loads(html.unescape(found.group(1)))
    if payload["fn"] != "function" or payload["err"]:
        return None
    return payload["res"]


@pytest.mark.skipif(_chrome() is None, reason="no Chrome/Chromium to execute app.js")
@pytest.mark.skipif(sys.platform == "win32", reason="file:// harness is POSIX-only here")
def test_cleanver_parity_in_real_v8(tmp_path):
    """Same parity, but running the real app.js in a real JS engine.

    The translation in `_translated_cleanver` is a stand-in for an engine, so
    where one is actually installed this checks both that the engine agrees with
    the Python rule AND that the stand-in agrees with the engine -- which is what
    keeps the always-on test above honest. Skipped, not failed, when no browser
    is available, so it never becomes the only thing holding the line.
    """
    actual = _run_cleanver_in_chrome(_chrome(), tmp_path, _PARITY_CORPUS)
    if actual is None:
        pytest.skip("Chrome present but could not execute the harness")
    translated = _translated_cleanver()
    for raw, got in zip(_PARITY_CORPUS, actual):
        assert got == _python_display_version(raw), (
            "real cleanVer(%r) = %r, but the Python rule says %r" % (raw, got, _python_display_version(raw))
        )
        assert got == translated(raw), (
            "the JS-to-Python translation is unfaithful for %r: engine %r != translated %r"
            % (raw, got, translated(raw))
        )

"""scripts/acceptance.py — the SQA acceptance runner: selection, manifest schema, and its reports."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("acceptance_runner", ROOT / "scripts" / "acceptance.py")
acc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(acc)

MANIFEST = acc.load_manifest()
KEYS = [t["key"] for t in MANIFEST["tickets"]]


# --- selection ---------------------------------------------------------------------------------

def _keys(spec):
    return [t["key"] for t in acc.select(MANIFEST, spec)]


def test_all_selects_every_ticket_in_manifest_order():
    assert _keys("all") == KEYS
    assert _keys("ALL") == KEYS


def test_a_ticket_is_selected_by_key_number_or_alias():
    assert _keys("SDKREQ-474") == ["SDKREQ-474"]
    assert _keys("sdkreq-474") == ["SDKREQ-474"]
    assert _keys("474") == ["SDKREQ-474"]
    assert _keys("app") == ["SDKREQ-474"]
    assert _keys("cloud") == ["SDKREQ-710"]


def test_a_comma_list_is_deduplicated_and_kept_in_manifest_order():
    assert _keys("stream, 473 ,launcher,i18n") == ["SDKREQ-473", "SDKREQ-475", "SDKREQ-483"]


@pytest.mark.parametrize("spec", ["", "999", "SDKREQ-999", "nope", "app,nope"])
def test_an_unknown_or_empty_selection_is_refused(spec):
    with pytest.raises(acc.SelectionError):
        acc.select(MANIFEST, spec)


def test_every_alias_the_brief_names_exists():
    aliases = {t["alias"] for t in MANIFEST["tickets"]}
    assert {"launcher", "app", "stream", "agent", "zoo", "compiler", "edgeguide", "monitor", "benchmark", "boot",
            "i18n", "sdklib", "toolbar", "tutorial"} <= aliases


# --- manifest ----------------------------------------------------------------------------------

def test_the_manifest_is_well_formed():
    assert acc.validate_manifest(MANIFEST) == []


def test_the_schema_check_catches_what_it_should():
    bad = {"tickets": [{"key": "X-1", "alias": "x", "title": "t", "testrail": None, "ac": [
        {"id": "1-AC1", "title": "", "requires": ["gpu"], "tests": []},
        {"id": "1-AC1", "title": "t", "requires": [], "tests": ["not a node id"]}]}]}
    problems = "\n".join(acc.validate_manifest(bad))
    for needle in ("no title", "requires must be", "at least one test", "duplicated", "node ids"):
        assert needle in problems, needle


def test_jira_tickets_carry_their_testrail_case():
    # SDKREQ-473..486 have TestRail cases C18231..C18244; a ticket created later (SDKREQ-710, DX Cloud) has none yet.
    for t in MANIFEST["tickets"]:
        n = acc.ticket_number(t["key"])
        if n and 473 <= int(n) <= 486:
            assert t["testrail"] == f"C{18231 + int(n) - 473}", t["key"]
        else:
            assert t["testrail"] is None, t["key"]


def test_every_mapped_test_exists_and_is_collected():
    files = sorted({node.split("::", 1)[0] for t in MANIFEST["tickets"] for a in t["ac"] for node in a["tests"]})
    for f in files:
        assert (ROOT / f).is_file(), f
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *files],
                         cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    collected = {line.strip() for line in out.stdout.splitlines() if "::" in line}
    missing = []
    for t in MANIFEST["tickets"]:
        for a in t["ac"]:
            for node in a["tests"]:
                if node not in collected and not any(c.startswith(node + "[") for c in collected):
                    missing.append(f"{a['id']}: {node}")
    assert not missing, "\n".join(missing) + "\n" + out.stdout[-2000:]


# --- statuses, plan and reports ---------------------------------------------------------------

HW = {"npu": (True, "DXRT v3.5.0"), "camera": (False, "no camera (/dev/video* missing)"), "dx_com": (True, "dx_com"),
      "llm": (False, "no LLM configured"), "aws": (False, "no AWS credentials"), "browser": (True, "chromium")}


def _ac(tests, requires=()):
    return {"id": "9-AC1", "title": "t", "requires": list(requires), "tests": tests}


def test_status_is_pass_fail_or_not_run():
    rec = {"t::a": {"nodeid": "t::a", "outcome": "passed", "duration": 1.0},
           "t::b[x]": {"nodeid": "t::b[x]", "outcome": "passed", "duration": 2.0},
           "t::b[y]": {"nodeid": "t::b[y]", "outcome": "failed", "duration": 0.5, "reason": "E   boom"},
           "t::c": {"nodeid": "t::c", "outcome": "skipped", "duration": 0.0, "reason": "Skipped: NOT RUN: no stream models"}}
    assert acc.ac_status(_ac(["t::a"]), HW, rec)["status"] == acc.PASS
    st = acc.ac_status(_ac(["t::a", "t::b"]), HW, rec)
    assert st["status"] == acc.FAIL and "boom" in st["reason"] and st["duration"] == 3.5
    st = acc.ac_status(_ac(["t::a", "t::c"]), HW, rec)
    assert st["status"] == acc.NOT_RUN and st["reason"] == "no stream models"
    st = acc.ac_status(_ac(["t::a"], ["camera", "npu"]), HW, rec)
    assert st["status"] == acc.NOT_RUN and "no camera" in st["reason"]
    assert acc.ac_status(_ac(["t::zzz"]), HW, rec)["status"] == acc.FAIL, "a test that did not run is a failure"


def test_the_plan_runs_each_file_once_and_skips_ac_the_machine_cannot_run():
    tickets = [{"key": "A", "ac": [_ac(["f1.py::a", "f2.py::b"]), _ac(["f3.py::c"], ["camera"])]},
               {"key": "B", "ac": [_ac(["f1.py::a", "f1.py::d"])]}]
    assert acc.plan(tickets, HW) == [("A", "f1.py", ["f1.py::a"]), ("A", "f2.py", ["f2.py::b"]),
                                     ("B", "f1.py", ["f1.py::d"])]


def test_reports_carry_results_times_environment_and_testrail_ids(tmp_path):
    tickets = [{"key": "SDKREQ-473", "alias": "launcher", "title": "[Launcher] 진입", "testrail": "C18231", "ac": [
                   {"id": "473-AC1", "title": "배너", "requires": [], "tests": ["t::a"]},
                   {"id": "473-AC2", "title": "인트로", "requires": [], "tests": ["t::b"]},
                   {"id": "473-AC3", "title": "카메라", "requires": ["camera"], "tests": ["t::c"]}]},
               {"key": "DXCLOUD", "alias": "cloud", "title": "[DX Cloud]", "testrail": None, "ac": [
                   {"id": "DXCLOUD-AC1", "title": "탭", "requires": [], "tests": ["t::a"]}]}]
    rec = {"t::a": {"nodeid": "t::a", "outcome": "passed", "duration": 1.25},
           "t::b": {"nodeid": "t::b", "outcome": "failed", "duration": 2.0, "reason": "E   AssertionError: no splash"}}
    results = acc.build_results(tickets, HW, rec, {"SDKREQ-473": 61.0, "DXCLOUD": 5.0})
    env = {**acc.environment(HW), "when": "2026-10-16T12:00:00"}
    acc.write_markdown(tmp_path / "report.md", results, env, 66.0)
    acc.write_html(tmp_path / "report.html", results, env, 66.0)
    acc.write_junit(tmp_path / "junit.xml", results, env)

    md = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "2 PASS · 1 FAIL · 1 NOT RUN" in md.replace("**", "")
    assert "no splash" in md and "no camera" in md and "1m01s" in md and "DXRT v3.5.0" in md
    html = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert "<title>" in html and "C18231" in html and "NOT RUN" in html

    root = ET.parse(tmp_path / "junit.xml").getroot()
    suites = root.findall("testsuite")
    assert [s.get("name").split()[0] for s in suites] == ["SDKREQ-473", "DXCLOUD"]
    s473 = suites[0]
    assert s473.get("tests") == "3" and s473.get("failures") == "1" and s473.get("skipped") == "1"
    assert {p.get("name"): p.get("value") for p in s473.find("properties")}["testrail_case_id"] == "C18231"
    cases = s473.findall("testcase")
    assert cases[0].get("name").startswith("[C18231] 473-AC1")
    assert {p.get("name"): p.get("value") for p in cases[0].find("properties")}["test_id"] == "C18231"
    assert cases[1].find("failure") is not None and cases[2].find("skipped") is not None
    assert not suites[1].find("testcase").get("name").startswith("["), "no TestRail case yet: no [C…] prefix"


def test_list_prints_tickets_ac_and_tests():
    text = acc.list_text(acc.select(MANIFEST, "485"))
    assert "SDKREQ-485" in text and "485-AC5" in text and "[llm,browser]" in text
    assert "tests/acceptance/test_sdkreq_485_toolbar_chat.py::" in text


def test_list_from_the_command_line_runs_nothing(tmp_path):
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "acceptance.py"), "cloud", "--list"],
                         cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert out.returncode == 0 and "SDKREQ-710" in out.stdout and "SDKREQ-473" not in out.stdout
    bad = subprocess.run([sys.executable, str(ROOT / "scripts" / "acceptance.py"), "nope", "--list"],
                         cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert bad.returncode == 2 and "unknown ticket or alias" in bad.stderr


def test_run_ci_runs_only_the_acceptance_selection_when_asked():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "--acceptance=*) ACCEPTANCE=" in script and "--strict)" in script and "--list)" in script
    hand_off = script.index('exec "$PY" scripts/acceptance.py "$ACCEPTANCE"')
    assert hand_off < script.index("== CSS token ratchet =="), "acceptance must not run the developer stages"


def test_tests_an_early_stop_never_reached_are_not_run_with_the_reason():
    rec = {"t::a": {"nodeid": "t::a", "outcome": "passed", "duration": 1.0}}
    st = acc.ac_status(_ac(["t::a", "t::b"]), HW, rec, stopped="run stopped early: only 300 MB free disk")
    assert st["status"] == acc.NOT_RUN and "300 MB" in st["reason"]


def test_preflight_stops_a_browser_run_without_playwright_or_chromium():
    tickets = acc.select(MANIFEST, "473")
    no_pw = acc.preflight(tickets, {"browser": (False, "playwright not installed")}, python="PY")
    assert len(no_pw) == 1 and "Playwright is not installed" in no_pw[0]
    assert "PY -m pip install -r requirements-ci.txt" in no_pw[0]
    no_chrome = acc.preflight(tickets, {"browser": (False, "no chromium for Playwright")}, python="PY")
    assert len(no_chrome) == 1 and "PY -m playwright install chromium" in no_chrome[0]
    assert acc.preflight(tickets, {"browser": (True, "chromium /usr/bin/google-chrome")}) == []


def test_preflight_lets_a_run_without_browser_ac_through():
    tickets = [{"key": "X", "ac": [{"id": "X-AC1", "requires": [], "tests": ["t::a"]}]}]
    assert acc.preflight(tickets, {"browser": (False, "playwright not installed")}) == []

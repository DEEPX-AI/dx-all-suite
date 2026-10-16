#!/usr/bin/env python3
"""DX AI Studio acceptance (SQA) runner: one command per Jira acceptance ticket.

    bash scripts/run_ci.sh --acceptance=all               # every ticket
    bash scripts/run_ci.sh --acceptance=474,stream        # a ticket number and an alias
    bash scripts/run_ci.sh --acceptance=all --list        # tickets, AC and mapped tests
    bash scripts/run_ci.sh --acceptance=SDKREQ-482 --strict   # NOT RUN counts as a failure

tests/acceptance/manifest.json maps ticket -> AC -> pytest node ids. Each AC lists what it needs
(npu, camera, dx_com, llm, aws, browser); tests/acceptance/hardware.py detects them, and an AC whose
needs are missing is NOT RUN with the reason, never a silent pass. Every test file runs in its own
pytest process (sync Playwright owns one event loop per process). The report goes to
var/acceptance/<timestamp>/: report.md, report.html, junit.xml (TestRail case ids) and results.json.

Exit 0 only when every AC that ran passed; --strict also fails on NOT RUN. Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tests" / "acceptance" / "manifest.json"
REQUIREMENTS = ("npu", "camera", "dx_com", "llm", "aws", "browser")
PASS, FAIL, NOT_RUN = "PASS", "FAIL", "NOT RUN"
MIN_FREE_MB = 450           # stop before the board's disk fills up
PROCESS_TIMEOUT = 1800


class SelectionError(ValueError):
    pass


# --- manifest -------------------------------------------------------------------------------

def load_manifest(path: Path = MANIFEST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> list[str]:
    """Schema problems as readable strings (empty when the manifest is well formed)."""
    problems = []
    keys, aliases, ac_ids = set(), set(), set()
    tickets = manifest.get("tickets")
    if not isinstance(tickets, list) or not tickets:
        return ["manifest has no tickets"]
    for t in tickets:
        key = t.get("key")
        if not key or key in keys:
            problems.append(f"ticket key missing or duplicated: {key!r}")
        keys.add(key)
        alias = t.get("alias")
        if not alias or alias in aliases:
            problems.append(f"{key}: alias missing or duplicated: {alias!r}")
        aliases.add(alias)
        for field in ("title", "testrail"):
            if field not in t:
                problems.append(f"{key}: no {field!r} (use null for a ticket without a TestRail case yet)")
        acs = t.get("ac") or []
        if not acs:
            problems.append(f"{key}: no AC")
        for ac in acs:
            aid = ac.get("id")
            if not aid or aid in ac_ids:
                problems.append(f"{key}: AC id missing or duplicated: {aid!r}")
            ac_ids.add(aid)
            if not str(ac.get("title") or "").strip():
                problems.append(f"{aid}: no title")
            req = ac.get("requires")
            if not isinstance(req, list) or any(r not in REQUIREMENTS for r in req):
                problems.append(f"{aid}: requires must be a list of {REQUIREMENTS}, got {req!r}")
            tests = ac.get("tests")
            if not isinstance(tests, list) or not tests:
                problems.append(f"{aid}: needs at least one test")
            elif any("::" not in str(x) or not str(x).startswith("tests/") for x in tests):
                problems.append(f"{aid}: tests must be pytest node ids under tests/: {tests}")
    return problems


def ticket_number(key: str) -> str | None:
    tail = key.rsplit("-", 1)[-1]
    return tail if tail.isdigit() else None


def select(manifest: dict, spec: str) -> list[dict]:
    """Tickets named by ``spec``: all, keys (SDKREQ-474 / 474), aliases, comma-separated; manifest order."""
    tickets = manifest["tickets"]
    tokens = [s.strip() for s in (spec or "").split(",") if s.strip()]
    if not tokens:
        raise SelectionError("empty selection")
    chosen = set()
    for tok in tokens:
        low = tok.lower()
        if low == "all":
            chosen.update(t["key"] for t in tickets)
            continue
        hit = [t["key"] for t in tickets
               if low in (t["key"].lower(), str(t.get("alias", "")).lower()) or low == ticket_number(t["key"])]
        if not hit:
            names = ", ".join(f"{t['key']}({t['alias']})" for t in tickets)
            raise SelectionError(f"unknown ticket or alias {tok!r}; known: all, {names}")
        chosen.update(hit)
    return [t for t in tickets if t["key"] in chosen]


def list_text(tickets: list[dict]) -> str:
    out = []
    for t in tickets:
        out.append(f"{t['key']}  ({t['alias']}, TestRail {t.get('testrail') or '-'})  {t['title']}")
        for ac in t["ac"]:
            req = ",".join(ac["requires"]) or "-"
            out.append(f"  {ac['id']:<12} [{req}] {ac['title']}")
            for node in ac["tests"]:
                out.append(f"      {node}")
    return "\n".join(out)


# --- running ----------------------------------------------------------------------------------

def _python() -> str:
    exe = os.environ.get("VENV_PYTHON") or str(ROOT / ".venv" / "bin" / "python")
    return exe if Path(exe).exists() else sys.executable


def _free_mb() -> float:
    return shutil.disk_usage(str(ROOT)).free / 1e6


def _match(records: dict, node: str):
    """Records for a manifest node id: exact, or every parametrisation of it."""
    if node in records:
        return [records[node]]
    return [r for nid, r in records.items() if nid.startswith(node + "[")]


def ac_status(ac: dict, hw: dict, records: dict, stopped: str = "") -> dict:
    """PASS / FAIL / NOT RUN for one AC. ``stopped``: why the run ended early; tests it never reached are NOT RUN."""
    missing = [r for r in ac["requires"] if not hw.get(r, (False, ""))[0]]
    if missing:
        return {"status": NOT_RUN, "reason": "; ".join(hw[r][1] for r in missing), "duration": 0.0, "tests": []}
    tests, status, reasons, duration = [], PASS, [], 0.0
    for node in ac["tests"]:
        recs = _match(records, node)
        if not recs and stopped:
            tests.append({"nodeid": node, "outcome": "skipped", "reason": stopped})
            if status == PASS:
                status = NOT_RUN
            reasons.append(stopped)
            continue
        if not recs:
            tests.append({"nodeid": node, "outcome": "missing", "reason": "test did not run"})
            status = FAIL
            reasons.append(f"{node}: did not run (not collected, or its process crashed)")
            continue
        for r in recs:
            duration += r.get("duration", 0.0)
            tests.append(r)
            if r["outcome"] in ("failed", "error"):
                status = FAIL
                reasons.append(f"{r['nodeid'].split('::')[-1]}: {r.get('reason', '')}".strip())
            elif r["outcome"] == "skipped" and status == PASS:
                status = NOT_RUN
                reasons.append(re.sub(r"^(Skipped: )?(NOT RUN: )?", "", r.get("reason") or "skipped"))
    if status == PASS:
        reasons = []
    elif status == FAIL:
        reasons = [x for x in reasons if x]
    return {"status": status, "reason": "\n".join(dict.fromkeys(reasons)), "duration": duration, "tests": tests}


def plan(tickets: list[dict], hw: dict) -> list[tuple[str, str, list[str]]]:
    """(ticket key, test file, node ids) per pytest process; a node already planned is not run twice."""
    seen, out = set(), []
    for t in tickets:
        by_file: dict[str, list[str]] = {}
        for ac in t["ac"]:
            if any(not hw.get(r, (False, ""))[0] for r in ac["requires"]):
                continue
            for node in ac["tests"]:
                if node in seen:
                    continue
                seen.add(node)
                by_file.setdefault(node.split("::", 1)[0], []).append(node)
        out.extend((t["key"], f, nodes) for f, nodes in by_file.items())
    return out


def run_process(nodes: list[str], outcomes: Path, artifacts: Path, tmp_root: Path, log: Path) -> tuple[int, float]:
    env = {**os.environ,
           "DX_ACCEPT_OUTCOMES": str(outcomes), "DX_ACCEPT_ARTIFACTS": str(artifacts),
           "DX_ACCEPT_TMP": str(tmp_root),
           # The suite's conftest points chat settings at a temp dir; keep the real one reachable.
           "DX_ACCEPT_REAL_CHAT_CONFIG_DIR": os.environ.get("DX_CHAT_CONFIG_DIR")
           or str(Path.home() / ".dx-ai-studio")}
    basetemp = Path(tempfile.mkdtemp(prefix="pytest-", dir=str(tmp_root)))
    cmd = [_python(), "-m", "pytest", *nodes, "-q", "--tb=short", "-p", "no:cacheprovider",
           "-p", "tests.acceptance.outcomes_plugin", f"--basetemp={basetemp}"]
    start = time.monotonic()
    with open(log, "wb") as fh:
        fh.write((" ".join(cmd) + "\n").encode())
        try:
            code = subprocess.run(cmd, cwd=str(ROOT), env=env, stdout=fh, stderr=subprocess.STDOUT,
                                  timeout=PROCESS_TIMEOUT).returncode
        except subprocess.TimeoutExpired:
            code = -1
            fh.write(f"\nTIMEOUT after {PROCESS_TIMEOUT}s\n".encode())
    shutil.rmtree(basetemp, ignore_errors=True)
    return code, time.monotonic() - start


def read_outcomes(path: Path) -> dict:
    records = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                records[rec["nodeid"]] = rec
    return records


# --- reports ----------------------------------------------------------------------------------

def _fmt_s(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60}m{sec % 60:02d}s" if sec >= 60 else f"{sec}s"


def environment(hw: dict) -> dict:
    def ver(path):
        try:
            return (ROOT / path).read_text(encoding="utf-8").strip()
        except OSError:
            return "?"
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        head = "?"
    return {"host": platform.node(), "os": platform.platform(), "python": platform.python_version(),
            "studio": ver("release.ver"), "suite": ver("../release.ver"), "git": head,
            "hardware": {k: {"available": v[0], "detail": v[1]} for k, v in hw.items()}}


def summarize(results: list[dict]) -> dict:
    total = {PASS: 0, FAIL: 0, NOT_RUN: 0}
    for t in results:
        for ac in t["ac"]:
            total[ac["status"]] += 1
    return total


def write_markdown(path: Path, results: list[dict], env: dict, wall: float) -> None:
    tot = summarize(results)
    lines = ["# DX AI Studio acceptance report", "",
             f"- When: {env['when']}  ·  wall time {_fmt_s(wall)}",
             f"- Studio {env['studio']} · suite {env['suite']} · git {env['git']} · {env['host']} · "
             f"Python {env['python']}",
             f"- Result: **{tot[PASS]} PASS · {tot[FAIL]} FAIL · {tot[NOT_RUN]} NOT RUN**",
             *([f"- **INCOMPLETE**: {env['stopped']}"] if env.get("stopped") else []), "",
             "## Environment", "", "| Needs | Available | Detail |", "|---|---|---|"]
    for k, v in env["hardware"].items():
        lines.append(f"| {k} | {'yes' if v['available'] else 'no'} | {v['detail']} |")
    lines += ["", "## Tickets", "", "| Ticket | TestRail | PASS | FAIL | NOT RUN | Time |", "|---|---|---|---|---|---|"]
    for t in results:
        c = {s: sum(1 for a in t["ac"] if a["status"] == s) for s in (PASS, FAIL, NOT_RUN)}
        lines.append(f"| {t['key']} {t['title']} | {t.get('testrail') or '-'} | {c[PASS]} | {c[FAIL]} | "
                     f"{c[NOT_RUN]} | {_fmt_s(t['wall'])} |")
    for t in results:
        lines += ["", f"## {t['key']} {t['title']}  ({t.get('testrail') or 'no TestRail case'}, "
                      f"{_fmt_s(t['wall'])})", "", "| AC | Result | Time | Detail |", "|---|---|---|---|"]
        for a in t["ac"]:
            detail = a["reason"].replace("\n", "<br>").replace("|", "\\|") if a["reason"] else ""
            tests = "<br>".join(f"`{n}`" for n in a["tests_listed"])
            lines.append(f"| **{a['id']}** {a['title']} | {a['status']} | {_fmt_s(a['duration'])} | "
                         f"{detail}{'<br>' if detail else ''}{tests} |")
    lines += ["", "NOT RUN = the AC needs something this machine does not have (shown in Detail); "
                  "it is neither a pass nor a failure unless run with --strict.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html(path: Path, results: list[dict], env: dict, wall: float) -> None:
    tot = summarize(results)
    e = html.escape
    rows = []
    for t in results:
        rows.append(f"<h2>{e(t['key'])} {e(t['title'])} <small>{e(t.get('testrail') or 'no TestRail case')} · "
                    f"{_fmt_s(t['wall'])}</small></h2><table><tr><th>AC</th><th>Result</th><th>Time</th>"
                    "<th>Detail</th></tr>")
        for a in t["ac"]:
            cls = {PASS: "pass", FAIL: "fail", NOT_RUN: "notrun"}[a["status"]]
            tests = "".join(f"<div><code>{e(n)}</code></div>" for n in a["tests_listed"])
            reason = f"<pre>{e(a['reason'])}</pre>" if a["reason"] else ""
            rows.append(f"<tr><td><b>{e(a['id'])}</b> {e(a['title'])}</td><td class='{cls}'>{a['status']}</td>"
                        f"<td>{_fmt_s(a['duration'])}</td><td>{reason}{tests}</td></tr>")
        rows.append("</table>")
    hw = "".join(f"<tr><td>{e(k)}</td><td>{'yes' if v['available'] else 'no'}</td><td>{e(v['detail'])}</td></tr>"
                 for k, v in env["hardware"].items())
    doc = f"""<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Studio acceptance report</title>
<style>
:root{{--bg:#fff;--fg:#1b1f24;--muted:#5b6470;--line:#d8dde3;--pass:#1a7f37;--fail:#cf222e;--nr:#9a6700}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e6edf3;--muted:#9da7b3;--line:#30363d;
--pass:#3fb950;--fail:#ff7b72;--nr:#d29922}}}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1200px;
padding:16px}}
table{{border-collapse:collapse;width:100%;margin:8px 0 20px}}td,th{{border:1px solid var(--line);padding:6px 8px;
vertical-align:top;text-align:left}}small{{color:var(--muted);font-weight:400}}code,pre{{font-size:12px;
white-space:pre-wrap;word-break:break-all;margin:0}}.pass{{color:var(--pass);font-weight:700}}
.fail{{color:var(--fail);font-weight:700}}.notrun{{color:var(--nr);font-weight:700}}
</style>
<h1>DX AI Studio acceptance report</h1>
<p>{e(env['when'])} · wall time {_fmt_s(wall)} · Studio {e(env['studio'])} · suite {e(env['suite'])} ·
git {e(env['git'])} · {e(env['host'])}</p>
<p><span class="pass">{tot[PASS]} PASS</span> · <span class="fail">{tot[FAIL]} FAIL</span> ·
<span class="notrun">{tot[NOT_RUN]} NOT RUN</span></p>
<h2>Environment</h2><table><tr><th>Needs</th><th>Available</th><th>Detail</th></tr>{hw}</table>
{''.join(rows)}
<p><small>NOT RUN = the AC needs something this machine does not have; it is neither a pass nor a failure
unless run with --strict.</small></p></html>
"""
    path.write_text(doc, encoding="utf-8")


def write_junit(path: Path, results: list[dict], env: dict) -> None:
    """One testsuite per ticket, one testcase per AC. TestRail ids ride as properties (trcli matches
    ``test_id`` with --case-matcher property) and as a ``[C1234]`` prefix in the name (--case-matcher name)."""
    root = ET.Element("testsuites", name="DX AI Studio acceptance")
    for t in results:
        tr = t.get("testrail")
        acs = t["ac"]
        suite = ET.SubElement(root, "testsuite", name=f"{t['key']} {t['title']}",
                              tests=str(len(acs)),
                              failures=str(sum(a["status"] == FAIL for a in acs)),
                              skipped=str(sum(a["status"] == NOT_RUN for a in acs)),
                              errors="0", time=f"{t['wall']:.1f}")
        props = ET.SubElement(suite, "properties")
        ET.SubElement(props, "property", name="jira", value=t["key"])
        if tr:
            ET.SubElement(props, "property", name="testrail_case_id", value=tr)
        for k, v in env["hardware"].items():
            ET.SubElement(props, "property", name=f"hw.{k}", value=("yes: " if v["available"] else "no: ") + v["detail"])
        for a in acs:
            name = (f"[{tr}] " if tr else "") + f"{a['id']} {a['title']}"
            case = ET.SubElement(suite, "testcase", classname=t["key"], name=name, time=f"{a['duration']:.1f}")
            cprops = ET.SubElement(case, "properties")
            if tr:
                ET.SubElement(cprops, "property", name="test_id", value=tr)
            ET.SubElement(cprops, "property", name="ac", value=a["id"])
            ET.SubElement(cprops, "property", name="tests", value=" ".join(a["tests_listed"]))
            if a["status"] == FAIL:
                ET.SubElement(case, "failure", message=(a["reason"].splitlines() or ["failed"])[0][:300]).text = a["reason"]
            elif a["status"] == NOT_RUN:
                ET.SubElement(case, "skipped", message=("NOT RUN: " + a["reason"])[:300])
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def build_results(tickets: list[dict], hw: dict, records: dict, walls: dict, stopped: str = "") -> list[dict]:
    out = []
    for t in tickets:
        acs = []
        for ac in t["ac"]:
            st = ac_status(ac, hw, records, stopped)
            acs.append({"id": ac["id"], "title": ac["title"], "requires": ac["requires"],
                        "tests_listed": ac["tests"], **st})
        out.append({"key": t["key"], "alias": t["alias"], "title": t["title"], "testrail": t.get("testrail"),
                    "wall": walls.get(t["key"], 0.0), "ac": acs})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("selection", nargs="?", default="all")
    ap.add_argument("--list", action="store_true", help="print tickets, AC and mapped tests, run nothing")
    ap.add_argument("--strict", action="store_true", help="NOT RUN also fails the run")
    ap.add_argument("--out", help="report directory (default var/acceptance/<timestamp>)")
    args = ap.parse_args(argv)

    manifest = load_manifest()
    problems = validate_manifest(manifest)
    if problems:
        print("manifest.json is invalid:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 2
    try:
        tickets = select(manifest, args.selection)
    except SelectionError as exc:
        print(f"--acceptance: {exc}", file=sys.stderr)
        return 2
    if args.list:
        print(list_text(tickets))
        return 0

    sys.path.insert(0, str(ROOT))
    from tests.acceptance.hardware import probe_all

    started = _dt.datetime.now()
    out = Path(args.out) if args.out else ROOT / "var" / "acceptance" / started.strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    hw = probe_all()
    os.environ["DX_ACCEPT_HW"] = json.dumps(hw)
    print("== Acceptance: " + ", ".join(t["key"] for t in tickets))
    for k, (ok, detail) in hw.items():
        print(f"   {k:<8} {'yes' if ok else 'no ':<4} {detail}")

    tmp_root = Path(tempfile.mkdtemp(prefix="dx-acceptance-", dir="/dev/shm" if Path("/dev/shm").is_dir() else None))
    outcomes = tmp_root / "outcomes.jsonl"
    logs = out / "logs"
    walls: dict[str, float] = {}
    stopped = ""
    t0 = time.monotonic()
    try:
        steps = plan(tickets, hw)
        for i, (key, test_file, nodes) in enumerate(steps, 1):
            if _free_mb() < MIN_FREE_MB:
                stopped = f"run stopped early: only {_free_mb():.0f} MB free disk (< {MIN_FREE_MB} MB)"
                print("STOP: " + stopped, file=sys.stderr)
                break
            logs.mkdir(exist_ok=True)
            log = logs / f"{i:02d}-{Path(test_file).stem}.log"
            print(f"-- [{i}/{len(steps)}] {key}: {test_file} ({len(nodes)} tests)", flush=True)
            code, took = run_process(nodes, outcomes, out / "screenshots", tmp_root, log)
            walls[key] = walls.get(key, 0.0) + took
            print(f"   exit {code} in {_fmt_s(took)}", flush=True)
            if code == 0:
                log.unlink(missing_ok=True)       # keep logs of failing processes only
        records = read_outcomes(outcomes)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    wall = time.monotonic() - t0
    if logs.exists() and not any(logs.iterdir()):
        logs.rmdir()

    results = build_results(tickets, hw, records, walls, stopped)
    env = {**environment(hw), "when": started.isoformat(timespec="seconds"), "stopped": stopped}
    (out / "results.json").write_text(json.dumps({"environment": env, "wall": wall, "tickets": results},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    write_markdown(out / "report.md", results, env, wall)
    write_html(out / "report.html", results, env, wall)
    write_junit(out / "junit.xml", results, env)

    tot = summarize(results)
    print("")
    print(f"{'Ticket':<14} {'PASS':>4} {'FAIL':>4} {'NOT RUN':>7}  {'Time':>7}")
    for t in results:
        c = {s: sum(1 for a in t["ac"] if a["status"] == s) for s in (PASS, FAIL, NOT_RUN)}
        print(f"{t['key']:<14} {c[PASS]:>4} {c[FAIL]:>4} {c[NOT_RUN]:>7}  {_fmt_s(t['wall']):>7}")
        for a in t["ac"]:
            if a["status"] != PASS:
                first = (a["reason"].splitlines() or [""])[0][:150]
                print(f"    {a['status']:<7} {a['id']:<11} {_fmt_s(a['duration']):>6}  {first}")
    print(f"Total: {tot[PASS]} PASS, {tot[FAIL]} FAIL, {tot[NOT_RUN]} NOT RUN in {_fmt_s(wall)}")
    print(f"Report: {out / 'report.md'}")
    if stopped:
        print(f"INCOMPLETE: {stopped}", file=sys.stderr)
        return 1
    if tot[FAIL]:
        return 1
    if args.strict and tot[NOT_RUN]:
        print("--strict: NOT RUN counts as a failure", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

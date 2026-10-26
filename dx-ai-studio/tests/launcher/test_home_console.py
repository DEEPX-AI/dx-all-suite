"""The home runs the agent without leaving the page — on the module's API.

The home gets its own agent surface and dx_agent_dev keeps its own. That is two
UIs, and it must not become two implementations: the launcher already reverse
proxies the module at `/agent/`, so the home calls the same endpoints the module
calls. Nothing about running an agent is reimplemented here.

What is genuinely new is only the rendering. The stream is already typed —
`message` / `command` / `log` / `status` / `session` / `done` / `error` — and it
splits cleanly: prose on the left, terminal on the right.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
CONSOLE = STATIC / "home-console.js"
INDEX = STATIC / "index.html"
STYLE = STATIC / "style.css"


def console() -> str:
    assert CONSOLE.is_file(), "launcher/static/home-console.js is missing"
    return CONSOLE.read_text(encoding="utf-8")


def rule(selector: str) -> str:
    """The rule whose selector is exactly this — not one that merely ends with it.

    `.work-term` and `.work-split.is-collapsed .work-term` both end in the same
    token, and matching the wrong one reads a display:none as the pane's own
    overflow behaviour.
    """
    css = STYLE.read_text(encoding="utf-8")
    m = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert m, f"{selector} rule missing"
    return re.sub(r"\s+", "", m.group(1))


# ── one backend ─────────────────────────────────────────────────


def test_the_home_calls_the_modules_endpoints_through_the_proxy():
    src = console()
    for path in ("/agent/api/agent/run", "/agent/api/agent/cancel"):
        assert path in src, f"the home must reach the module at {path}"


def test_no_new_server_route_was_added_for_this():
    """If the home needed its own agent endpoint, there would be two of them.

    The launcher already proxies dx_agent_dev; adding a route here would mean
    the module's API and the home's could drift apart.
    """
    launcher = (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert '"/api/agent' not in launcher, (
        "the home must consume the module's agent API, not republish it"
    )


def test_the_module_is_untouched_by_this_feature():
    """dx_agent_dev keeps its own console. This branch does not edit it."""
    src = console()
    assert "dx_agent_dev/" not in src


# ── the split ───────────────────────────────────────────────────


def test_working_view_splits_narration_from_terminal():
    html = INDEX.read_text(encoding="utf-8")
    for element_id in ("homeWork", "workNarration", "workTerminal", "workTerminalOut"):
        assert f'id="{element_id}"' in html, f"missing #{element_id}"


def test_the_split_is_fixed_and_the_terminal_collapses():
    body = rule(".work-split")
    assert "grid-template-columns" in body
    assert "38fr" in body and "62fr" in body, (
        "the transcript is where code and logs land, so it takes the larger half"
    )
    assert "grid-template-columns:1fr" in rule(".work-split.is-collapsed")


def test_terminal_scrolls_inside_its_own_pane():
    """Wide output must never make the page scroll sideways."""
    assert "overflow-x:auto" in rule(".work-term")


# ── event routing ───────────────────────────────────────────────


def test_events_go_to_the_side_that_can_show_them():
    src = console()
    routing = src[src.index("function renderEvent") :]
    for event in ("message", "command", "log", "status", "done", "error"):
        assert f"'{event}'" in routing, f"the stream's {event!r} event is unhandled"
    assert "'ping'" in src, "keepalives must be dropped, not rendered"


def test_activity_summary_counts_by_the_adapters_own_prefixes():
    """The adapter formats shell lines as `$ cmd` and file tools as `✓ action: path`.

    We control both ends, so counting by prefix is a contract rather than a
    guess — and an unrecognised prefix falls back to a plain total instead of
    inventing a category.
    """
    src = console()
    assert "'$ '" in src or '"$ "' in src, "no command prefix in the summary"
    assert "✓" in src, "no file-operation prefix in the summary"


def test_the_terminal_pins_when_the_user_scrolls_up():
    """A log that yanks itself to the bottom while you read is a log nobody reads."""
    src = console()
    assert "addEventListener('scroll'" in src, "the terminal never notices you scrolled"
    assert "follow" in src.lower()


def test_setup_is_decided_before_the_run_not_during_it():
    """Agent, model and effort are a decision, and the console is not where it is made.

    The console header is only on screen once a run has started, and a control
    you can reach only after committing cannot help you decide whether to
    commit. The choice lives in the input form, visible at rest; the console
    reads it rather than owning a second copy.
    """
    src = console()
    assert "is-running" in src, "nothing marks the view as busy"
    assert "agentChoice" in src, "the console must read the choice, not re-collect it"
    # Source comments may name the endpoint, so match the call itself.
    assert "fetch('/agent/api/agent/models" not in src, (
        "the console must not fetch options — that endpoint needs ?agent= and "
        "returns no agent list"
    )

    html = INDEX.read_text(encoding="utf-8")
    build = html[html.index('id="homeAskForm"'):html.index('id="studioGrid"')]
    for element_id in ("setupAgent", "setupModel", "setupEffort"):
        assert f'id="{element_id}"' in build, f"{element_id} must sit in Build, before any run"

    setup = (ROOT / "launcher" / "static" / "home-agent-setup.js").read_text(encoding="utf-8")
    assert "'/status'" in setup, "the options come from the module's status endpoint"
    # Effort levels differ per agent — copilot has `none`, codex has `minimal`
    # and no `max`, claude has neither. A list written here would be wrong for
    # two of the five agents the module supports.
    for level in ("minimal", "xhigh", "max"):
        assert f"'{level}'" not in setup and f'"{level}"' not in setup, (
            f"effort level {level!r} is hard-coded; it belongs to the agent"
        )


def test_sign_in_state_comes_from_the_adapter_that_owns_it():
    """"Not signed in" is a claim, and a wrong one costs the user a login they already did.

    The module reports authenticated as true / false / null, where null means
    the adapter could not tell. All three are distinct here, and the exact
    login command comes from the adapter rather than being written twice.
    """
    setup = (ROOT / "launcher" / "static" / "home-agent-setup.js").read_text(encoding="utf-8")
    # The paths are built from one API base, so match the base and the route.
    assert "'/agent/api/agent'" in setup, "the setup must go through the module's proxy"
    assert "'/login/status?agent='" in setup, "the login hint must come from the module"
    assert "=== true" in setup and "=== false" in setup, (
        "unknown sign-in state must not be reported as signed out"
    )


def test_a_finished_run_ends_on_the_artefact():
    """The point of the minutes just spent is a thing you can execute."""
    src = console()
    assert "session_dir" in src, "the session folder is the payoff and must be shown"
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="workRunIt"' in html
    assert 'id="workOpenModule"' in html, (
        "the deeper flow lives in the module — the home must offer the door"
    )

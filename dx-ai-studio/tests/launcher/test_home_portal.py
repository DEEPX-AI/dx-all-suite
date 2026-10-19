"""Contracts for the launcher home as a platform portal.

The home's ornament (an orbital ring, a HUD frame, a neon halo, a logo that
decodes on load) is a deliberate brand surface. Written as loose hex literals
in the same stylesheet as the toolbar and the settings dialog, its colours
would be invisible to the theme switch, and the chrome could never follow
light mode.

The split this file enforces: **brand colour is named and scoped, chrome colour
comes from the shared semantic tokens.** An intentionally dark hero is not a
light-theme bug — but it needs a name before it can be one.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLE = ROOT / "launcher" / "static" / "style.css"
INDEX = ROOT / "launcher" / "static" / "index.html"

# `--x: #hex` is a definition, not a use. The css_token_gate ignores those for the
# same reason: naming a colour is the fix, spraying it is the problem.
_VAR_DEF = re.compile(r"--[\w-]+\s*:[^;}]*")
_HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")

# The palette the intro is built from. These may be *defined*, never *used* raw.
BRAND_LITERALS = (
    "#00D4FF", "#00d4ff",   # scanline, beams, gauge
    "#00FF88",              # module status
    "#FFD000", "#FFD700",   # core text, charge dot
    "#ff0040",              # decode glitch
    "#0A1628",              # splash ground
)

# Surfaces a user operates. These follow the theme, so they may name no literal.
CHROME_SELECTORS = (
    ".top-bar",
    ".launch-card",
    ".buy-topbar-btn",
    ".replay-btn",
    ".deepx-link",
    ".eco-link",
    ".route-recovery-notice",
    ".pu-tags > span",
    ".platform-info-close",
    ".studio-beta-badge",
)


def style() -> str:
    return STYLE.read_text(encoding="utf-8")


def uses_of(css: str) -> str:
    """The stylesheet with variable definitions removed — what is left is usage."""
    return _VAR_DEF.sub("", css)


def rule_body(css: str, selector: str) -> str:
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert m, f"{selector} rule missing from launcher/static/style.css"
    return m.group(1)


def test_brand_palette_is_defined_once_and_scoped():
    """The neon lives in one named block, not sprayed across the file."""
    css = style()
    assert "--brand-" in css, (
        "the intro palette has no name — define --brand-* tokens so the "
        "deliberately-dark surface is a decision instead of 52 stray literals"
    )
    defs = re.findall(r"--brand-[\w-]+\s*:", css)
    assert len(defs) >= 5, f"expected the intro palette as tokens, found {len(defs)}"


def test_brand_literals_are_never_used_raw():
    """A brand colour may be defined once; using it raw puts it beyond reach."""
    used = uses_of(style())
    leaked = sorted({lit for lit in BRAND_LITERALS if lit in used})
    assert not leaked, (
        f"brand colours used as literals instead of var(--brand-*): {leaked}"
    )


def test_chrome_selectors_carry_no_literal_colour():
    """Chrome follows the theme, so it may not name a colour of its own."""
    css = style()
    offenders = {}
    for selector in CHROME_SELECTORS:
        body = _VAR_DEF.sub("", rule_body(css, selector))
        hits = _HEX.findall(body)
        if hits:
            offenders[selector] = sorted(set(hits))
    assert not offenders, (
        "chrome must take colour from the shared semantic tokens "
        f"(--surface-*, --text-*, --status-*): {offenders}"
    )


# ── the portal nav ──────────────────────────────────────────────
# One navigation, not two: the home must not reach the same eight places from
# both a dot strip in the top bar and a ring of tiles. Every other surface in
# the studio navigates from one place.

def index() -> str:
    return INDEX.read_text(encoding="utf-8")


def test_the_home_has_no_section_nav():
    """The home has no section nav (Home, Modules, Learn).

    The home is one screen, so an anchor has nowhere to scroll. SDK Library and
    About are books in the grid; the wordmark goes home. A section nav would
    point at nothing.
    """
    html = index()
    assert 'class="portal-nav' not in html, "the section nav is back"
    assert 'id="portalNav"' not in html


def test_the_duplicate_dot_strip_is_gone():
    """Eight dots and eight tiles pointed at the same eight modules."""
    html = index()
    assert 'class="status-dots"' not in html, (
        "the dot strip duplicates the module cards — module state belongs on "
        "the card it describes"
    )


def test_the_ring_left_the_resting_home():
    """The orbital survives as the intro, not as the layout.

    Eight tiles pinned to a circle can only scale, never rewrap: at 650px the
    cards clipped and the link column floated over the copy. Most of the
    launcher's breakpoints existed to prop that up.
    """
    css = style()
    assert "min-width: 769px" not in css and "min-width:769px" not in css, (
        "the orbital range query outlived the orbital layout"
    )
    html = index()
    ring_at_top = html.index('class="orbital-card"') if 'class="orbital-card"' in html else -1
    if ring_at_top >= 0:
        intro = html.index('id="splashOverlay"')
        assert ring_at_top > intro, (
            "orbital markup must live inside the intro overlay, not the resting home"
        )


# ── the hero ────────────────────────────────────────────────────
# The centre of the ring said "DEEPX / AI Studio / 8 Modules" in dimmed text
# behind a marketing collage. Two focal points at the same depth, so neither
# read. The hero says one thing and offers one input.


def test_the_prompt_is_the_first_thing_in_the_work_column():
    """The command line comes before the tools.

    The top of a local app's work surface is not for a pitch (a big headline
    and a two-line subtitle). The stage keeps a title, but the input is the
    first thing you can act on, above the module grid.
    """
    html = index()
    assert 'class="home-hero"' not in html, "the marketing hero is back"
    main = html[html.index('id="homeStage"'):]
    assert main.index('id="homeAsk"') < main.index('id="studioGrid"'), (
        "the prompt must come before the module grid"
    )
    ask = main[main.index('id="homeAsk"'):][:400]
    assert "placeholder" in ask, "an empty box with no example is a blank stare"


def test_the_modules_are_above_the_fold():
    """The only reason to open a launcher is to launch something.

    The previous home stacked seven full-width sections and put the eight
    module cards fourth, two scrolls down. On the stage they sit directly under
    the command line, and everything that is not a tool is in the bar below.
    """
    html = index()
    stage = html.index('id="homeStage"')
    grid = html.index('id="studioGrid"')
    bar = html.index('id="homeBar"')
    assert stage < grid < bar
    for gone in ('id="models"', 'id="ecosystem"', 'id="solutions"'):
        assert gone not in html, f"{gone} is a page section, not a work surface"



def test_hero_never_shows_an_empty_box():
    """A blank prompt on a landing page is a blank stare.

    The example chips are the feature, not decoration: they teach the syntax
    and they are one click to run. They are also the contract the router in the
    next task has to satisfy.
    """
    html = index()
    chips = html.count('class="ask-chip"')
    assert chips >= 4, f"expected at least four example chips, found {chips}"


def test_hero_says_whether_the_hardware_is_there():
    """A website cannot say "DX-M1 connected". That line is why this is not one."""
    html = index()
    assert 'id="heroDeviceChip"' in html



# ── the answered state ──────────────────────────────────────────


def test_answer_surface_exists_and_starts_hidden():
    html = index()
    assert 'id="homeAnswer"' in html, "the prompt has nowhere to answer"
    answer = html[html.index('id="homeAnswer"'):][:400]
    assert "hidden" in answer, "the answer surface must not occupy the resting home"


def test_the_agent_is_an_escalation_not_a_fourth_route():
    """Offering "build it from scratch" beside a preset we just found reads as
    if the studio does not trust its own answer.

    When we matched, the agent is one quiet line under the routes. When we did
    not, it is the whole answer — and it shows a plan before it spends minutes.
    """
    html = index()
    assert 'id="answerEscalate"' in html, "no quiet agent line under the routes"
    assert 'id="answerAgentPlan"' in html, "no agent plan for the unmatched case"
    css = style()
    escalate = rule_body(css, ".answer-escalate")
    assert "border-top" in escalate, (
        "the escalation sits below the routes as an aside, not among them"
    )


def test_the_plan_is_shown_before_the_agent_runs():
    """Escalating straight into a running agent is the jarring part.

    A few lines of "here is what I will do", with a time estimate, turns a leap
    into a decision — and gives the minutes an honest place to be declared.
    """
    html = index()
    plan = html[html.index('id="answerAgentPlan"'):]
    plan = plan[: plan.index("</section>")] if "</section>" in plan else plan[:1200]
    assert 'class="plan-steps"' in plan, "the agent must say what it will do first"
    assert 'id="answerAgentGo"' in plan, "and wait to be told to start"


# ── the sections ────────────────────────────────────────────────


def test_the_catalogue_size_lands_on_the_card_that_opens_it():
    """A five-across model row on the front door was a second Model Zoo.

    348 models belong in the module built to browse them; what the front door
    owes you is the number, on the card that goes there — and only when the zoo
    is actually up to be counted.
    """
    js = (ROOT / "launcher" / "static" / "home-sections.js").read_text(encoding="utf-8")
    assert "/zoo/api/catalog" in js, "the count must come from the zoo, not a constant"
    # The card selector is built from the app keys in MODULE_FACTS (six modules share
    # the code). What must hold is that zoo is in that table and the drawing code
    # finds cards by data-app.
    assert "orbital-card[data-app=" in js, "the count has to land on a module card"
    assert "'zoo'" in js, "the Model Zoo must still be one of the counted modules"
    html = index()
    assert 'id="homeModelRow"' not in html, "the duplicate model row is back"


def test_module_cards_say_what_they_are():
    """A tile with a name and `--:—` is a launcher icon with extra steps."""
    html = index()
    grid = html[html.index('id="studioGrid"'):]
    grid = grid[: grid.index("</section>")] if "</section>" in grid else grid[:9000]
    assert grid.count('class="card-desc"') >= 8, (
        "every module card needs a sentence saying what it is for"
    )
    assert ":—" not in grid, "a placeholder port is not module state"
    assert grid.count('data-role="state"') >= 8, "each card must have a state line"


def test_what_leaves_the_app_sits_below_the_work_surface():
    """No Ecosystem or Solutions sections: a partner list and invented one-liners.

    Neither is state and neither is a tool, so on a workspace they are filler
    with the same visual weight as the modules. The links that lead somewhere
    real live in the bar under the stage; the replay control is part of the
    tour, top right.
    """
    html = index()
    bar = html[html.index('id="homeBar"'):]
    bar = bar[: bar.index("</footer>")]
    assert 'class="deepx-links"' in bar, "the DEEPX links lost their home"
    assert 'id="replayBtn"' not in bar, "replay is the tour's, not a destination"
    tour = html[html.index('id="homeTour"'):html.index('id="homeStage"')]
    assert 'id="replayBtn"' in tour, "the replay control left the tour"
    widgets = html[html.index('id="homeDevice"'):html.index('id="homeBar"')]
    assert 'class="deepx-links"' not in widgets, (
        "a state widget that also carries a link directory is not a state widget"
    )


def test_module_state_comes_from_the_existing_poll():
    """One health poll, not two. The cards read what checkHealth already knows."""
    js = (ROOT / "launcher" / "static" / "launcher-app-frame.js").read_text(encoding="utf-8")
    assert js.count("setInterval(checkHealth") == 1, (
        "module state must not get a second poller"
    )

# ── the intro ───────────────────────────────────────────────────
# Four intros have shipped here and all four were rejected: a 17.5-second neon
# cinematic, a 1.2s fade with no idea in it, a hand-off whose points flew onto
# the finished page and read as debris, and a drawn black hole. Each borrowed a
# genre and illustrated it. This one borrows a grammar instead — Apple's own ad
# grammar — and applies it to the only subject we actually have: the wordmark.
# The grammar is the design, so the grammar is what is pinned. Durations,
# angles and distances are tuning, and none of them are.


def test_the_intro_obeys_apple_ad_grammar():
    """One subject, one camera move, and only the compositor's two properties.

    The four rejected intros all failed the same way: given a reference, they
    drew it. So the rule pinned here is not "what it looks like" but the four
    constraints the grammar actually imposes —

      · the subject is the wordmark, treated as a surface light crosses
      · exactly two properties animate: transform and opacity
      · type arrives last, after the camera has settled
      · no canvas and no per-frame loop — the compositor runs the motion

    The last one is why the previous intro is gone, and it is the cheapest to
    regress: one requestAnimationFrame loop brings the whole thing back onto
    the main thread. Typing the prompts is a handful of setTimeouts changing
    text, which is a different thing and is allowed.
    """
    src = (ROOT / "launcher" / "static" / "launcher-splash.js").read_text(encoding="utf-8")
    for banned in ("getContext", "requestAnimationFrame(function step",
                   "cancelAnimationFrame(ns._introRAF", "_stars", "_paint"):
        assert banned not in src, f"{banned} puts the intro back on the main thread"

    html = index()
    assert 'class="mark-shine"' in html, "no surface for the light to cross"
    assert 'id="splashSky"' not in html, "the canvas outlived the sequence that drew on it"

    css = style()
    # Only transform and opacity may be transitioned, on every part of the mark.
    for sel in (".mark", ".mark-shine", ".mark-sub"):
        body = rule_body(css, sel)
        assert "transition:" in body, f"{sel} does not animate"
        props = body[body.index("transition:"):].split(";")[0]
        for token in ("width", "height", "top", "left", "filter",
                      "background-position", "box-shadow", " all "):
            assert token not in props, f"{sel} animates {token.strip()}, which is not composited"

    # The camera moves once — a shallow rotation the specular reflection reads off.
    assert "rotateY" in rule_body(css, ".mark")
    assert "perspective" in rule_body(css, ".splash-overlay")

    # Type arrives last: the subtitle's transition carries a delay, and the
    # delay is long enough that the camera has settled before the type shows up.
    sub = rule_body(css, ".mark-sub")
    delays = [
        float(re.findall(r"([\d.]+)s", part)[-1])
        for part in sub[sub.index("transition:"):].split(";")[0].split(",")
        if len(re.findall(r"([\d.]+)s", part)) >= 2
    ]
    assert delays, "the subtitle arrives with the camera instead of after it"
    assert min(delays) >= 0.6, f"the subtitle's delay is only {min(delays)}s"


def test_the_intro_subject_is_a_surface_the_light_crosses():
    """The intro's subject is a surface the light can cross; three invariants pin it.

    A flat white wordmark has no surface for light to cross, so the intro would
    read as refined but empty. The subject is the real logotype used as a mask,
    with a material and a reflection. Three invariants make that read:

      1. The logo clips; the band moves. Putting the logo mask on the MOVING
         layer moves the letters instead of the light, and the X is drawn twice,
         offset. Plain text hides this because the glyphs look alike; the
         logotype does not.
      2. The face is dark at rest. A near-white face with a white band passing
         over it shows nothing (measured: face 239, band 255).
      3. The reflection's mask has to survive scaleY(-1). Masks apply before
         transforms, so a mask that is opaque at its own top ends up opaque at
         the visual BOTTOM — the reflection detaches and reads as a second
         wordmark lying below.
    """
    css = style()

    sweep = rule_body(css, ".mark-sweep")
    shine = rule_body(css, ".mark-shine")
    assert "deepx-logo.svg" in sweep, "the logo must clip from the stationary layer"
    assert "deepx-logo.svg" not in shine, (
        "the logo mask is on the moving layer, so the letters travel, not the light"
    )
    assert "transform" not in sweep, "the clipping layer must not move"
    assert "translateX" in shine, "nothing sweeps"

    face = rule_body(css, ".mark-face")
    rest = re.search(r"opacity:\s*([\d.]+)", face)
    assert rest and float(rest.group(1)) <= 0.6, (
        "the face is too bright at rest for a white specular to register on it"
    )

    floor = rule_body(css, ".mark-floor")
    assert "scaleY(-1)" in floor
    mask = re.search(r"mask-image:\s*linear-gradient\(([^;]+)\)", floor)
    assert mask, "the reflection has no falloff"
    assert mask.group(1).strip().startswith("rgba(0, 0, 0, 0)"), (
        "the reflection's mask is opaque at its own top, which scaleY(-1) turns "
        "into opaque at the bottom — it detaches from the object"
    )


def test_the_working_beat_shows_the_product_rather_than_claiming_it():
    """Apple's context shot and Google's search-query sequence, which here are
    the same shot.

    More decoration does not make an intro feel less thin. Apple's answer is
    the context shot — the product in use — and Google's "Parisian Love" tells
    a whole story with nothing but queries typed into the product's own input.
    This product's premise is "say what you want and it builds it", so those
    two references land on one scene: the studio working.

    That only holds if the scene is true, which is what this pins. The prompts
    are the ones already offered on the home's Build box, already translated
    into every locale — not copy invented for an animation. The answers are the
    modules that actually take that work, named as the home names them. An
    intro that shows the product doing something it cannot do is worse than an
    empty one.
    """
    js = (ROOT / "launcher" / "static" / "launcher-splash.js").read_text(encoding="utf-8")
    html = index()

    work = re.search(r"_WORK = \[(.*?)\];", js, re.DOTALL)
    assert work, "the working beat has no script"
    beats = re.findall(r"ask:\s*'([^']+)'\s*,\s*by:\s*'([^']+)'", work.group(1))
    assert len(beats) >= 3, "one prompt is an example; three is the product working"

    # The home offers requests in two places: the chips (showcase prompts) and the
    # placeholder cycle, which also carries the short requests the router sends straight
    # to a module (the intro's three routed requests live in the cycle).
    prompts = (ROOT / "launcher" / "static" / "home-prompts.js").read_text(encoding="utf-8")
    cycle = prompts[prompts.index("window.DXHomePlaceholders"):]
    for ask, by in beats:
        assert "data-i18n=\"" + ask + "\"" in html or \
               "data-i18n-placeholder=\"" + ask + "\"" in html or \
               json.dumps(ask) in cycle, (
            f"{ask!r} is copy written for the intro, not something the home offers"
        )
        assert "'" + ask + "':" in html, f"{ask!r} is not in the dictionary"
        assert ">" + by + "<" in html, f"{by!r} is not a module the home lists"


def test_the_working_beats_are_regenerable_and_stay_in_the_splash():
    """Every scene in the working beats can be made again, and none leaks into the page.

    All three beats are real material: sixteen channels of DEEPX's own sample
    footage with the boxes a DX-M1 drew, a drive through LA segmented frame by
    frame on a DX-M1, and the real YOLO26n graph folding into the chip. Mixed
    colour casts and AI overlays baked into photographs are met by one grade per
    scene and by keeping results as data the page draws where it can.

    An asset nobody can regenerate is worse than none, so every folder names its
    bake script and its source.

    It also pins a boundary: replacing the intro's photo paths must not touch the
    About section's use-case images.
    """
    intro = ROOT / "launcher" / "static" / "img" / "intro"
    for stale in ("scene-detect.svg", "scene-segment.svg", "scene-silicon.svg"):
        assert not (intro / stale).exists(), f"{stale} was replaced by real material"
    assert not (ROOT / "scripts" / "intro" / "make_scenes.py").exists()
    for folder, script in (("stream", "bake_stream.py"), ("app", "bake_app.py"), ("compile", "bake_compile.py")):
        assert (intro / folder / "SOURCE.md").exists(), f"{folder}/SOURCE.md is missing"
        assert (ROOT / "scripts" / "intro" / script).exists(), f"{folder} cannot be baked again"
        assert script in (intro / folder / "SOURCE.md").read_text(encoding="utf-8")

    html = index()
    for js in ("intro-stream.js", "intro-app.js", "intro-compile.js"):
        assert f'<script src="/{js}"></script>' in html
    assert 'class="cue-scene"' not in html, "the old card is gone"
    # The About section keeps its own photographs.
    about = html[html.index("</header>"):]
    assert "img/intro/" not in about, (
        "an intro scene leaked into the page; the photo swap matched outside the splash"
    )
    for photo in ("usecase-smart-factory-agv-robot.jpg", "usecase-security-cctv-ip-camera.jpg"):
        assert photo in about, f"About lost {photo}"


def test_the_closing_claim_is_quoted_not_written():
    """Apple closes on one claim. Ours is not ours to write.

    The three scenes before it — a camera, a warehouse, the die — are the
    evidence for exactly one sentence, and the company already said it: DEEPX
    declared the era of Physical AI at CES 2026 and its CEO put it in a line.
    So the close quotes rather than composes.

    That only stays true if it keeps the marks of a quotation: quote
    characters, a <blockquote>, and an attribution naming who said it, in what
    role, and where. Strip any of those and it silently becomes marketing copy
    the studio is asserting on its own authority, which is a different and much
    weaker thing — and one nobody can check.

    It is deliberately untranslated. Re-authoring a named person's sentence in
    five languages would make it ours again, which is the thing this guards
    against; the i18n audit already skips strings identical across locales.
    """
    html = index()
    splash = html[html.index('id="splashOverlay"'):html.index("</header>")]

    assert "<blockquote" in splash, "the claim is no longer marked as a quotation"
    assert "\u201c" in splash and "\u201d" in splash, "the quote marks are gone"

    by = re.search(r'class="claim-by"[^>]*>([^<]+)<', splash)
    assert by, "the claim has no attribution"
    for part in ("Lokwon Kim", "DEEPX", "CES 2026"):
        assert part in by.group(1), f"the attribution does not say {part!r}"
    assert "CEO" in by.group(1), "the attribution does not say in what role"

    # A reader must be able to check it, so the source travels with the markup.
    # Scoped to the comment that introduces the quotation: the header's Buy link
    # also points at deepx.ai, and a looser search was satisfied by that instead.
    cite = re.search(r"<!--(?:(?!-->).)*?-->\s*<blockquote", splash, re.DOTALL)
    assert cite, "the quotation is not introduced by a source comment"
    assert "deepx.ai/" in cite.group(0), "the claim cites no source of its own"

    # Not translated, on purpose — a data-i18n key here would invite exactly the
    # re-authoring this guards against.
    claim = splash[splash.index("<blockquote"):splash.index("</blockquote>")]
    assert "data-i18n" not in claim, (
        "the quotation is marked for translation, which turns it into our words"
    )


def test_the_name_and_the_console_share_one_slot():
    """Two things in one place, and neither may inherit the other's delay.

    The subtitle and the prompt line occupy the same spot, so the sequence has
    one composition rather than a layout that jumps every beat. Both are
    absolutely placed inside the slot; laid out in flow they would sit at
    different heights and show at once.

    The delay is the subtler half. The subtitle's entrance is deliberately late
    — type arrives last — but a transition-delay applies to every direction, so
    a shared 1.85s would also delay its exit and its return: it would sit behind
    the first prompt for two seconds and could not come back before the cut
    after the work. Each state change carries its own transition.
    """
    css = style()
    slot = rule_body(css, ".mark-slot")
    assert "position: relative" in slot
    for sel in (".mark-sub", ".mark-cue"):
        assert "position: absolute" in rule_body(css, sel), f"{sel} is not in the slot"

    for sel in (".splash-overlay.is-working .mark-sub",
                ".splash-overlay.is-closed .mark-sub"):
        body = rule_body(css, sel)
        assert "transition:" in body, (
            f"{sel} inherits the entrance delay, so the subtitle moves seconds late"
        )
        assert not re.search(r"\)\s+[\d.]+s\s*[,;]", body), f"{sel} carries a delay"


def test_the_intro_cuts_rather_than_fades_into_the_app():
    """The mark scales past the lens, the app is switched on behind it, cut.

    A fade would show the app arriving. A cut does not — which is why the shell
    is revealed while the overlay still covers everything.
    """
    src = (ROOT / "launcher" / "static" / "launcher-splash.js").read_text(encoding="utf-8")
    assert "completeLauncherBoot" in src, "nothing turns the app on behind the cut"
    assert "is-through" in src
    css = style()
    assert "background: transparent" in rule_body(css, ".splash-overlay.is-through")


def test_the_intro_yields_to_reduced_motion():
    """Reduced motion gets the same frame, arrived at without the move.

    Not a skip: the wordmark and its subtitle still land, they just cross-fade
    into place. `is-still` is the state that says so, and it has to be reachable
    before anything is scheduled — a reduced-motion path that runs after the
    camera starts has already broken the promise.
    """
    src = (ROOT / "launcher" / "static" / "launcher-splash.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in src
    head = src[: src.index("is-running")]
    assert "is-still" in head, (
        "the reduced-motion exit must come before the camera is started"
    )
    css = style()
    for sel in (".splash-overlay.is-still .mark",
                ".splash-overlay.is-still .mark-shine",
                ".splash-overlay.is-still .mark-sub"):
        assert "transition: none" in rule_body(css, sel), f"{sel} still animates"


def test_module_state_says_nothing_until_it_knows():
    """A row's state is unknown until the health poll answers.

    The markup shipped an em dash as a placeholder, so eight of them sat on the
    page on every load — a character that means "we have not asked yet" to the
    person who wrote it and nothing at all to anyone else.
    """
    html = index()
    grid = html[html.index('id="studioGrid"'):]
    grid = grid[: grid.index("</section>")]
    assert 'data-role="state">—<' not in grid, "the placeholder dash is back"
    assert grid.count('data-role="state"') >= 8, "each row still needs its state line"

"""The intro's pixel axis.

The landing baselines plant dx-splash-seen before capture and skip the intro. So an
all-green run only means "the screens after the splash did not move"; it says nothing
about whether the intro draws as intended. The structural contract
(tests/launcher/test_home_portal.py) holds the markup, but correct markup can still
draw wrong — e.g. a logo mask attached to a moving layer showing two X marks, a face
too bright to show the specular, or a flipped reflection mask laying a second wordmark
down. Such defects pass the contract and show only in the frame.

Capture is not timed. The state is set to its final values and captured with
animations="disabled", so timing changes stay green and composition changes go red.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")
pytest.importorskip("PIL")

from tests.server_helpers import start_module_server  # noqa: E402
from tests.visual.baseline_spec import (  # noqa: E402
    INTRO_STATES,
    VIEWPORT,
    intro_baseline_name,
)
from tests.visual.compare import compare  # noqa: E402
from tests.visual.test_visual_regression import (  # noqa: E402
    ARTIFACT_DIR,
    BASELINE_DIR,
    MAX_CHANGED_RATIO,
    UPDATE,
)

# Set one state instead of playing the sequence. The copy must match _WORK in
# launcher-splash.js; if it drifts, test_home_portal's working-beat contract catches it first.
_DRIVE = """(state) => {
  const ov = document.getElementById('splashOverlay');
  if (!ov) return false;
  // 예약된 타이머를 먼저 끈다. 안 끄면 시퀀스가 제 갈 길을 가서 is-through 를
  // 얹거나 skipSplash 로 오버레이를 걷어 버리고, 캡처에는 인트로가 아니라 홈이
  // 찍힌다 — 그런 캡처끼리는 당연히 0픽셀로 일치하므로 결정성 측정도 속는다.
  const ns = window.DXLauncher;
  if (ns && ns._splashTimers) {
    ns._splashTimers.forEach(clearTimeout);
    ns._splashTimers.length = 0;
  }
  ov.className = 'splash-overlay is-running'
    + (state === 'work' ? ' is-working' : '')
    + (state === 'close' ? ' is-closed' : '');
  if (state === 'work') {
    const cue = document.getElementById('splashCue');
    cue.setAttribute('data-beat', '1');
    cue.classList.remove('is-out');
    cue.classList.add('is-answered');
    document.getElementById('splashCueText').textContent = 'segment a video file';
    document.getElementById('splashCueAnswer').textContent = 'App';
  }
  return true;
}"""


def _capture_intro(browser, state: str, out: Path) -> None:
    server, port = start_module_server("launcher")
    try:
        # reduced_motion is not used here. The intro has its own reduced-motion path
        # (is-still), which would capture a different design that clears after 700ms.
        # animations="disabled" pins motion at the final state instead.
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()
        try:
            page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60_000)
            page.wait_for_selector("#splashOverlay", timeout=10_000)
            assert page.evaluate(_DRIVE, state), "the intro overlay never rendered"
            page.wait_for_timeout(700)
            out.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(out), animations="disabled")
        finally:
            page.close()
            ctx.close()
    finally:
        server.shutdown()


@pytest.mark.visual
@pytest.mark.parametrize("state", INTRO_STATES)
def test_intro_state_matches_baseline(visual_browser, state, tmp_path):
    engine, browser = visual_browser
    name = intro_baseline_name(state)

    baseline = BASELINE_DIR / engine / name
    if UPDATE:
        _capture_intro(browser, state, baseline)
        pytest.skip(f"baseline written: {baseline.relative_to(BASELINE_DIR.parent)}")

    if not baseline.is_file():
        pytest.skip(
            f"no baseline for {engine}/{name} — create it with "
            f"DX_VISUAL_UPDATE=1 pytest tests/visual/"
        )

    candidate = tmp_path / name
    _capture_intro(browser, state, candidate)

    diff_out = ARTIFACT_DIR / engine / f"{name[:-4]}-diff.png"
    result = compare(baseline, candidate, diff_out)

    assert result["same_size"], (
        f"{engine}/{name}: viewport changed — baseline {result['baseline_size']} "
        f"vs current {result['candidate_size']}"
    )
    assert result["changed_ratio"] <= MAX_CHANGED_RATIO, (
        f"{engine}/{name}: {result['changed_pixels']} px "
        f"({result['changed_ratio'] * 100:.4f}%) differ, limit "
        f"{MAX_CHANGED_RATIO * 100:.4f}%. Diff: {diff_out}"
    )

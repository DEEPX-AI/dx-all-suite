"""Browser copy audit – language-switch smoke for all modules/states/locales.

Starts each module server, navigates to every state in the copy audit matrix,
triggers a language switch for each locale, and records a
``BrowserObservation`` artifact.  Locale marker failures (e.g. ``document.lang``
not updated, missing ``lang-*`` body class) are written as
``runtime-not-switching`` evidence — they do *not* fail the test.

Requires:
- Playwright (``pip install playwright && playwright install chromium``)
- ``DX_I18N_AUDIT_ARTIFACT_DIR`` environment variable pointing to the
  directory where observation JSON files should be written.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402
from tools.i18n_audit.browser_evidence import (  # noqa: E402
    BrowserObservation,
    stable_visible_text_sample,
    write_browser_observation,
)
from tools.i18n_audit.browser_denylist import find_stale_english_phrases  # noqa: E402
from tools.i18n_audit.browser_matrix import (  # noqa: E402
    COPY_AUDIT_STATES,
    wait_for_copy_audit_state_ready,
)


@pytest.fixture(scope="session")
def artifact_root() -> Path:
    raw = os.environ.get("DX_I18N_AUDIT_ARTIFACT_DIR", "")
    if not raw:
        pytest.skip("DX_I18N_AUDIT_ARTIFACT_DIR not set")
    p = Path(raw)
    p.mkdir(parents=True, exist_ok=True)
    return p


@pytest.fixture(scope="session")
def browser(artifact_root):
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def page(artifact_root, browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    try:
        pg = ctx.new_page()
    except Exception:
        ctx.close()
        raise
    try:
        yield pg
    finally:
        try:
            pg.close()
        finally:
            ctx.close()

@pytest.mark.smoke
@pytest.mark.parametrize(
    "state",
    COPY_AUDIT_STATES,
    ids=[f"{s.module}-{s.state}" for s in COPY_AUDIT_STATES],
)
def test_state_records_language_marker_observations_for_all_locales(artifact_root, page, state):
    server, port = start_module_server(state.server_module)
    try:
        page.goto(
            f"http://127.0.0.1:{port}{state.route}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector(
            state.expected_selector, state="attached", timeout=8000
        )
        wait_for_copy_audit_state_ready(page, state)

        for lang in state.locales:
            # Attempt to trigger language switch via common DX patterns.
            page.evaluate(
                """(lang) => {
                    localStorage.setItem('dx-lang', lang);
                    if (window.DXI18n) window.DXI18n.setLang(lang);
                    window.dispatchEvent(
                        new MessageEvent('message', {
                            data: { type: 'dx-lang-change', lang }
                        })
                    );
                }""",
                lang,
            )
            page.wait_for_timeout(150)

            document_lang = page.evaluate(
                "() => document.documentElement.lang || ''"
            )
            has_body_class = page.evaluate(
                "(lang) => document.body.classList.contains('lang-' + lang)",
                lang,
            )

            try:
                samples = stable_visible_text_sample(
                    page.locator("body").inner_text(timeout=3000)
                )
            except Exception:
                samples = ()

            issue_type = (
                "observed"
                if document_lang == lang and has_body_class
                else "runtime-not-switching"
            )

            stale_hits = find_stale_english_phrases(
                lang, samples, issue_type=issue_type
            )
            if stale_hits:
                issue_type = "stale-english-copy"

            write_browser_observation(
                artifact_root,
                BrowserObservation(
                    module=state.module,
                    state=state.state,
                    route=state.route,
                    locale=lang,
                    document_lang=document_lang,
                    body_has_lang_class=has_body_class,
                    visible_text_sample=samples,
                    issue_type=issue_type,
                ),
            )
            assert issue_type != "stale-english-copy", (
                f"{state.module}/{state.state}@{lang}: stale English {stale_hits}"
            )
    finally:
        try:
            server.shutdown()
        finally:
            server.server_close()

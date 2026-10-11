"""Every control a user can reach has a name a screen reader can read (2026-10-11 axe audit).

axe-core (WCAG 2 A/AA) on the live Studio found 383 unnamed form controls, among them every model checkbox in the
Benchmark list and the Model Zoo cart, the A/B Compare selects and the Agent Dev settings. It also found an icon-only
close button, a page-tab row marked role=tablist that holds no tabs, Run Demo cards that are buttons with buttons
inside, and aria-selected on plain buttons. This test does not vendor axe. It applies the same rules to every page of
every module.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.browser_support import resolve_chromium_executable  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

MODULES = ["dx_app", "dx_stream", "dx_modelzoo", "dx_compiler", "dx_planner", "dx_benchmark", "dx_monitor",
           "dx_agent_dev"]

# The accessible name, simplified from accname: aria-labelledby, aria-label, <label for>, a wrapping <label>, title,
# placeholder (inputs), then the button's own text or image alt.
_PROBLEMS = r"""() => {
  const visible = el => el.getClientRects().length && getComputedStyle(el).visibility === 'visible';
  const txt = el => (el ? (el.innerText || el.textContent || '') : '').replace(/\s+/g, ' ').trim();
  function name(el) {
    const by = el.getAttribute('aria-labelledby');
    if (by && by.split(/\s+/).map(id => txt(document.getElementById(id))).join('').trim()) return true;
    if ((el.getAttribute('aria-label') || '').trim()) return true;
    if (el.id && [...document.querySelectorAll('label[for="' + CSS.escape(el.id) + '"]')].some(l => txt(l))) return true;
    const wrap = el.closest('label');
    if (wrap && txt(wrap)) return true;
    if ((el.getAttribute('title') || '').trim()) return true;
    if (el.tagName === 'INPUT' && (el.getAttribute('placeholder') || '').trim()) return true;
    if (el.tagName === 'BUTTON' && (txt(el) || [...el.querySelectorAll('img[alt]')].some(i => i.alt.trim()))) return true;
    return false;
  }
  const where = el => (el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + [...el.classList].join('.'))
    + (el.getAttribute('onchange') || el.getAttribute('onclick') || '').slice(0, 40);
  const out = [];
  document.querySelectorAll('input:not([type=hidden]), select, textarea, button').forEach(el => {
    if (visible(el) && !el.closest('[aria-hidden=true]') && !name(el)) out.push('unnamed ' + where(el));
  });
  document.querySelectorAll('[role=tablist]').forEach(list => {
    [...list.children].forEach(c => { if (c.getAttribute('role') !== 'tab') out.push('tablist child without role=tab ' + where(c)); });
  });
  const interactive = 'a[href], button, input, select, textarea, [role=button], [tabindex]:not([tabindex="-1"])';
  document.querySelectorAll('[role=button], a[href], button').forEach(el => {
    if (visible(el) && el.querySelector(interactive)) out.push('interactive inside interactive ' + where(el));
  });
  document.querySelectorAll('button.disabled, [role=button].disabled').forEach(el => {
    if (visible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true') out.push('looks disabled, is not ' + where(el));
  });
  document.querySelectorAll('[aria-selected]').forEach(el => {
    const r = el.getAttribute('role');
    if (!['tab', 'option', 'row', 'gridcell', 'treeitem', 'columnheader', 'rowheader'].includes(r))
      out.push('aria-selected on role=' + r + ' ' + where(el));
  });
  return [...new Set(out)];
}"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
        yield br
        br.close()


@pytest.mark.parametrize("module", MODULES)
def test_every_page_names_its_controls(browser, module):
    srv, port = start_module_server(module)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(600)
        problems = {"(first page)": page.evaluate(_PROBLEMS)}
        tabs = page.evaluate("[...document.querySelectorAll('.dx-shell-tabs .dx-tab')].map(b => b.dataset.page)")
        for tab in tabs:
            page.evaluate("p => document.querySelector('.dx-shell-tabs .dx-tab[data-page=\"' + p + '\"]').click()", tab)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            page.wait_for_timeout(700)
            problems[tab] = page.evaluate(_PROBLEMS)
        problems = {k: v for k, v in problems.items() if v}
        assert not problems, "\n" + "\n".join(f"{k}: {x}" for k, v in problems.items() for x in v)
    finally:
        ctx.close()
        srv.shutdown()
        srv.server_close()

"""Layout faults of a rendered model card: sideways scroll, children overflowing their parent, and labels,
numbers, chips or buttons that wrap. Used by the CI browser suite and by the one-off check over all cards:

    .venv/bin/python -m tests.dx_modelzoo.model_card_layout <dx_app root>
"""
from __future__ import annotations

import sys
from pathlib import Path

WIDTHS = (1280, 1024, 390)
THEMES = ("dark", "light")
CHECK = r"""(theme) => {
  const out = [];
  const de = document.documentElement;
  if ((de.dataset.theme === 'light') !== (theme === 'light')) out.push('theme not applied: ' + theme);
  if (de.scrollWidth > de.clientWidth + 1) out.push('page scrolls sideways: ' + de.scrollWidth + ' > ' + de.clientWidth);
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('.scroll, pre') || el.tagName === 'PRE' || getComputedStyle(el).position === 'absolute') continue;
    const r = el.getBoundingClientRect(), p = el.parentElement && el.parentElement.getBoundingClientRect();
    if (p && r.width && (r.right > p.right + 1.5 || r.left < p.left - 1.5))
      out.push('overflows parent: <' + el.tagName.toLowerCase() + ' class="' + el.className + '"> ' + el.textContent.trim().slice(0, 40));
  }
  const lines = node => { const r = document.createRange(); r.selectNodeContents(node);
    return new Set([...r.getClientRects()].filter(x => x.width > 0).map(x => Math.round(x.top))).size; };
  ['th', 'td.n', 'td.k', '.kpi b', '.chips li', '.btn', 'dl.facts dt', 'ul.dl .t b', 'ul.dl .l a', '.theme'].forEach(sel =>
    document.querySelectorAll(sel).forEach(el => {
      const node = [...el.childNodes].find(n => n.nodeType === 3 && n.textContent.trim()) || el;
      if (lines(node) > 1) out.push('wraps: ' + sel + ' "' + el.textContent.trim().slice(0, 40) + '"');
    }));
  return [...new Set(out)];
}"""


def faults(browser, html_path):
    found = []
    for theme in THEMES:
        for width in WIDTHS:
            ctx = browser.new_context(viewport={"width": width, "height": 900})
            if theme == "light":
                ctx.add_init_script("try{localStorage.setItem('dx-card-theme','light')}catch(e){}")
            page = ctx.new_page()
            page.goto(Path(html_path).resolve().as_uri(), wait_until="load")
            found += [f"{theme}@{width}: {f}" for f in page.evaluate(CHECK, theme)]
            ctx.close()
    return found


def main(dx_app_root):
    from playwright.sync_api import sync_playwright

    from shared.chromium import resolve_chromium_executable

    cards = sorted(Path(dx_app_root).glob("src/python_example/*/*/*/model.html"))
    bad = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
        for i, card in enumerate(cards, 1):
            problems = faults(browser, card)
            if problems:
                bad += 1
                print(card.parent.name, *problems[:6], sep="\n  ")
            if i % 50 == 0:
                print(f"{i}/{len(cards)} checked", flush=True)
        browser.close()
    print(f"{len(cards)} cards, {bad} with layout faults")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

"""Full UI-click tutorial journey audit — no startSection() shortcuts."""
from __future__ import annotations

import json
from typing import Any

from playwright.sync_api import Page

METRICS_JS = """() => {
  const engine = window._dxTutorial;
  if (engine && typeof engine._refreshHighlight === 'function') {
    engine._refreshHighlight();
  }
  const step = engine && engine._curSection
    ? engine._curSection.steps[engine._curStep]
    : null;
  const selector = step && step.target ? step.target : null;
  const ov = document.querySelector('.dxt-overlay.active');
  const sp = document.querySelector('.dxt-spotlight.active');
  const tip = document.querySelector('.dxt-tooltip.active');
  const floating = !!(tip && tip.style.transform && tip.style.transform.indexOf('translate(-50%') >= 0);
  let target = null;
  if (selector && engine && typeof engine._queryTarget === 'function') {
    target = engine._queryTarget(selector);
  } else if (selector) {
    target = document.querySelector(selector);
  }
  let targetRect = null;
  if (target) {
    const r = target.getBoundingClientRect();
    targetRect = { width: r.width, height: r.height };
  }
  return {
    sectionId: engine && engine._curSection ? engine._curSection.id : null,
    stepIndex: engine ? engine._curStep : null,
    selector,
    overlayActive: !!ov,
    spotlightActive: !!sp,
    tooltipActive: !!tip,
    floating,
    hasTarget: !!target,
    targetVisible: !!(targetRect && (targetRect.width > 0 || targetRect.height > 0)),
    tutorialMockActive: !!document.querySelector('[data-dxt-tutorial-mock]'),
  };
}"""


def set_lang(page: Page, lang: str) -> None:
    page.evaluate(
        """(lang) => {
      localStorage.setItem('dx-lang', lang);
      if (window.DXI18n && typeof DXI18n.setLang === 'function') DXI18n.setLang(lang);
    }""",
        lang,
    )


def dismiss_confirm(page: Page) -> None:
    page.evaluate(
        """() => {
      const btn = document.querySelector('.dxt-confirm-btn.primary');
      if (btn) btn.click();
    }"""
    )
    page.wait_for_timeout(150)


def analyze_step(metrics: dict[str, Any]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if metrics.get("tutorialMockActive"):
        issues.append(("MOCK_INJECTION", "data-dxt-tutorial-mock present in DOM"))
    selector = metrics.get("selector")
    if selector:
        if metrics.get("floating"):
            issues.append(("FLOATING_FALLBACK", f"target {selector!r} floating"))
        elif not metrics.get("spotlightActive"):
            issues.append(("NO_SPOTLIGHT", f"target {selector!r} no spotlight"))
        elif not metrics.get("hasTarget"):
            issues.append(("TARGET_MISSING", f"selector {selector!r} missing"))
        elif not metrics.get("targetVisible"):
            issues.append(("TARGET_HIDDEN", f"selector {selector!r} zero bbox"))
    elif metrics.get("tooltipActive") and not metrics.get("floating"):
        pass
    if not metrics.get("overlayActive"):
        issues.append(("NO_OVERLAY", "overlay inactive"))
    if not metrics.get("tooltipActive"):
        issues.append(("NO_TOOLTIP", "tooltip inactive"))
    return issues


def run_ui_journey(
    page: Page,
    *,
    lang: str = "en",
    module_setup: str = "() => {}",
    wait_selector: str = "#dxToolbar",
    ready_script: str = "() => window._dxTutorial",
    ready_timeout: int = 20000,
) -> list[dict[str, Any]]:
    """Click Tutorial → Start from Beginning → Next through all sections."""
    set_lang(page, lang)
    page.evaluate(module_setup)
    page.wait_for_timeout(500)
    page.wait_for_selector(wait_selector, timeout=ready_timeout)
    page.wait_for_function(ready_script, timeout=ready_timeout)

    page.evaluate(
        """() => {
      document.querySelectorAll('dialog[open]').forEach(d => {
        try { d.close(); } catch (e) {}
      });
      document.querySelectorAll('.modal-overlay.open').forEach(el => {
        el.classList.remove('open');
        if (el.tagName === 'DIALOG') el.removeAttribute('open');
      });
    }"""
    )

    page.evaluate("() => { if (window._dxTutorial) window._dxTutorial.resetProgress(); }")
    page.wait_for_timeout(200)

    page.evaluate("() => { const b = document.getElementById('dxToolbarTutorial'); if (b) b.click(); }")
    page.wait_for_selector(".dxt-toc", timeout=10000)
    page.evaluate("() => { const b = document.querySelector('.dxt-toc-btn-start'); if (b) b.click(); }")
    page.wait_for_selector(".dxt-tooltip.active", timeout=15000)

    results: list[dict[str, Any]] = []
    max_clicks = 500
    clicks = 0

    while clicks < max_clicks:
        page.wait_for_timeout(350)
        if page.query_selector(".dxt-confirm-overlay"):
            dismiss_confirm(page)
            page.wait_for_timeout(200)
            continue
        if not page.query_selector(".dxt-tooltip.active"):
            if page.query_selector(".dxt-toc"):
                break
            page.wait_for_timeout(200)
            continue

        metrics = page.evaluate(METRICS_JS)
        issues = analyze_step(metrics)
        results.append({"metrics": metrics, "issues": issues, "lang": lang})

        page.evaluate(
            """() => {
          const dlg = document.getElementById('dx-input-modal');
          if (dlg && dlg.open) {
            if (window.DXStream && typeof DXStream._inputModalCancel === 'function') {
              DXStream._inputModalCancel();
            } else {
              dlg.close();
            }
          }
        }"""
        )
        clicked = page.evaluate(
            "() => { const b = document.querySelector('.dxt-tip-next'); if (b) { b.click(); return true; } return false; }"
        )
        if not clicked:
            break
        clicks += 1
        for _ in range(10):
            page.wait_for_timeout(100)
            if page.query_selector(".dxt-confirm-overlay"):
                dismiss_confirm(page)
                break

    return results


def summarize(results: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for row in results:
        m = row["metrics"]
        for kind, detail in row["issues"]:
            failures.append(
                f"{m.get('sectionId')}|step{m.get('stepIndex')}|{kind}|{detail}"
            )
    return failures

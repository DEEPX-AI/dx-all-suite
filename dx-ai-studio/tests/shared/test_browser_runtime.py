"""Test runner browser provisioning contracts."""

import pytest


def test_chromium_launches_without_playwright_cache_binary():
    playwright = pytest.importorskip("playwright.sync_api")

    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content("<title>browser-ok</title>")
            assert page.title() == "browser-ok"
        finally:
            browser.close()
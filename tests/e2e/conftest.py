"""Shared E2E test fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the running app."""
    import os

    return os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def api_url(base_url):
    """API base URL."""
    return f"{base_url}"


@pytest.fixture(scope="session")
def page_context():
    """Playwright browser context for E2E tests."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="pt-BR",
            )
            yield context
            context.close()
            browser.close()
    except ImportError:
        pytest.skip("playwright não instalado")

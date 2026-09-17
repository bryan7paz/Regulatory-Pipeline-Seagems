"""Shared Playwright browser pool — reuse one Chromium instance across requests."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from core.config import logger

_browser = None
_lock = asyncio.Lock()


@asynccontextmanager
async def get_browser() -> AsyncGenerator:
    """Yield a shared Playwright Chromium browser instance.

    Lazily initialised on first use; reused across all subsequent calls.
    A new page is created per call and closed on exit.
    """
    global _browser
    from playwright.async_api import async_playwright

    async with _lock:
        if _browser is None or not _browser.is_connected():
            logger.info("Iniciando browser pool compartilhado...")
            pw = await async_playwright().start()
            _browser = await pw.chromium.launch(headless=True)

    page = await _browser.new_page()
    try:
        yield page
    finally:
        await page.close()


async def close_pool() -> None:
    """Shut down the shared browser pool."""
    global _browser
    if _browser is not None and _browser.is_connected():
        await _browser.close()
        _browser = None
        logger.info("Browser pool fechado.")
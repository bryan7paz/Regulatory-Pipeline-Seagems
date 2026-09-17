"""Document downloader with retry logic and shared browser pool."""

from __future__ import annotations

import asyncio

from core.config import logger

MAX_RETRIES = 3


async def download(url: str) -> bytes:
    """Fetch the raw content of a URL with automatic retry.

    Retries up to MAX_RETRIES times on transient failures.
    """
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if url.lower().endswith(".pdf"):
                return await _download_file(url)
            return await _download_html(url)
        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                logger.warning(
                    "Download tentativa %d/%d falhou: %s — retry em %ds",
                    attempt,
                    MAX_RETRIES,
                    exc,
                    attempt * 2,
                )
                await asyncio.sleep(attempt * 2)
            else:
                logger.error("Download falhou após %d tentativas: %s", MAX_RETRIES, exc)
    raise last_exc  # type: ignore[misc]


async def _download_file(url: str) -> bytes:
    import httpx

    headers = {"User-Agent": "regulatory-pipeline/1.0"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(url, timeout=120)
        resp.raise_for_status()
        return resp.content


async def _download_html(url: str) -> bytes:
    from core.browser import get_browser

    async with get_browser() as page:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        html = await page.content()
    return html.encode("utf-8")

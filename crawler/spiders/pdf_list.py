"""PDF listing spider for portals that index PDF documents directly."""
from __future__ import annotations

from urllib.parse import urljoin

from .base import BaseSpider, Item


class PdfListSpider(BaseSpider):
    """Extracts PDF links only (stricter than generic HTML list)."""

    async def fetch_items(self) -> list[Item]:
        from core.browser import get_browser
        from bs4 import BeautifulSoup

        async with get_browser() as page:
            await page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
            html = await page.content()

        soup = BeautifulSoup(html, "html.parser")
        items: list[Item] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.lower().endswith(".pdf"):
                continue
            full_url = urljoin(self.url, href)
            title = a.get_text(" ", strip=True) or href.rsplit("/", 1)[-1]
            if full_url in seen:
                continue
            seen.add(full_url)
            items.append(Item(title=title, url=full_url, source_id=self.source_id))
        return items
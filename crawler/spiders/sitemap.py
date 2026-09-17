"""Sitemap/RSS spider for portals exposing structured feeds."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from .base import BaseSpider, Item


class SitemapSpider(BaseSpider):
    """Parses sitemap.xml or RSS/Atom feeds."""

    async def fetch_items(self) -> list[Item]:
        import httpx

        headers = {"User-Agent": "regulatory-pipeline/1.0"}
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            resp = await client.get(self.url, timeout=60)
            resp.raise_for_status()
            content = resp.text

        items: list[Item] = []
        root = ET.fromstring(content)
        # Sitemap namespace handling
        if root.tag.endswith("urlset"):
            items = self._parse_sitemap(root)
        elif root.tag.endswith("rss") or root.tag == "rss":
            items = self._parse_rss(root)
        else:
            items = self._parse_any(root)
        return items

    def _parse_sitemap(self, root: ET.Element) -> list[Item]:
        entries = []
        for url in root:
            loc = url.find("{*}loc")
            if loc is None or not loc.text:
                continue
            lastmod = url.find("{*}lastmod")
            entries.append(
                Item(
                    title=loc.text.rsplit("/", 1)[-1],
                    url=loc.text,
                    published_date=lastmod.text if lastmod is not None else None,
                    source_id=self.source_id,
                )
            )
        return entries

    def _parse_rss(self, root: ET.Element) -> list[Item]:
        entries = []
        for item in root.iter("item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            pub = item.findtext("pubDate") or None
            if link:
                entries.append(Item(title=title, url=link, published_date=pub,
                                    source_id=self.source_id))
        return entries

    def _parse_any(self, root: ET.Element) -> list[Item]:
        # Fallback: any element with a url-like text
        entries = []
        for el in root.iter():
            if el.tag.endswith("loc") and el.text:
                entries.append(Item(title=el.text.rsplit("/", 1)[-1], url=el.text,
                                    source_id=self.source_id))
        return entries
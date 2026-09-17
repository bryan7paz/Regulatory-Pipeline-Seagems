"""Spider registry: maps a source config to a concrete spider instance."""
from __future__ import annotations

from typing import Any

from .base import BaseSpider
from .html_list import HtmlListSpider
from .pdf_list import PdfListSpider
from .sitemap import SitemapSpider
from .login import LoginSpider
from .adapters import ADAPTER_MAP

TYPE_MAP: dict[str, type[BaseSpider]] = {
    "html_list": HtmlListSpider,
    "pdf_list": PdfListSpider,
    "sitemap": SitemapSpider,
    "login": LoginSpider,
}


def get_spider(source: dict[str, Any]) -> BaseSpider:
    source_id = source.get("id", "")
    if source_id in ADAPTER_MAP:
        return ADAPTER_MAP[source_id](source)
    spider_type = source.get("type", "html_list")
    cls = TYPE_MAP.get(spider_type, HtmlListSpider)
    return cls(source)
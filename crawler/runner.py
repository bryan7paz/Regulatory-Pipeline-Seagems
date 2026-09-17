"""Orchestrates the crawl: detect new items and enqueue downloads."""
from __future__ import annotations

import asyncio
from typing import Any

from core.config import load_sources, logger
from core.browser import close_pool
from .downloader import download
from .spiders.base import Item
from .spiders.registry import get_spider
from . import storage


async def run_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    """Run a single source and return the newly enqueued records."""
    source_id = source.get("id", "")
    spider = get_spider(source)

    items: list[Item] = await spider.fetch_items()

    seen = storage.load_seen(source_id)
    new_records: list[dict[str, Any]] = []
    new_hashes: set[str] = set(seen)

    for it in items:
        d = it.to_dict()
        d["source_name"] = source.get("name", "")
        h = storage.item_hash(d)
        if h in seen:
            continue
        try:
            content = await download(it.url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Download falhou %s: %s", it.url, exc)
            continue
        record = storage.enqueue(d, content)
        if record:
            new_records.append(record)
            new_hashes.add(h)

    storage.save_seen(source_id, new_hashes)
    return new_records


async def run_all() -> list[dict[str, Any]]:
    """Run all configured sources and return every new record."""
    sources = load_sources()
    all_records: list[dict[str, Any]] = []
    try:
        for source in sources:
            source_id = source.get("id", "?")
            logger.info("Processando fonte: %s", source_id)
            try:
                records = await run_source(source)
            except Exception as exc:  # noqa: BLE001
                logger.error("Fonte %s falhou: %s", source_id, exc)
                records = []
            logger.info("  -> %d documento(s) novo(s)", len(records))
            all_records.extend(records)
    finally:
        await close_pool()
    return all_records


def run() -> list[dict[str, Any]]:
    """Synchronous entry point."""
    return asyncio.run(run_all())


if __name__ == "__main__":
    records = run()
    logger.info("Total de documentos novos: %d", len(records))
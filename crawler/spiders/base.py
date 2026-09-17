"""Base spider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    """A single document/item detected on a source page."""

    title: str
    url: str
    published_date: str | None = None
    source_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "published_date": self.published_date,
            "source_id": self.source_id,
            "extra": self.extra,
        }


class BaseSpider(ABC):
    """Common interface every spider must implement."""

    def __init__(self, source: dict[str, Any]) -> None:
        self.source = source
        self.source_id: str = source.get("id", "")
        self.url: str = source.get("url", "")

    @abstractmethod
    async def fetch_items(self) -> list[Item]:
        """Return the list of items currently published by the source."""
        raise NotImplementedError
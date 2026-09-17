"""Local persistence for crawler state and the pending download queue."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "state"
DATA_DIR = BASE_DIR.parent / "data"


def _ensure_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _state_path(source_id: str) -> Path:
    return STATE_DIR / f"{source_id}.json"


def load_seen(source_id: str) -> set[str]:
    """Return the set of item hashes already seen for a source."""
    path = _state_path(source_id)
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get("seen", []))


def save_seen(source_id: str, seen: set[str]) -> None:
    _ensure_dirs()
    _state_path(source_id).write_text(
        json.dumps({"seen": sorted(seen)}, indent=2), encoding="utf-8"
    )


def item_hash(item: dict[str, Any]) -> str:
    """Stable hash of an item identity (title + url)."""
    raw = f"{item.get('source_id', '')}|{item.get('title', '')}|{item.get('url', '')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def enqueue(item: dict[str, Any], content: bytes) -> dict[str, Any]:
    """Persist a downloaded document and metadata to the pending queue.

    Skips if the sha256 hash is already in the queue (deduplication).
    """
    _ensure_dirs()
    sha = hashlib.sha256(content).hexdigest()
    out_dir = DATA_DIR / item.get("source_id", "unknown")
    out_dir.mkdir(parents=True, exist_ok=True)

    url = item.get("url", "")
    ext = ".pdf" if url.lower().endswith(".pdf") else ".html"
    filename = f"{sha[:16]}{ext}"
    (out_dir / filename).write_bytes(content)

    queue_path = DATA_DIR / "queue.jsonl"
    if queue_path.exists():
        with queue_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("sha256") == sha:
                    return {}  # already queued

    record = {
        **item,
        "sha256": sha,
        "local_path": str(out_dir / filename),
        "content_type": "pdf" if ext == ".pdf" else "html",
    }
    with queue_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

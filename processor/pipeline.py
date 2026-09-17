"""End-to-end processing pipeline: queue -> extract -> LLM -> normalized record."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .extract import extract_from_file
from .gateway import generate_structured
from .normalizer import normalize
from .prompt_builder import build_prompt

QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "queue.jsonl"


def process_record(record: dict[str, Any]) -> dict[str, Any]:
    """Process a single queued record into a structured analysis dict."""
    text = extract_from_file(record["local_path"], record.get("content_type", "html"))
    system_prompt, user_prompt = build_prompt(text)
    raw = generate_structured(system_prompt, user_prompt)
    analysis = normalize(raw)

    result = analysis.model_dump()
    result.update(
        {
            "source_id": record.get("source_id", ""),
            "source_name": record.get("source_name", ""),
            "url_origem": record.get("url", ""),
            "documento_hash": record.get("sha256", ""),
        }
    )
    return result


def read_queue() -> list[dict[str, Any]]:
    if not QUEUE_PATH.exists():
        return []
    records = []
    with QUEUE_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def process_all() -> list[dict[str, Any]]:
    results = []
    for record in read_queue():
        try:
            results.append(process_record(record))
        except Exception as exc:  # noqa: BLE001
            print(f"[processor] error on {record.get('url')}: {exc}")
    return results


if __name__ == "__main__":
    out = process_all()
    print(json.dumps(out, ensure_ascii=False, indent=2))
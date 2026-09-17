"""End-to-end orchestration: crawl -> process -> persist to database.

Run with: python run_pipeline.py
"""
from __future__ import annotations

from crawler import runner
from process_queue import process_queue
from core.config import logger


def main() -> None:
    new_docs = runner.run()
    logger.info("[pipeline] %d novo(s) documento(s) baixado(s)", len(new_docs))

    if not new_docs:
        logger.info("[pipeline] nada novo; encerrando.")
        return

    saved = process_queue()
    logger.info("[pipeline] %d registro(s) salvos no banco", saved)


if __name__ == "__main__":
    main()
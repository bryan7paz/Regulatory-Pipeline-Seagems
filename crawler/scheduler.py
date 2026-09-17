"""APScheduler-based daily scheduler for the full pipeline.

Runs crawl → process → persist as a single job.
"""
from __future__ import annotations

import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler

from core.config import load_env, logger
from crawler.runner import run_all


def _full_pipeline() -> None:
    """Execute crawl + process + persist synchronously."""
    # 1. Crawl
    logger.info("[scheduler] iniciando crawl...")
    records = asyncio.run(run_all())
    logger.info("[scheduler] crawl concluído: %d documento(s) novo(s)", len(records))

    if not records:
        return

    # 2. Process + persist via process_queue
    import subprocess
    import sys
    try:
        result = subprocess.run(
            [sys.executable, "process_queue.py"],
            cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent),
            timeout=600,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error("[scheduler] process_queue falhou:\n%s", result.stderr)
        else:
            logger.info("[scheduler] process_queue concluído:\n%s", result.stdout)
    except subprocess.TimeoutExpired:
        logger.error("[scheduler] process_queue timeout (600s)")
    except Exception as exc:  # noqa: BLE001
        logger.error("[scheduler] erro ao rodar process_queue: %s", exc)


def main() -> None:
    env = load_env()
    hour = int(env.get("SCHEDULE_HOUR", "6"))
    timezone = env.get("SCHEDULE_TIMEZONE", "America/Sao_Paulo")

    scheduler = BlockingScheduler(timezone=timezone)
    scheduler.add_job(_full_pipeline, "cron", hour=hour, id="daily_pipeline")
    logger.info("[scheduler] pipeline diário agendado às %02d:00 (%s)", hour, timezone)
    scheduler.start()


if __name__ == "__main__":
    main()

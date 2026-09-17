"""Crawler configuration — re-exports from core.config for backward compatibility."""
from core.config import (  # noqa: F401
    BASE_DIR,
    CONFIG_DIR,
    load_env,
    load_prompt,
    load_sources,
    logger,
    validate_env,
)
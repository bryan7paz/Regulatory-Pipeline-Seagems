"""LLM gateway — dispatches to the active provider via core.llm_providers."""
from __future__ import annotations

from typing import Any

from core.config import logger
from core.llm_providers import generate_structured as _generate


def generate_structured(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """Call the active LLM and return parsed JSON.

    Delegates to core.llm_providers which handles provider selection,
    retry logic, and fallback chain.
    """
    return _generate(system_prompt, user_prompt)

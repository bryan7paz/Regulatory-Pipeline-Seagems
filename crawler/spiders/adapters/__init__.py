"""Spider adapters for individual regulatory portals.

When a portal requires custom parsing beyond the generic spiders,
add a dedicated adapter here and register it in ADAPTER_MAP.
"""

from .imodocs import ImodocsAdapter

ADAPTER_MAP = {
    "imodocs": ImodocsAdapter,
}

__all__ = ["ADAPTER_MAP", "ImodocsAdapter"]

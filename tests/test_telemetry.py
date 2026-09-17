"""Tests for api/telemetry.py — OpenTelemetry middleware."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

from api.telemetry import TelemetryMiddleware


class TestTelemetryMiddleware:
    def test_init(self):
        middleware = TelemetryMiddleware(MagicMock())
        assert middleware is not None

    def test_dispatch_calls_next(self):
        middleware = TelemetryMiddleware(MagicMock())
        request = MagicMock()
        request.url.path = "/test"
        request.headers = {}

        call_next = AsyncMock()
        call_next.return_value = MagicMock(status_code=200)

        import asyncio

        response = asyncio.run(middleware.dispatch(request, call_next))

        call_next.assert_called_once_with(request)
        assert response.status_code == 200

    def test_dispatch_records_duration(self):
        middleware = TelemetryMiddleware(MagicMock())
        request = MagicMock()
        request.url.path = "/slow"
        request.headers = {}

        async def slow_next(req):
            time.sleep(0.01)
            return MagicMock(status_code=200)

        import asyncio

        response = asyncio.run(middleware.dispatch(request, slow_next))
        assert response.status_code == 200

    def test_dispatch_handles_exception(self):
        middleware = TelemetryMiddleware(MagicMock())
        request = MagicMock()
        request.url.path = "/error"
        request.headers = {}

        async def failing_next(req):
            raise ValueError("test error")

        import asyncio

        try:
            asyncio.run(middleware.dispatch(request, failing_next))
            raise AssertionError()
        except ValueError:
            pass

"""FastAPI middleware for OpenTelemetry tracing."""
from __future__ import annotations

import time
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware that creates a span for each HTTP request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            from opentelemetry import trace
            from opentelemetry.trace import Status, StatusCode

            tracer = trace.get_tracer("fastapi")

            method = request.method
            path = request.url.path

            with tracer.start_span(
                f"HTTP {method} {path}",
                attributes={
                    "http.method": method,
                    "http.url": str(request.url),
                    "http.path": path,
                    "http.scheme": request.url.scheme,
                    "http.host": request.headers.get("host", ""),
                    "http.user_agent": request.headers.get("user-agent", ""),
                    "http.client_ip": request.client.host if request.client else "",
                },
            ) as span:
                start_time = time.time()

                try:
                    response = await call_next(request)
                    elapsed = time.time() - start_time

                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.elapsed_ms", round(elapsed * 1000, 2))

                    if response.status_code >= 400:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    else:
                        span.set_status(Status(StatusCode.OK))

                    return response

                except Exception as exc:
                    elapsed = time.time() - start_time
                    span.set_attribute("http.elapsed_ms", round(elapsed * 1000, 2))
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    span.record_exception(exc)
                    raise

        except ImportError:
            return await call_next(request)

"""OpenTelemetry observability — tracing and metrics."""
from __future__ import annotations

import os
from typing import Any

from core.config import load_env, logger


def setup_telemetry(app_name: str = "regulatory-pipeline") -> Any:
    """Configure OpenTelemetry with OTLP exporter.

    Returns the tracer provider, or None if OTel is not configured.
    """
    env = load_env()
    otlp_endpoint = env.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    otlp_enabled = env.get("OTEL_ENABLED", "false").lower() == "true"

    if not otlp_enabled and not otlp_endpoint:
        logger.info("OpenTelemetry desabilitado (defina OTEL_ENABLED=true)")
        return None

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME

        resource = Resource.create({SERVICE_NAME: app_name})
        provider = TracerProvider(resource=resource)

        # Console exporter (always on for debugging)
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

        # OTLP exporter (Datadog, Grafana, Jaeger, etc.)
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info("OpenTelemetry OTLP exporter configurado: %s", otlp_endpoint)
            except ImportError:
                logger.warning("opentelemetry-exporter-otlp não instalado")

        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry habilitado: %s", app_name)
        return provider

    except ImportError:
        logger.warning("OpenTelemetry não instalado. Instale: pip install opentelemetry-api opentelemetry-sdk")
        return None


def get_tracer(name: str = __name__) -> Any:
    """Get a tracer instance."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        return None


def trace_span(name: str, attributes: dict[str, Any] | None = None):
    """Context manager for creating a trace span."""
    tracer = get_tracer()
    if tracer is None:
        from contextlib import nullcontext
        return nullcontext()

    from opentelemetry.trace import Status, StatusCode

    class _SpanContext:
        def __init__(self, tracer, name, attrs):
            self.tracer = tracer
            self.name = name
            self.attrs = attrs or {}
            self.span = None

        def __enter__(self):
            self.span = self.tracer.start_span(self.name, attributes=self.attrs)
            return self.span

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.span:
                if exc_type:
                    self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                    self.span.record_exception(exc_val)
                self.span.end()
            return False

    return _SpanContext(tracer, name, attributes)

"""Observability & Tracing module for Agent Assessment Hub.

Provides OpenTelemetry instrumentation, Google Cloud Trace exporter,
PII-redacted structured JSON logging, and explicit intent/outcome audit tracking.
"""

import json
import logging
import time
from typing import Any, Callable, Dict, Optional
from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode

from src.guardrails import redact_pii

# Initialize OpenTelemetry Tracer Provider
try:
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(CloudTraceSpanExporter()))
    trace.set_tracer_provider(provider)
except Exception:
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

tracer = trace.get_tracer("agent-assessment-hub", "0.1.0")

# Configure Structured Logging with PII Redaction
logger = logging.getLogger("agent_hub")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler()

    class PiiRedactingJsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            raw_message = record.getMessage()
            sanitized_message = redact_pii(raw_message)
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": sanitized_message,
            }
            if hasattr(record, "intent"):
                log_data["intent"] = redact_pii(str(record.intent))
            if hasattr(record, "outcome"):
                log_data["outcome"] = redact_pii(str(record.outcome))
            if hasattr(record, "extra_fields"):
                log_data["extra"] = {k: redact_pii(str(v)) for k, v in record.extra_fields.items()}
            return json.dumps(log_data)

    handler.setFormatter(PiiRedactingJsonFormatter())
    logger.addHandler(handler)


def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Decorator to trace function execution with OpenTelemetry and PII-sanitized telemetry."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, redact_pii(str(v)))
                start_time = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("execution.duration_ms", duration_ms)
                    span.set_status(Status(StatusCode.OK))
                    logger.info(f"{name} completed successfully in {duration_ms:.2f}ms")
                    return result
                except Exception as e:
                    sanitized_err = redact_pii(str(e))
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, sanitized_err))
                    logger.error(f"Error in {name}: {sanitized_err}")
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, redact_pii(str(v)))
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("execution.duration_ms", duration_ms)
                    span.set_status(Status(StatusCode.OK))
                    logger.info(f"{name} completed successfully in {duration_ms:.2f}ms")
                    return result
                except Exception as e:
                    sanitized_err = redact_pii(str(e))
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, sanitized_err))
                    logger.error(f"Error in {name}: {sanitized_err}")
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

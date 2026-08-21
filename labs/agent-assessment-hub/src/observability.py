"""Observability & Tracing module for Agent Assessment Hub.

Provides OpenTelemetry instrumentation, Cloud Trace integration,
structured logging, and execution latency/token tracking.
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

# Initialize OpenTelemetry Tracer
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

# Configure Structured Logging
logger = logging.getLogger("agent_hub")
handler = logging.StreamHandler()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        return json.dumps(log_data)


handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Decorator to trace function execution with OpenTelemetry and structured logging."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, str(v))
                start_time = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("execution.duration_ms", duration_ms)
                    span.set_status(Status(StatusCode.OK))
                    logger.info(f"{name} completed successfully in {duration_ms:.2f}ms")
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    logger.error(f"Error in {name}: {str(e)}")
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, str(v))
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("execution.duration_ms", duration_ms)
                    span.set_status(Status(StatusCode.OK))
                    logger.info(f"{name} completed successfully in {duration_ms:.2f}ms")
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    logger.error(f"Error in {name}: {str(e)}")
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

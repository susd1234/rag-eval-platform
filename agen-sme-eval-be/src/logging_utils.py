"""
Logging utilities for enhanced inter-agent communication and request progress tracking
"""

import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Optional, Dict, Any
from functools import wraps
import json


# Context variable for tracking request correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)


class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        correlation_id = correlation_id_var.get()
        record.correlation_id = correlation_id or "no-correlation-id"
        return True


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with correlation IDs"""

    def format(self, record: logging.LogRecord) -> str:
        # Create custom timestamp in DDMMMYY_HHMMSS format
        import datetime

        dt = datetime.datetime.fromtimestamp(record.created)
        custom_timestamp = dt.strftime("%d%b%y_%H%M%S").upper()

        # Create structured log entry
        log_entry = {
            "timestamp": custom_timestamp,
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", "no-correlation-id"),
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "agent_name"):
            log_entry["agent_name"] = record.agent_name
        if hasattr(record, "metric"):
            log_entry["metric"] = record.metric
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "processing_time"):
            log_entry["processing_time"] = record.processing_time
        if hasattr(record, "model_name"):
            log_entry["model_name"] = record.model_name
        if hasattr(record, "response_length"):
            log_entry["response_length"] = record.response_length
        if hasattr(record, "evaluation_step"):
            log_entry["evaluation_step"] = record.evaluation_step

        # Include exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_enhanced_logging():
    """Setup enhanced logging configuration for the entire application"""

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with structured formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Add correlation filter and formatter
    correlation_filter = CorrelationFilter()
    structured_formatter = StructuredFormatter()

    console_handler.addFilter(correlation_filter)
    console_handler.setFormatter(structured_formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Set specific logger levels
    logging.getLogger("src.orchestrator_factory").setLevel(logging.INFO)
    logging.getLogger("src.agents").setLevel(logging.INFO)
    logging.getLogger("src.proxy_client").setLevel(logging.INFO)
    logging.getLogger("src.api").setLevel(logging.INFO)

    # Suppress overly verbose third-party loggers
    logging.getLogger("litellm").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def set_correlation_id(correlation_id: str):
    """Set correlation ID for the current context"""
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID"""
    return correlation_id_var.get()


def generate_correlation_id() -> str:
    """Generate a new correlation ID"""
    return f"req_{uuid.uuid4().hex[:12]}"


def log_agent_communication(
    logger: logging.Logger,
    action: str,
    agent_name: str,
    metric: str,
    request_id: str,
    details: Optional[Dict[str, Any]] = None,
):
    """Log agent communication events with structured data"""
    extra = {
        "agent_name": agent_name,
        "metric": metric,
        "request_id": request_id,
        "evaluation_step": action,
    }

    if details:
        extra.update(details)

    message = f"Agent Communication - {action}: {agent_name} ({metric}) - Request: {request_id}"

    # Add timeout configuration context for debugging
    if action == "message_send_start":
        from src.config import get_settings

        settings = get_settings()
        extra["timeout_threshold"] = settings.agent_communication_timeout
        extra["llm_timeout_threshold"] = settings.llm_request_timeout
        extra["max_retry_attempts"] = settings.agent_retry_attempts

    if details:
        message += f" - Details: {details}"

    logger.info(message, extra=extra)


def log_llm_interaction(
    logger: logging.Logger,
    action: str,
    model_name: str,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    processing_time: Optional[float] = None,
):
    """Log LLM interaction events with structured data"""
    extra = {"model_name": model_name, "evaluation_step": f"llm_{action}"}

    if processing_time:
        extra["processing_time"] = processing_time

    if response_data and "content_length" in response_data:
        extra["response_length"] = response_data["content_length"]

    message = f"LLM Interaction - {action}: {model_name}"

    if request_data:
        message += f" - Request: {request_data}"

    if response_data:
        message += f" - Response: {response_data}"

    if processing_time:
        message += f" - Time: {processing_time:.3f}s"

    logger.info(message, extra=extra)


def log_evaluation_progress(
    logger: logging.Logger,
    step: str,
    evaluation_id: str,
    progress_data: Optional[Dict[str, Any]] = None,
):
    """Log evaluation progress with structured data"""
    extra = {"request_id": evaluation_id, "evaluation_step": step}

    if progress_data:
        extra.update(progress_data)

    message = f"Evaluation Progress - {step}: {evaluation_id}"

    if progress_data:
        message += f" - Data: {progress_data}"

    logger.info(message, extra=extra)


def log_timeout_warning(
    logger: logging.Logger,
    component: str,
    operation: str,
    elapsed_time: float,
    threshold: float,
    context: Optional[Dict[str, Any]] = None,
):
    """Log timeout warnings when operations approach timeout thresholds"""
    extra = {
        "component": component,
        "operation": operation,
        "elapsed_time": elapsed_time,
        "timeout_threshold": threshold,
        "timeout_utilization": (elapsed_time / threshold) * 100,
        "evaluation_step": "timeout_warning",
    }

    if context:
        extra.update(context)

    message = f"Timeout Warning - {component} {operation}: {elapsed_time:.2f}s/{threshold:.2f}s ({(elapsed_time/threshold)*100:.1f}%)"

    if elapsed_time > threshold * 0.8:  # Warning at 80% of timeout
        logger.warning(message, extra=extra)
    else:
        logger.info(message, extra=extra)


def log_performance_metric(
    logger: logging.Logger,
    metric_name: str,
    value: float,
    unit: str = "seconds",
    context: Optional[Dict[str, Any]] = None,
):
    """Log performance metrics with structured data"""
    extra = {
        "evaluation_step": f"performance_{metric_name}",
        "processing_time": value if unit == "seconds" else None,
    }

    if context:
        extra.update(context)

    message = f"Performance Metric - {metric_name}: {value} {unit}"

    if context:
        message += f" - Context: {context}"

    logger.info(message, extra=extra)


def timing_decorator(operation_name: str):
    """Decorator to automatically log operation timing"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(func.__module__)

            try:
                result = await func(*args, **kwargs)
                processing_time = time.time() - start_time

                log_performance_metric(
                    logger,
                    operation_name,
                    processing_time,
                    context={"function": func.__name__, "status": "success"},
                )

                return result
            except Exception as e:
                processing_time = time.time() - start_time

                log_performance_metric(
                    logger,
                    operation_name,
                    processing_time,
                    context={
                        "function": func.__name__,
                        "status": "error",
                        "error": str(e),
                    },
                )

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(func.__module__)

            try:
                result = func(*args, **kwargs)
                processing_time = time.time() - start_time

                log_performance_metric(
                    logger,
                    operation_name,
                    processing_time,
                    context={"function": func.__name__, "status": "success"},
                )

                return result
            except Exception as e:
                processing_time = time.time() - start_time

                log_performance_metric(
                    logger,
                    operation_name,
                    processing_time,
                    context={
                        "function": func.__name__,
                        "status": "error",
                        "error": str(e),
                    },
                )

                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class LoggingContext:
    """Context manager for setting up logging context for a request"""

    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or generate_correlation_id()
        self.previous_correlation_id = None

    def __enter__(self):
        self.previous_correlation_id = get_correlation_id()
        set_correlation_id(self.correlation_id)
        return self.correlation_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_correlation_id(self.previous_correlation_id)


def create_logger_with_context(name: str) -> logging.Logger:
    """Create a logger with enhanced context support"""
    logger = logging.getLogger(name)
    return logger

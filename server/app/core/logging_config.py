import logging
import re
import sys
import structlog

# PII Redaction Regex Patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def pii_scrub_processor(logger, method_name, event_dict):
    """Redact sensitive PII data before persisting log output."""
    for key, val in event_dict.items():
        if isinstance(val, str):
            val = EMAIL_REGEX.sub("[REDACTED_EMAIL]", val)
            val = PHONE_REGEX.sub("[REDACTED_PHONE]", val)
            val = SSN_REGEX.sub("[REDACTED_SSN]", val)
            event_dict[key] = val
    return event_dict


def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            pii_scrub_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()

import logging
import os
import time
from logging.config import dictConfig


DEFAULT_LOG_LEVEL = "INFO"

SUPPORTED_LOG_LEVELS = {
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
}


class UtcFormatter(logging.Formatter):
    """
    Format application timestamps using UTC.
    """

    converter = time.gmtime


def resolve_log_level(
    value: str | None,
) -> str:
    """
    Normalize an environment-provided logging level.

    Invalid or missing values safely fall back to INFO.
    """

    if not value:
        return DEFAULT_LOG_LEVEL

    normalized_value = value.strip().upper()

    if normalized_value not in SUPPORTED_LOG_LEVELS:
        return DEFAULT_LOG_LEVEL

    return normalized_value


def configure_logging() -> None:
    """
    Configure consistent application and Uvicorn logging.

    The formatter intentionally excludes request bodies,
    authorization headers, tokens, and user-provided data.
    """

    log_level = resolve_log_level(
        os.getenv("LOG_LEVEL")
    )

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "careerpilot": {
                    "()": (
                        "app.logging_config."
                        "UtcFormatter"
                    ),
                    "format": (
                        "%(asctime)sZ "
                        "%(levelname)s "
                        "%(name)s "
                        "%(message)s"
                    ),
                    "datefmt": (
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": (
                        "logging.StreamHandler"
                    ),
                    "formatter": "careerpilot",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "handlers": [
                    "console",
                ],
                "level": log_level,
            },
            "loggers": {
                "uvicorn": {
                    "handlers": [
                        "console",
                    ],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": [
                        "console",
                    ],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": [
                        "console",
                    ],
                    "level": log_level,
                    "propagate": False,
                },
            },
        }
    )
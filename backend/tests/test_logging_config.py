from app.logging_config import (
    DEFAULT_LOG_LEVEL,
    resolve_log_level,
)


def test_resolve_log_level_normalizes_value():
    assert (
        resolve_log_level(" debug ")
        == "DEBUG"
    )


def test_resolve_log_level_accepts_supported_levels():
    supported_levels = [
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG",
    ]

    for level in supported_levels:
        assert (
            resolve_log_level(level)
            == level
        )


def test_resolve_log_level_uses_safe_default():
    assert (
        resolve_log_level(None)
        == DEFAULT_LOG_LEVEL
    )

    assert (
        resolve_log_level("")
        == DEFAULT_LOG_LEVEL
    )

    assert (
        resolve_log_level("verbose")
        == DEFAULT_LOG_LEVEL
    )
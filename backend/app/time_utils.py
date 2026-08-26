from datetime import (
    UTC,
    datetime,
)


def utc_now_naive() -> datetime:
    """
    Return the current UTC time as a naive datetime.

    CareerPilot currently stores timestamps in MySQL
    DATETIME columns, which do not preserve timezone
    information. This helper keeps that database
    contract while avoiding datetime.utcnow().
    """

    return datetime.now(
        UTC
    ).replace(
        tzinfo=None
    )
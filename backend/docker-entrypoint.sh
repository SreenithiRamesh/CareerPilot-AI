#!/bin/sh

set -eu

echo "Waiting for the CareerPilot database..."

python - <<'PY'
import os
import socket
import time
from urllib.parse import urlparse


database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not configured."
    )

parsed_url = urlparse(database_url)

host = parsed_url.hostname or "mysql"
port = parsed_url.port or 3306

maximum_attempts = 60
retry_delay_seconds = 2

for attempt in range(1, maximum_attempts + 1):
    try:
        with socket.create_connection(
            (host, port),
            timeout=3,
        ):
            print(
                f"Database is available at "
                f"{host}:{port}."
            )
            break

    except OSError:
        print(
            f"Database is not ready "
            f"({attempt}/{maximum_attempts})."
        )
        time.sleep(retry_delay_seconds)

else:
    raise RuntimeError(
        "Database did not become available "
        "within the expected time."
    )
PY

echo "Applying database migrations..."

alembic upgrade head

echo "Starting CareerPilot API..."

exec "$@"
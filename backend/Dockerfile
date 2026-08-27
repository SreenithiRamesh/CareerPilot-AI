FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install --requirement requirements.txt

RUN useradd \
    --create-home \
    --shell /bin/bash \
    careerpilot

COPY --chown=careerpilot:careerpilot alembic.ini ./alembic.ini
COPY --chown=careerpilot:careerpilot alembic ./alembic
COPY --chown=careerpilot:careerpilot app ./app
COPY --chown=careerpilot:careerpilot docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p /app/chroma_db \
    && chown -R careerpilot:careerpilot /app/chroma_db

USER careerpilot

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
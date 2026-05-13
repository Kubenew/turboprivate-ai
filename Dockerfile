FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml .
COPY turbo/ turbo/
COPY worker/ worker/

RUN pip install --no-cache-dir ".[full]"

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY turbo/ turbo/
COPY worker/ worker/

RUN useradd -r -s /bin/false turbo
USER turbo

EXPOSE 8000

CMD ["uvicorn", "turbo.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

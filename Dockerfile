FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e ".[all]"

COPY turbo/ turbo/
COPY worker/ worker/

EXPOSE 8000

CMD ["uvicorn", "turbo.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

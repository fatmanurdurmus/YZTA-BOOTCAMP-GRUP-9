FROM python:3.12-slim

WORKDIR /app

COPY apps/backend/pyproject.toml ./
COPY apps/backend/alembic.ini ./
COPY apps/backend/alembic ./alembic
COPY apps/backend/src ./src

RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 1000 carbonpilot && chown -R carbonpilot:carbonpilot /app
USER carbonpilot

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn carbonpilot.main:app --host 0.0.0.0 --port 8000"]
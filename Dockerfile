FROM ghcr.io/astral-sh/uv:0.7-python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev

COPY . /app/

ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port $PORT"]

# Backend image: FastAPI app + AI Customer Support Worker (T059).
# Debian-slim + uv (installed via pip for a reproducible image) from the lockfile.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

# Install dependency tree + the local project (src layout exposes `main`).
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY data ./data

# --no-dev: runtime image only (ruff/pytest/mypy stay out of the image).
RUN uv sync --no-dev

EXPOSE 8000

# Default command; compose overrides with --reload for local iteration.
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
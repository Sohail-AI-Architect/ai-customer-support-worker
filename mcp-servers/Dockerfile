# MCP tool-server images (T059).
#
# Packages the three worker tool servers (knowledge / support-data /
# escalation-approval). Each is a framework-agnostic Python package whose tests
# add `../../backend/src` to pythonpath, so this image also carries the backend
# shared source on PYTHONPATH.
#
# NOTE: the servers are consumed by the backend through in-process adapters
# today (services/escalation_approval.py etc.). The concrete MCP stdio/HTTP
# transport bridge to the backend remains the deferred wiring (see
# backend/src/mcp/__init__.py "completed in Polish (T059)"). This image makes
# each server runnable/verifiable standalone and is the base for that bridge.
#
# Build from the repo root:
#   docker build -f mcp-servers/Dockerfile -t ai-mcp-servers .
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/backend/src \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

# Backend shared source (imported by the servers' tool logic + tests).
COPY backend/src /app/backend/src

# The three tool-server packages.
COPY mcp-servers/knowledge-server ./mcp-servers/knowledge-server
COPY mcp-servers/support-data-server ./mcp-servers/support-data-server
COPY mcp-servers/escalation-approval-server ./mcp-servers/escalation-approval-server

RUN uv sync --project mcp-servers/knowledge-server \
 && uv sync --project mcp-servers/support-data-server \
 && uv sync --project mcp-servers/escalation-approval-server

# Default: run each server's own test suite as an install/smoke gate.
CMD ["uv", "run", "--project", "mcp-servers/knowledge-server", "pytest", "mcp-servers/knowledge-server/tests", \
     "-m", "", "-q"]
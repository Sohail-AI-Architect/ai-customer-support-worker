"""FastAPI application entrypoint for the AI Customer Support Worker backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from api import agent_approvals, agent_escalations, chat, tickets
from api.errors import (
    AppError,
    handle_app_error,
    handle_authz_error,
    handle_http_error,
    handle_unhandled,
)
from config import get_settings
from domain.authorization import AuthorizationError
from services.observability import configure_logging, new_trace_id

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    request.state.trace_id = new_trace_id()
    response = await call_next(request)
    response.headers["X-Trace-Id"] = request.state.trace_id
    return response


app.add_exception_handler(AppError, handle_app_error)
app.add_exception_handler(AuthorizationError, handle_authz_error)
app.add_exception_handler(StarletteHTTPException, handle_http_error)
app.add_exception_handler(Exception, handle_unhandled)

app.include_router(chat.router)
app.include_router(tickets.router)
app.include_router(agent_escalations.router)
app.include_router(agent_approvals.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}

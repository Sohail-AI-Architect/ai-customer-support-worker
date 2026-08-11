"""API error envelope (plan Section 17, T016).

All errors return JSON: {error, message, trace_id}.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from domain.authorization import AuthorizationError
from services.observability import new_trace_id


class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


async def error_handlers() -> None:
    """Registered in main.py."""


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else new_trace_id()
    return JSONResponse(
        status_code=exc.status,
        content={"error": exc.code, "message": exc.message, "trace_id": trace_id},
    )


async def handle_authz_error(request: Request, exc: AuthorizationError) -> JSONResponse:
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else new_trace_id()
    return JSONResponse(
        status_code=403,
        content={"error": "unauthorized", "message": str(exc), "trace_id": trace_id},
    )


async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else new_trace_id()
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": str(exc.detail), "trace_id": trace_id},
    )


async def handle_unhandled(request: Request, exc: Exception) -> JSONResponse:
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else new_trace_id()
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal",
            "message": "An internal error occurred.",
            "trace_id": trace_id,
        },
    )

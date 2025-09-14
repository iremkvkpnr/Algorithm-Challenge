"""Exception handlers for VRP API."""

from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse

from .error_codes import ErrorCode
from .error_messages import ErrorMessage
from .vrp_exceptions import VRPException
from ..utils.logger import get_service_logger

logger = get_service_logger()


def create_error_response(error_code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None, 
                         request_id: Optional[str] = None) -> Dict[str, Any]:
    resp = {
        "error": {
            "code": error_code.value,
            "message": message,
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
            )) if logger.handlers else None
        }
    }
    
    if details:
        resp["error"]["details"] = details
    
    if request_id:
        resp["error"]["request_id"] = request_id
    
    return resp


def get_status_code_for_error(error_code: ErrorCode) -> int:
    status_map = {
        ErrorCode.VALIDATION_ERROR: 400,
        ErrorCode.TIMEOUT_ERROR: 408,
        ErrorCode.SOLVER_ERROR: 422,
        ErrorCode.SOLUTION_ERROR: 422,
        ErrorCode.DATABASE_ERROR: 503,
        ErrorCode.INTERNAL_ERROR: 500,
    }
    return status_map.get(error_code, 500)


async def vrp_exception_handler(request: Request, exc: VRPException) -> JSONResponse:
    logger.error(f"{exc.error_code.value} - {exc.message}", extra={
        "error_code": exc.error_code.value,
        "details": exc.details,
        "request_path": request.url.path
    })
    
    status_code = get_status_code_for_error(exc.error_code)
    request_id = getattr(request.state, 'request_id', None)
    
    return JSONResponse(
        status_code=status_code,
        content=create_error_response(exc.error_code, exc.message, exc.details, request_id)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {type(exc).__name__} - {exc}", extra={
        "exception_type": type(exc).__name__,
        "request_path": request.url.path
    }, exc_info=True)
    
    request_id = getattr(request.state, 'request_id', None)
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            ErrorCode.INTERNAL_ERROR, 
            ErrorMessage.INTERNAL_ERROR, 
            {"exception_type": type(exc).__name__},
            request_id
        )
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Validation error: {exc}", extra={
        "request_path": request.url.path,
        "validation_errors": str(exc)
    })
    
    request_id = getattr(request.state, 'request_id', None)
    
    return JSONResponse(
        status_code=400,
        content=create_error_response(
            ErrorCode.VALIDATION_ERROR,
            ErrorMessage.VALIDATION_ERROR,
            {"validation_errors": str(exc)},
            request_id
        )
    )
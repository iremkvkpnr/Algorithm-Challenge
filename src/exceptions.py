"""Custom exceptions and error handling for VRP API."""

import logging
from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class VRPException(Exception):
    def __init__(self, message: str, error_code: str = "VRP_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class VRPValidationError(VRPException):
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class VRPSolverError(VRPException):
    def __init__(self, message: str, solver_details: Optional[str] = None):
        self.solver_details = solver_details
        super().__init__(message, "SOLVER_ERROR")


class VRPTimeoutError(VRPException):
    def __init__(self, message: str = "Solver timeout exceeded"):
        super().__init__(message, "TIMEOUT_ERROR")


def create_error_response(error_code: str, message: str, details: Optional[Dict[str, Any]] = None):
    resp = {"error": {"code": error_code, "message": message}}
    if details:
        resp["error"]["details"] = details
    return resp


async def vrp_exception_handler(request: Request, exc: VRPException):
    logger.error(f"{exc.error_code} - {exc.message}")
    status = 400 if isinstance(exc, VRPValidationError) else 500
    if isinstance(exc, VRPTimeoutError):
        status = 408

    details = {}
    if isinstance(exc, VRPValidationError) and exc.field:
        details["field"] = exc.field
    elif isinstance(exc, VRPSolverError) and exc.solver_details:
        details["solver_details"] = exc.solver_details

    return JSONResponse(status_code=status, content=create_error_response(exc.error_code, exc.message, details or None))


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled: {type(exc).__name__} - {exc}")
    return JSONResponse(status_code=500, content=create_error_response("INTERNAL_ERROR", "Internal server error"))


async def validation_exception_handler(request: Request, exc: Exception):
    logger.error(f"Validation: {exc}")
    return JSONResponse(
        status_code=400,
        content=create_error_response("VALIDATION_ERROR", "Invalid input data", {"validation_errors": str(exc)})
    )

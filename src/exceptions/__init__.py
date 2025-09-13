"""Exception handling system for VRP API."""

from .error_codes import ErrorCode
from .error_messages import ErrorMessage
from .vrp_exceptions import (
    VRPException,
    VRPValidationError,
    VRPSolverError,
    VRPTimeoutError,
    VRPDatabaseError
)
from .handlers import (
    create_error_response,
    get_status_code_for_error,
    vrp_exception_handler,
    general_exception_handler,
    validation_exception_handler
)

__all__ = [
    'ErrorCode',
    'ErrorMessage',
    'VRPException',
    'VRPValidationError',
    'VRPSolverError',
    'VRPTimeoutError',
    'VRPDatabaseError',
    'create_error_response',
    'get_status_code_for_error',
    'vrp_exception_handler',
    'general_exception_handler',
    'validation_exception_handler'
]
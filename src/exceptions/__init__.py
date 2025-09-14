"""Exception handling system for VRP API."""

from .error_codes import ErrorCode
from .error_messages import ErrorMessage
from .vrp_exceptions import (
    VRPException,
    VRPError,
    VRPSystemError
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
    'VRPError',
    'VRPSystemError',
    'create_error_response',
    'get_status_code_for_error',
    'vrp_exception_handler',
    'general_exception_handler',
    'validation_exception_handler'
]
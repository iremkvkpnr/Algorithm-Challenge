"""VRP-specific exception classes."""

from typing import Any, Dict, Optional
from .error_codes import ErrorCode
from .error_messages import ErrorMessage


class VRPException(Exception):
    
    def __init__(self, error_code: ErrorCode, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.details = details or {}
        
        if message is None:
            message = getattr(ErrorMessage, error_code.name, error_code.value)
        
        if self.details and '{' in message:
            try:
                message = message.format(**self.details)
            except KeyError:
                pass
        
        self.message = message
        super().__init__(message)


class VRPValidationError(VRPException):
    
    def __init__(self, error_code: ErrorCode = ErrorCode.VALIDATION_ERROR, 
                 message: Optional[str] = None, field: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.field = field
        if field and details is None:
            details = {'field': field}
        elif field and details:
            details['field'] = field
        super().__init__(error_code, message, details)


class VRPSolverError(VRPException):
    
    def __init__(self, error_code: ErrorCode = ErrorCode.SOLVER_ERROR, 
                 message: Optional[str] = None, solver_details: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.solver_details = solver_details
        if solver_details and details is None:
            details = {'solver_details': solver_details}
        elif solver_details and details:
            details['solver_details'] = solver_details
        super().__init__(error_code, message, details)


class VRPTimeoutError(VRPException):
    
    def __init__(self, message: Optional[str] = None, timeout_seconds: Optional[int] = None):
        details = {'timeout_seconds': timeout_seconds} if timeout_seconds else None
        super().__init__(ErrorCode.TIMEOUT_ERROR, message, details)


class VRPDatabaseError(VRPException):
    
    def __init__(self, error_code: ErrorCode, message: Optional[str] = None, 
                 operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if operation and details is None:
            details = {'operation': operation}
        elif operation and details:
            details['operation'] = operation
        super().__init__(error_code, message, details)
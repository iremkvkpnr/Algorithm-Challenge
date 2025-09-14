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


class VRPError(VRPException):
    
    def __init__(self, error_code: ErrorCode = ErrorCode.VALIDATION_ERROR, 
                 message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code, message, details)


class VRPSystemError(VRPException):
    
    def __init__(self, error_code: ErrorCode = ErrorCode.INTERNAL_ERROR, 
                 message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(error_code, message, details)
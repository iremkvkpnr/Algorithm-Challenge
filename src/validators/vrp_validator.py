"""Main VRP validator that coordinates all validation operations."""

from typing import Dict
from ..schemas.request_models import VRPInput
from ..schemas.response_models import Route
from .business_validator import BusinessValidator
from ..exceptions import VRPError
from ..utils.logger import get_service_logger

logger = get_service_logger()


class VRPValidator:
    
    def __init__(self):
        self.business_validator = BusinessValidator()
    
    def validate_request(self, data: VRPInput) -> None:
        
        try:
            BusinessValidator.validate_business_rules(data)
            
        except VRPError as e:
            logger.error(f"Validation failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during validation: {str(e)}")
            raise VRPError(
                "VALIDATION_ERROR",
                f'Unexpected validation error: {str(e)}'
            )
    
    def validate_solution(self, routes: Dict[str, Route], data: VRPInput) -> None:
      
        try:
            BusinessValidator.validate_solution(routes, data)
            
        except VRPError as e:
            logger.error(f"Solution validation failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during solution validation: {str(e)}")
            raise VRPError(
                "SOLUTION_VALIDATION_ERROR",
                f'Unexpected solution validation error: {str(e)}'
            )
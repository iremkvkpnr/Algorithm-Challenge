"""Main VRP validator that coordinates all validation operations."""

from typing import Dict
from ..schemas.input import VRPInputDTO
from ..models.domain import VRPProblem, Route
from .input_validator import InputValidator
from .business_validator import BusinessValidator
from ..exceptions import VRPValidationError
import logging

logger = logging.getLogger(__name__)


class VRPValidator:
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.business_validator = BusinessValidator()
    
    def validate_request(self, data: VRPInputDTO) -> None:
        
        logger.info("Starting VRP request validation")
        
        try:
            logger.debug("Validating basic input structure")
            self.input_validator.validate_basic_input(data)
            
            logger.debug("Validating business rules")
            self.business_validator.validate_business_rules(data)
            
            logger.info("VRP request validation completed successfully")
            
        except VRPValidationError as e:
            logger.error(f"Validation failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during validation: {str(e)}")
            raise VRPValidationError(
                "VALIDATION_ERROR",
                details={'reason': f'Unexpected validation error: {str(e)}'}
            )
    
    def validate_solution(self, routes: Dict[str, Route], problem: VRPProblem) -> None:
      
        logger.info("Starting VRP solution validation")
        
        try:
            self.business_validator.validate_solution(routes, problem)
            logger.info("VRP solution validation completed successfully")
            
        except VRPValidationError as e:
            logger.error(f"Solution validation failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during solution validation: {str(e)}")
            raise VRPValidationError(
                "SOLUTION_VALIDATION_ERROR",
                details={'reason': f'Unexpected solution validation error: {str(e)}'}
            )
"""Input validation for VRP API requests."""

from typing import List, Optional, Any, Dict
from ..exceptions import VRPValidationError, ErrorCode
from ..schemas.input import VRPInputDTO, VehicleDTO, JobDTO


class InputValidator:
    
    @staticmethod
    def validate_vehicle(vehicle: VehicleDTO) -> None:
        if vehicle.start_index < 0:
            raise VRPValidationError(
                ErrorCode.INVALID_VEHICLE_DATA,
                details={
                    'vehicle_id': vehicle.id,
                    'field': 'start_index',
                    'value': vehicle.start_index,
                    'reason': 'start_index cannot be negative'
                }
            )
    
    @staticmethod
    def validate_job(job: JobDTO) -> None:
        if job.location_index < 0:
            raise VRPValidationError(
                ErrorCode.INVALID_JOB_DATA,
                details={
                    'job_id': job.id,
                    'field': 'location_index',
                    'value': job.location_index,
                    'reason': 'location_index cannot be negative'
                }
            )
        
        if job.service is not None and job.service < 0:
            raise VRPValidationError(
                ErrorCode.INVALID_JOB_DATA,
                details={
                    'job_id': job.id,
                    'field': 'service',
                    'value': job.service,
                    'reason': 'service time cannot be negative'
                }
            )
    
    @staticmethod
    def validate_matrix(matrix: List[List[int]]) -> None:
        """Validate distance matrix."""
        if not matrix:
            raise VRPValidationError(
                ErrorCode.INVALID_MATRIX_DATA,
                details={'reason': 'Matrix cannot be empty'}
            )
        
        n = len(matrix)
        for i, row in enumerate(matrix):
            if len(row) != n:
                raise VRPValidationError(
                    ErrorCode.INVALID_MATRIX_DATA,
                    details={
                        'reason': 'Matrix must be square',
                        'expected_size': n,
                        'row_index': i,
                        'actual_row_size': len(row)
                    }
                )
            
            for j, distance in enumerate(row):
                if distance < 0:
                    raise VRPValidationError(
                        ErrorCode.INVALID_MATRIX_DATA,
                        details={
                            'reason': 'Distance cannot be negative',
                            'row': i,
                            'col': j,
                            'value': distance
                        }
                    )
    
    @classmethod
    def validate_basic_input(cls, data: VRPInputDTO) -> None:
        if not data.vehicles:
            raise VRPValidationError(
                ErrorCode.INVALID_VEHICLE_DATA,
                details={'reason': 'No vehicles provided'}
            )
        
        for vehicle in data.vehicles:
            cls.validate_vehicle(vehicle)
        
        for job in data.jobs:
            cls.validate_job(job)
        
        cls.validate_matrix(data.matrix)
"""Business logic validation for VRP API."""

from typing import List, Dict, Set
from ..exceptions import VRPValidationError, ErrorCode
from ..schemas.input import VRPInputDTO
from ..models.domain import VRPProblem, Route


class BusinessValidator:
    
    @staticmethod
    def validate_location_indices(data: VRPInputDTO) -> None:
        matrix_size = len(data.matrix)
        
        for vehicle in data.vehicles:
            if vehicle.start_index >= matrix_size:
                raise VRPValidationError(
                    ErrorCode.INVALID_LOCATION_INDEX,
                    details={
                        'vehicle_id': vehicle.id,
                        'index': vehicle.start_index,
                        'valid_range': f'0..{matrix_size-1}',
                        'matrix_size': matrix_size
                    }
                )
        
        for job in data.jobs:
            if job.location_index >= matrix_size:
                raise VRPValidationError(
                    ErrorCode.INVALID_LOCATION_INDEX,
                    details={
                        'job_id': job.id,
                        'index': job.location_index,
                        'valid_range': f'0..{matrix_size-1}',
                        'matrix_size': matrix_size
                    }
                )
    
    @staticmethod
    def validate_vehicle_capacity_constraints(data: VRPInputDTO) -> None:
        for vehicle in data.vehicles:
            if vehicle.capacity:
                vehicle_capacity = vehicle.capacity[0]
                
                total_demand = sum(
                    job.delivery[0] if job.delivery else 1 
                    for job in data.jobs
                )
                
                if vehicle_capacity < total_demand and len(data.vehicles) == 1:
                    raise VRPValidationError(
                        ErrorCode.CAPACITY_EXCEEDED,
                        details={
                            'vehicle_id': vehicle.id,
                            'vehicle_capacity': vehicle_capacity,
                            'total_demand': total_demand,
                            'reason': 'Single vehicle cannot handle total demand'
                        }
                    )
    
    @staticmethod
    def validate_unique_ids(data: VRPInputDTO) -> None:
        vehicle_ids = [v.id for v in data.vehicles]
        if len(vehicle_ids) != len(set(vehicle_ids)):
            duplicates = [vid for vid in vehicle_ids if vehicle_ids.count(vid) > 1]
            raise VRPValidationError(
                ErrorCode.INVALID_VEHICLE_DATA,
                details={
                    'reason': 'Vehicle IDs must be unique',
                    'duplicate_ids': list(set(duplicates))
                }
            )
        
        job_ids = [j.id for j in data.jobs]
        if len(job_ids) != len(set(job_ids)):
            duplicates = [jid for jid in job_ids if job_ids.count(jid) > 1]
            raise VRPValidationError(
                ErrorCode.INVALID_JOB_DATA,
                details={
                    'reason': 'Job IDs must be unique',
                    'duplicate_ids': list(set(duplicates))
                }
            )
    
    @staticmethod
    def validate_route_assignment(routes: Dict[str, Route], problem: VRPProblem) -> None:
        assigned_jobs = []
        for route in routes.values():
            assigned_jobs.extend(route.jobs)
        
        expected_jobs = set(job.id for job in problem.jobs)
        actual_jobs = set(assigned_jobs)
        
        missing_jobs = expected_jobs - actual_jobs
        if missing_jobs:
            raise VRPValidationError(
                ErrorCode.INVALID_ROUTE_ASSIGNMENT,
                details={
                    'reason': 'Some jobs are not assigned to any route',
                    'missing_jobs': list(missing_jobs),
                    'total_jobs': len(expected_jobs),
                    'assigned_jobs': len(actual_jobs)
                }
            )
        
        if len(assigned_jobs) != len(actual_jobs):
            duplicates = [jid for jid in assigned_jobs if assigned_jobs.count(jid) > 1]
            raise VRPValidationError(
                ErrorCode.INVALID_ROUTE_ASSIGNMENT,
                details={
                    'reason': 'Some jobs are assigned to multiple routes',
                    'duplicate_jobs': list(set(duplicates))
                }
            )
    
    @staticmethod
    def validate_route_capacity(routes: Dict[str, Route], problem: VRPProblem) -> None:
        for vehicle_id, route in routes.items():
            vehicle = next((v for v in problem.vehicles if str(v.id) == vehicle_id), None)
            if not vehicle or not vehicle.capacity:
                continue
            
            vehicle_capacity = vehicle.capacity[0]
            route_demand = sum(
                job.delivery[0] if job.delivery else 0 
                for job in problem.jobs 
                if job.id in route.jobs
            )
            
            if route_demand > vehicle_capacity:
                raise VRPValidationError(
                    ErrorCode.CAPACITY_EXCEEDED,
                    details={
                        'vehicle_id': vehicle.id,
                        'route_demand': route_demand,
                        'vehicle_capacity': vehicle_capacity,
                        'jobs_in_route': route.jobs
                    }
                )
    
    @classmethod
    def validate_business_rules(cls, data: VRPInputDTO) -> None:
        cls.validate_location_indices(data)
        cls.validate_vehicle_capacity_constraints(data)
        cls.validate_unique_ids(data)
    
    @classmethod
    def validate_solution(cls, routes: Dict[str, Route], problem: VRPProblem) -> None:
        cls.validate_route_assignment(routes, problem)
        cls.validate_route_capacity(routes, problem)
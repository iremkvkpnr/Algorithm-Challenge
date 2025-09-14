"""Business logic validation for VRP API."""

from typing import List, Dict, Set
from ..exceptions import VRPError, ErrorCode
from ..schemas.request_models import VRPInput
from ..schemas.response_models import Route


class BusinessValidator:
    
    @classmethod
    def validate_matrix(cls, data: VRPInput) -> None:
        matrix = data.matrix
        if not matrix:
            raise VRPError(
                ErrorCode.INVALID_MATRIX_DATA,
                "Matrix cannot be empty"
            )
        
        n = len(matrix)
        for i, row in enumerate(matrix):
            if len(row) != n:
                raise VRPError(
                    ErrorCode.INVALID_MATRIX_DATA,
                    f"Matrix must be square. Row {i} has {len(row)} elements, expected {n}"
                )
            
            for j, distance in enumerate(row):
                if distance < 0:
                    raise VRPError(
                        ErrorCode.INVALID_MATRIX_DATA,
                        f"Distance cannot be negative at position [{i}][{j}]: {distance}"
                    )
    
    @staticmethod
    def validate_location_indices(data: VRPInput) -> None:
        matrix_size = len(data.matrix)
        
        for vehicle in data.vehicles:
            if vehicle.start_index >= matrix_size:
                raise VRPError(
                    ErrorCode.INVALID_LOCATION_INDEX,
                    f"Vehicle {vehicle.id} start_index {vehicle.start_index} exceeds matrix size {matrix_size}"
                )
        
        for job in data.jobs:
            if job.location_index >= matrix_size:
                raise VRPError(
                    ErrorCode.INVALID_LOCATION_INDEX,
                    f"Job {job.id} location_index {job.location_index} exceeds matrix size {matrix_size}"
                )
    
    @staticmethod
    def validate_vehicle_capacity_constraints(data: VRPInput) -> None:
        for vehicle in data.vehicles:
            if vehicle.capacity:
                vehicle_capacity = vehicle.capacity[0]
                
                total_demand = sum(
                    job.delivery[0] if job.delivery else 1 
                    for job in data.jobs
                )
                
                if vehicle_capacity < total_demand and len(data.vehicles) == 1:
                    raise VRPError(
                        ErrorCode.CAPACITY_EXCEEDED,
                        f"Vehicle {vehicle.id} capacity {vehicle_capacity} cannot handle total demand {total_demand}"
                    )
    
    
    @staticmethod
    def validate_route_assignment(routes: Dict[str, Route], data: VRPInput) -> None:
        assigned_jobs = []
        for route in routes.values():
            assigned_jobs.extend(route.jobs)
        
        expected_jobs = set(job.id for job in data.jobs)
        actual_jobs = set(assigned_jobs)
        
        missing_jobs = expected_jobs - actual_jobs
        if missing_jobs:
            raise VRPError(
                ErrorCode.INVALID_ROUTE_ASSIGNMENT,
                f"Some jobs are not assigned to any route: {list(missing_jobs)}"
            )
        
        if len(assigned_jobs) != len(actual_jobs):
            duplicates = [jid for jid in assigned_jobs if assigned_jobs.count(jid) > 1]
            raise VRPError(
                ErrorCode.INVALID_ROUTE_ASSIGNMENT,
                f"Some jobs are assigned to multiple routes: {list(set(duplicates))}"
            )
    
    @staticmethod
    def validate_route_capacity(routes: Dict[str, Route], data: VRPInput) -> None:
        for vehicle_id, route in routes.items():
            vehicle = next((v for v in data.vehicles if str(v.id) == vehicle_id), None)
            if not vehicle or not vehicle.capacity:
                continue
            
            vehicle_capacity = vehicle.capacity[0]
            route_demand = sum(
                job.delivery[0] if job.delivery else 0 
                for job in data.jobs 
                if job.id in route.jobs
            )
            
            if route_demand > vehicle_capacity:
                raise VRPError(
                    ErrorCode.CAPACITY_EXCEEDED,
                    f"Vehicle {vehicle.id} route demand {route_demand} exceeds capacity {vehicle_capacity}"
                )
    
    @classmethod
    def validate_business_rules(cls, data: VRPInput) -> None:
        cls.validate_matrix(data)
        cls.validate_location_indices(data)
        cls.validate_vehicle_capacity_constraints(data)
    
    @classmethod
    def validate_solution(cls, routes: Dict[str, Route], data: VRPInput) -> None:
        cls.validate_route_assignment(routes, data)
        cls.validate_route_capacity(routes, data)
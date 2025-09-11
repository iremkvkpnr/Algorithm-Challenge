"""Input DTOs for VRP API requests."""

from typing import List, Optional
from pydantic import BaseModel, validator


class VehicleDTO(BaseModel):
    id: int
    start_index: int
    capacity: Optional[List[int]] = None
    
    @validator('start_index')
    def check_start_index(cls, v):
        if v < 0:
            raise ValueError("start_index cannot be negative")
        return v


class JobDTO(BaseModel):
    id: int
    location_index: int
    delivery: Optional[List[int]] = None
    service: Optional[int] = None
    
    @validator('location_index')
    def check_location_index(cls, v):
        if v < 0:
            raise ValueError("location_index cannot be negative")
        return v

    @validator('service')
    def check_service(cls, v):
        if v is not None and v < 0:
            raise ValueError("service time cannot be negative")
        return v


class VRPInputDTO(BaseModel):
    vehicles: List[VehicleDTO]
    jobs: List[JobDTO]
    matrix: List[List[int]]
    
    @validator('matrix')
    def check_matrix(cls, v):
        n = len(v)
        if any(len(row) != n for row in v):
            raise ValueError("matrix must be square")
        return v

    def get_max_location_index(self) -> int:
        return max(
            max(v.start_index for v in self.vehicles),
            max(j.location_index for j in self.jobs)
        )
"""Input DTOs for VRP API requests."""

from typing import List, Optional
from pydantic import BaseModel


class VehicleDTO(BaseModel):
    id: int
    start_index: int
    capacity: Optional[List[int]] = None


class JobDTO(BaseModel):
    id: int
    location_index: int
    delivery: Optional[List[int]] = None
    service: Optional[int] = None


class VRPInputDTO(BaseModel):
    vehicles: List[VehicleDTO]
    jobs: List[JobDTO]
    matrix: List[List[int]]
    

    def get_max_location_index(self) -> int:
        return max(
            max(v.start_index for v in self.vehicles),
            max(j.location_index for j in self.jobs)
        )
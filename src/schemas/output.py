"""Output DTOs for VRP API responses."""

from typing import List, Optional, Dict
from pydantic import BaseModel


class RouteDTO(BaseModel):
    jobs: List[int]
    delivery_duration: int
    capacity_used: int
    total_service_time: int
    total_distance: int
    start_location: int
    end_location: int = 0


class VRPMetadataDTO(BaseModel):
    solve_time_seconds: float
    algorithm: str = "OR-Tools"
    objective_value: Optional[int] = None


class VRPOutputDTO(BaseModel):
    total_delivery_duration: int
    routes: Dict[str, RouteDTO]
    metadata: Optional[VRPMetadataDTO] = None
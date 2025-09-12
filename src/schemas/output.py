"""Output DTOs for VRP API responses."""

from typing import List, Optional, Dict
from pydantic import BaseModel


class RouteDTO(BaseModel):
    jobs: List[int] = []
    delivery_duration: int = 0
    capacity_used: int = 0


class VRPMetadataDTO(BaseModel):
    solve_time_seconds: float
    algorithm: str = "OR-Tools"
    objective_value: Optional[int] = None


class VRPOutputDTO(BaseModel):
    total_delivery_duration: int
    routes: Dict[str, RouteDTO]
    metadata: Optional[VRPMetadataDTO] = None
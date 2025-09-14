"""Output models for VRP API responses."""

from typing import List, Optional, Dict
from pydantic import BaseModel


class Route(BaseModel):
    jobs: List[int]
    delivery_duration: int
    capacity_used: int
    total_service_time: int
    total_distance: int
    start_location: int
    end_location: int = 0


class VRPMetadata(BaseModel):
    solve_time_seconds: float
    algorithm: str = "OR-Tools"
    objective_value: Optional[int] = None
    random_seed: int


class VRPOutput(BaseModel):
    total_delivery_duration: int
    routes: Dict[str, Route]
    metadata: Optional[VRPMetadata] = None
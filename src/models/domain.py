"""Domain models for VRP business logic."""

from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class Vehicle:
    id: int
    start_index: int
    capacity: Optional[List[int]] = None


@dataclass
class Job:
    id: int
    location_index: int
    delivery: Optional[List[int]] = None
    service: Optional[int] = None


@dataclass
class VRPProblem:
    vehicles: List[Vehicle]
    jobs: List[Job]
    matrix: List[List[int]]
    
    def get_max_location_index(self) -> int:
        return max(
            max(v.start_index for v in self.vehicles),
            max(j.location_index for j in self.jobs)
        )


@dataclass
class Route:
    jobs: List[int]
    delivery_duration: int
    capacity_used: int = 0


@dataclass
class VRPSolution:
    total_delivery_duration: int
    routes: Dict[str, Route]
    solve_time_seconds: Optional[float] = None
    objective_value: Optional[int] = None
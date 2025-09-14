"""Input models for VRP API requests."""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Vehicle(BaseModel):
    id: int
    start_index: int = Field(..., ge=0, description="Vehicle start location index (must be non-negative)")
    capacity: Optional[List[int]] = Field(None, description="Vehicle capacity constraints")


class Job(BaseModel):
    id: int
    location_index: int = Field(..., ge=0, description="Job location index (must be non-negative)")
    delivery: Optional[List[int]] = Field(None, description="Delivery requirements")
    service: Optional[int] = Field(None, ge=0, description="Service time (must be non-negative if provided)")


class VRPInput(BaseModel):
    vehicles: List[Vehicle] = Field(..., min_items=1, description="List of vehicles (at least one required)")
    jobs: List[Job] = Field(..., description="List of jobs to be delivered")
    matrix: List[List[int]] = Field(..., description="Distance matrix between locations")
    random_seed: Optional[int] = Field(None, description="Random seed for reproducible results")
        
    @validator('vehicles')
    def validate_unique_vehicle_ids(cls, v):
        if v:
            vehicle_ids = [vehicle.id for vehicle in v]
            if len(vehicle_ids) != len(set(vehicle_ids)):
                duplicates = [vid for vid in vehicle_ids if vehicle_ids.count(vid) > 1]
                raise ValueError(f'Vehicle IDs must be unique. Duplicates: {list(set(duplicates))}')
        return v
    
    @validator('jobs')
    def validate_unique_job_ids(cls, v):
        if v:
            job_ids = [job.id for job in v]
            if len(job_ids) != len(set(job_ids)):
                duplicates = [jid for jid in job_ids if job_ids.count(jid) > 1]
                raise ValueError(f'Job IDs must be unique. Duplicates: {list(set(duplicates))}')
        return v
    

    def get_max_location_index(self) -> int:
        return max(
            max(v.start_index for v in self.vehicles),
            max(j.location_index for j in self.jobs)
        )
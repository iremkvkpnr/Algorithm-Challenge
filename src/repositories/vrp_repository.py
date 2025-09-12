"""VRP Repository for database operations."""
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection

from ..models.domain import Vehicle, Job
from ..schemas.input import VRPInputDTO
from ..schemas.output import VRPOutputDTO
from ..config.database import DatabaseConfig
from ..utils.logger import get_service_logger

logger = get_service_logger()


class VRPRepository:
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None):
        self.db_config = db_config or DatabaseConfig()
        self.client = self.db_config.get_mongo_client()
        self.db = self.db_config.get_database(self.client)
        
        self.solutions_col: Collection = self.db['solutions']
        self.vehicles_col: Collection = self.db['vehicles']
        self.jobs_col: Collection = self.db['jobs']
    
    def save_vehicles(self, vehicles: List[Vehicle]) -> List[str]:
        vehicle_docs = []
        for vehicle in vehicles:
            doc = {
                "vehicle_id": vehicle.id,
                "start_index": vehicle.start_index,
                "capacity": vehicle.capacity
            }
            vehicle_docs.append(doc)
        
        if vehicle_docs:
            result = self.vehicles_col.insert_many(vehicle_docs)
            return [str(id) for id in result.inserted_ids]
        return []
    
    def save_jobs(self, jobs: List[Job]) -> List[str]:
        job_docs = []
        for job in jobs:
            doc = {
                "job_id": job.id,
                "location_index": job.location_index,
                "delivery": job.delivery,
                "service": job.service
            }
            job_docs.append(doc)
        
        if job_docs:
            result = self.jobs_col.insert_many(job_docs)
            return [str(id) for id in result.inserted_ids]
        return []
    
    def save_solution(self, output_dto: VRPOutputDTO, input_data: VRPInputDTO, 
                     vehicle_ids: List[str], job_ids: List[str]) -> str:
        solution_dict = output_dto.dict()
        
        solution_dict['timestamp'] = datetime.utcnow()
        solution_dict['vehicle_refs'] = vehicle_ids
        solution_dict['job_refs'] = job_ids
        
        result = self.solutions_col.insert_one(solution_dict)
        return str(result.inserted_id)
    
    def get_solution_by_id(self, solution_id: str) -> Optional[dict]:
        from bson import ObjectId
        try:
            return self.solutions_col.find_one({"_id": ObjectId(solution_id)})
        except Exception as e:
            logger.error(f"Error retrieving solution {solution_id}: {str(e)}")
            return None
    
    def get_recent_solutions(self, limit: int = 10) -> List[dict]:
        try:
            return list(self.solutions_col.find().sort("timestamp", -1).limit(limit))
        except Exception as e:
            logger.error(f"Error retrieving recent solutions: {str(e)}")
            return []
    
    def close_connection(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
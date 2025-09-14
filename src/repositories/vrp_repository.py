"""VRP Repository for database operations."""
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection

from ..schemas.request_models import VRPInput, Vehicle, Job
from ..schemas.response_models import VRPOutput
from ..config.database import DatabaseConfig
from ..utils.logger import get_service_logger
from ..exceptions import VRPSystemError, ErrorCode

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
        try:
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
        except Exception as e:
            logger.error(f"Failed to save vehicles: {str(e)}", exc_info=True)
            raise VRPSystemError(
                ErrorCode.DATABASE_ERROR,
                f"Failed to save vehicles to database: {str(e)}"
            )
    
    def save_jobs(self, jobs: List[Job]) -> List[str]:
        try:
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
        except Exception as e:
            logger.error(f"Failed to save jobs: {str(e)}", exc_info=True)
            raise VRPSystemError(
                ErrorCode.DATABASE_ERROR,
                f"Failed to save jobs to database: {str(e)}"
            )
    
    def save_solution(self, output_dto: VRPOutput, input_data: VRPInput, 
                     vehicle_ids: List[str], job_ids: List[str]) -> str:
        try:
            solution_dict = output_dto.dict()
            
            solution_dict['timestamp'] = datetime.utcnow()
            solution_dict['vehicle_refs'] = vehicle_ids
            solution_dict['job_refs'] = job_ids
            
            result = self.solutions_col.insert_one(solution_dict)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save solution: {str(e)}", exc_info=True)
            raise VRPSystemError(
                ErrorCode.DATABASE_ERROR,
                f"Failed to save solution to database: {str(e)}"
            )
    
    def get_solution_by_id(self, solution_id: str) -> Optional[dict]:
        from bson import ObjectId
        try:
            return self.solutions_col.find_one({"_id": ObjectId(solution_id)})
        except Exception as e:
            logger.error(f"Failed to retrieve solution {solution_id}: {str(e)}", exc_info=True)
            raise VRPDatabaseError(
                ErrorCode.DATABASE_OPERATION_ERROR,
                f"Failed to retrieve solution {solution_id}: {str(e)}"
            )
    
    def get_recent_solutions(self, limit: int = 10) -> List[dict]:
        try:
            return list(self.solutions_col.find().sort("timestamp", -1).limit(limit))
        except Exception as e:
            logger.error(f"Failed to retrieve recent solutions: {str(e)}", exc_info=True)
            raise VRPSystemError(
                ErrorCode.DATABASE_ERROR,
                f"Failed to retrieve recent solutions: {str(e)}"
            )
    
    def close_connection(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
"""Database configuration module."""
import os
from typing import Optional
from pymongo import MongoClient
from ..utils.logger import get_service_logger
from ..exceptions import VRPSolverError

logger = get_service_logger()


class DatabaseConfig:
    
    def __init__(self, mongo_uri: Optional[str] = None):
        self.mongo_uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('MONGO_DB_NAME', 'vrp_db')
        self.connection_timeout = int(os.getenv('MONGO_TIMEOUT', '10000'))
        self._client = None
    
    def get_mongo_client(self) -> MongoClient:
        try:
            client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=self.connection_timeout)

            client.admin.command('ping')
            logger.info("MongoDB connection established")
            return client
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise VRPSolverError(f"Database connection required but failed: {str(e)}")
    
    def get_database(self, client: MongoClient):
        return client[self.database_name]
    
    def test_connection(self):
        try:
            if not self._client:
                self._client = self.get_mongo_client()
            else:
                self._client.admin.command('ping')
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise
    
    def close_connection(self):
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Database connection closed")


db_config = DatabaseConfig()
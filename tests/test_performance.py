import pytest
import time
from src.services.vrp_service import VRPService
from src.schemas.request_models import VRPInput, Vehicle, Job


class TestVRPPerformance:
    
    def setup_method(self):
        self.vrp_service = VRPService(time_limit=10)
    
    def test_large_dataset_performance(self):
        vehicles = [
            Vehicle(id=i, start_index=0, capacity=[20]) 
            for i in range(1, 6)
        ]
        
        jobs = [
            Job(id=i, location_index=i, delivery=[2], service=100)
            for i in range(1, 21)
        ]
        
        matrix_size = 21
        matrix = [
            [abs(i - j) * 100 for j in range(matrix_size)]
            for i in range(matrix_size)
        ]
        
        data = VRPInput(
            vehicles=vehicles,
            jobs=jobs,
            matrix=matrix
        )
        
        start_time = time.time()
        result = self.vrp_service.solve(data)
        solve_time = time.time() - start_time
        
        assert result.total_delivery_duration > 0
        assert len(result.routes) <= 5
        assert solve_time < 10.0
        assert result.metadata.solve_time_seconds < 10.0
        
        total_jobs_assigned = sum(len(route.jobs) for route in result.routes.values())
        assert total_jobs_assigned == 20
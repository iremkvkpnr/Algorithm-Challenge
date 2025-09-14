import pytest
from src.services.vrp_service import VRPService
from src.schemas.request_models import VRPInput, Vehicle, Job
from src.exceptions import VRPError


class TestVRPService:
    
    def setup_method(self):
        self.vrp_service = VRPService()
    
    def test_simple_vrp_solution(self):
        data = VRPInput(
            vehicles=[
                Vehicle(id=1, start_index=0, capacity=[10])
            ],
            jobs=[
                Job(id=1, location_index=1, delivery=[2]),
                Job(id=2, location_index=2, delivery=[3])
            ],
            matrix=[
                [0, 100, 200],
                [100, 0, 150], 
                [200, 150, 0]
            ]
        )
        
        result = self.vrp_service.solve(data)
        
        assert result.total_delivery_duration > 0
        assert len(result.routes) == 1
        assert "1" in result.routes
        assert len(result.routes["1"].jobs) == 2
        assert result.routes["1"].capacity_used == 5
    
    def test_invalid_matrix_raises_error(self):
        data = VRPInput(
            vehicles=[Vehicle(id=1, start_index=0, capacity=[10])],
            jobs=[Job(id=1, location_index=1, delivery=[2])],
            matrix=[
                [0, 100],
                [100, 0, 150]
            ]
        )
        
        with pytest.raises(VRPError):
            self.vrp_service.solve(data)
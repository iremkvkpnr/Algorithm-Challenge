import pytest
from fastapi.testclient import TestClient
from src.app import create_app
from src.services.vrp_service import VRPService


class TestVRPAPI:
    
    def setup_method(self):
        self.app = create_app()
        self.app.state.vrp_service = VRPService(repository=None)
        self.client = TestClient(self.app)
    
    def test_health_endpoint(self):
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_solve_vrp_endpoint(self):
        payload = {
            "vehicles": [
                {"id": 1, "start_index": 0, "capacity": [10]}
            ],
            "jobs": [
                {"id": 1, "location_index": 1, "delivery": [2]},
                {"id": 2, "location_index": 2, "delivery": [3]}
            ],
            "matrix": [
                [0, 100, 200],
                [100, 0, 150],
                [200, 150, 0]
            ]
        }
        
        response = self.client.post("/solve", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_delivery_duration" in data
        assert "routes" in data
        assert "1" in data["routes"]
        assert len(data["routes"]["1"]["jobs"]) == 2
    
    def test_invalid_request_returns_422(self):
        payload = {
            "vehicles": [],
            "jobs": [],
            "matrix": []
        }
        
        response = self.client.post("/solve", json=payload)
        
        assert response.status_code == 422
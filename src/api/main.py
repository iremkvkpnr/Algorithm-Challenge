from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging
from typing import Dict

from ..schemas.input import VRPInputDTO
from ..schemas.output import VRPOutputDTO
from ..services.vrp_service import VRPService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VRP API",
    description="HTTP microservice for Vehicle Routing Problem",
    version="1.0.0"
)

# Simple CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

vrp_service = VRPService()


@app.get("/")
async def root():
    return {"message": "VRP API is running", "version": "1.0.0"}


@app.post("/solve", response_model=VRPOutputDTO)
async def solve_vrp(vrp_input: VRPInputDTO) -> VRPOutputDTO:
    try:
        logger.info(f"Received VRP request: {len(vrp_input.vehicles)} vehicles, {len(vrp_input.jobs)} jobs")
        result = vrp_service.solve(vrp_input)
        logger.info(f"VRP solved. Total duration: {result.total_delivery_duration}")
        return result
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Solver error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

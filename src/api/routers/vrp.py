"""VRP API router."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
import logging

from ...schemas.input import VRPInputDTO
from ...schemas.output import VRPOutputDTO
from ...services.vrp_service import VRPService
from ..deps import get_vrp_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["VRP"])


@router.post("/solve", response_model=VRPOutputDTO)
async def solve_vrp(
    vrp_input: VRPInputDTO,
    vrp_service: VRPService = Depends(get_vrp_service)
) -> VRPOutputDTO:
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
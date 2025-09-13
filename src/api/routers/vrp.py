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
    logger.info(
        f"Received VRP request: {len(vrp_input.vehicles)} vehicles, {len(vrp_input.jobs)} jobs",
        extra={'vehicles': len(vrp_input.vehicles), 'jobs': len(vrp_input.jobs)}
    )
    
    result = vrp_service.solve(vrp_input)
    
    logger.info(
        f"VRP solved successfully. Total duration: {result.total_delivery_duration}",
        extra={
            'total_duration': result.total_delivery_duration,
            'solve_time': result.metadata.solve_time_seconds if result.metadata else None,
            'routes_count': len(result.routes)
        }
    )
    
    return result
"""VRP API router."""

from fastapi import APIRouter, Request

from ...schemas.request_models import VRPInput
from ...schemas.response_models import VRPOutput
from ...services.vrp_service import VRPService
from ...utils.logger import get_service_logger

logger = get_service_logger()

router = APIRouter(tags=["VRP"])


@router.post("/solve", response_model=VRPOutput)
async def solve_vrp(
    vrp_input: VRPInput,
    request: Request
) -> VRPOutput:
    logger.info(
        f"Received VRP request: {len(vrp_input.vehicles)} vehicles, {len(vrp_input.jobs)} jobs",
        extra={'vehicles': len(vrp_input.vehicles), 'jobs': len(vrp_input.jobs)}
    )
    
    vrp_service: VRPService = request.app.state.vrp_service
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
"""FastAPI dependency providers."""

from fastapi import Request
from ..services.vrp_service import VRPService


def get_vrp_service(request: Request) -> VRPService:
    return request.app.state.vrp_service
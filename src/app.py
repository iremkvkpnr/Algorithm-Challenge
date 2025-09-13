from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import ValidationError
import logging

from .services.vrp_service import VRPService
from .repositories.vrp_repository import VRPRepository
from .config.database import db_config
from .exceptions import VRPException
from .exceptions.handlers import (
    vrp_exception_handler,
    general_exception_handler,
    validation_exception_handler
)

logger = logging.getLogger("vrp.api")

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting VRP API")
    db_config.test_connection()
    repository = VRPRepository()
    app.state.vrp_service = VRPService(repository=repository)
    logger.info("VRP service ready")
    
    yield
    
    logger.info("Shutting down VRP API")
    if hasattr(app.state, 'vrp_service') and app.state.vrp_service.repository:
        app.state.vrp_service.repository.close_connection()
    db_config.close_connection()


def create_app() -> FastAPI:
    app = FastAPI(
        title="VRP API",
        description="HTTP microservice for Vehicle Routing Problem",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    logging.basicConfig(level=logging.INFO)

    app.add_exception_handler(VRPException, vrp_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    from .api.routers.vrp import router as vrp_router
    app.include_router(vrp_router, prefix="")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "message": "VRP API running", "version": "1.0.0"}

    return app

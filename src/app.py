from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .services.vrp_service import VRPService
from .exceptions import (
    VRPException,
    vrp_exception_handler,
    general_exception_handler,
    validation_exception_handler
)

logger = logging.getLogger("vrp.api")

def create_app() -> FastAPI:
    app = FastAPI(
        title="VRP API",
        description="HTTP microservice for Vehicle Routing Problem",
        version="1.0.0"
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
    app.add_exception_handler(Exception, validation_exception_handler)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting VRP API")
        app.state.vrp_service = VRPService()
        logger.info("VRP service ready")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down VRP API")

    from .api.routers.vrp import router as vrp_router
    app.include_router(vrp_router)

    @app.get("/")
    async def root():
        return {"message": "VRP API running", "version": "1.0.0"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

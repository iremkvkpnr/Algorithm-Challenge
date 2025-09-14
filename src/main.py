""" VRP Challenge HTTP Microservice """

import argparse
import uvicorn

from .utils.logger import get_service_logger

logger = get_service_logger()

def main():
    parser = argparse.ArgumentParser(description='VRP Challenge HTTP Microservice')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    logger.info(f"Starting VRP microservice on {args.host}:{args.port}")
    
    try:
        uvicorn.run(
            "src.app:create_app",
            factory=True,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()

"""Launcher for VRP Challenge HTTP Microservice."""

import uvicorn
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Start the VRP Challenge API server")

    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('--log-level', choices=['critical', 'error', 'warning', 'info', 'debug'], default='info', help='Logging level')

    args = parser.parse_args()

    try:
        print(f"Starting VRP API server at http://{args.host}:{args.port}")
        print("API docs available at /docs or /redoc")
        print("Press Ctrl+C to stop")

        uvicorn.run(
            "src.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level
        )

    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        return 0
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

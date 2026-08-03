#!/usr/bin/env python3
"""
MomentoFresh API Server Entry Point

This is the main entry point for the MomentoFresh backend API server.
It initializes the FastAPI application and starts the Uvicorn server.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from momento.config import settings
from momento.api.app import app
from momento.db import init_database, get_engine
from momento.store import seed_initial_data
from momento.feed import LiveFeedEngine
from momento.watcher import start_file_watcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("momento_api.log"),
    ],
)
logger = logging.getLogger(__name__)


def create_database():
    """Initialize the database and create tables."""
    logger.info("Initializing database...")
    init_database()
    logger.info("Database initialized successfully")


def seed_data():
    """Seed initial data if the database is empty."""
    logger.info("Seeding initial data...")
    seed_initial_data()
    logger.info("Initial data seeded")


def start_feed_engine():
    """Start the live feed engine if configured."""
    if settings.feed_autostart:
        logger.info("Starting live feed engine...")
        feed_engine = LiveFeedEngine()
        feed_engine.start()
        logger.info("Live feed engine started")
        return feed_engine
    return None


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(description="MomentoFresh API Server")
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Create database and exit",
    )
    parser.add_argument(
        "--receiver-only",
        action="store_true",
        help="Run only the file watcher without API server",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--host",
        default=settings.api_host,
        help="Host to bind to (default: from config)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help="Port to listen on (default: from config)",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set logging level",
    )

    args = parser.parse_args()

    # Configure logging level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)

    # Initialize database
    create_database()

    # Only init - create DB and exit
    if args.init_only:
        logger.info("Database created successfully. Exiting.")
        sys.exit(0)

    # Seed initial data
    seed_data()

    # Receiver only mode - just run the file watcher
    if args.receiver_only:
        logger.info("Running in receiver-only mode")
        start_file_watcher()
        # Keep the process running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down receiver...")
        sys.exit(0)

    # Start feed engine if configured
    feed_engine = start_feed_engine()

    # Start file watcher
    start_file_watcher()

    # Start the API server
    logger.info(f"Starting MomentoFresh API server on {args.host}:{args.port}")
    logger.info(f"API Docs: http://{args.host}:{args.port}/docs")
    logger.info(f"Health: http://{args.host}:{args.port}/api/v1/health")

    try:
        import uvicorn

        uvicorn.run(
            "momento.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            log_config=None,  # Use our configured logging
        )
    except KeyboardInterrupt:
        logger.info("Shutting down API server...")
        if feed_engine:
            feed_engine.stop()
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
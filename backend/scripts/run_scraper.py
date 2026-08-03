#!/usr/bin/env python3
"""
Standalone Aviator Scraper Entry Point

Run this script to start the scraper as a standalone service.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from momento.scraper.scraper import get_scraper, start_scraper
from momento.scraper.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Aviator Scraper")
    parser.add_argument(
        "--url",
        default=None,
        help="Specific URL to scrape (overrides config)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Scrape interval in seconds (overrides config)",
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="Don't store in database",
    )
    parser.add_argument(
        "--no-broadcast",
        action="store_true",
        help="Don't broadcast via WebSocket",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a single test scrape and exit",
    )

    args = parser.parse_args()

    # Override settings from arguments
    if args.url:
        settings.aviator_urls = [args.url]
    if args.interval:
        settings.interval_seconds = args.interval
    if args.no_store:
        settings.store_in_database = False
    if args.broadcast_enabled is not None:
        settings.broadcast_enabled = not args.no_broadcast

    logger.info(f"Starting Aviator scraper")
    logger.info(f"URLs: {settings.aviator_urls}")
    logger.info(f"Interval: {settings.interval_seconds}s")
    logger.info(f"Store in DB: {settings.store_in_database}")
    logger.info(f"Broadcast: {settings.broadcast_enabled}")

    if args.test:
        # Run a single test
        scraper = get_scraper()
        for url in settings.aviator_urls:
            logger.info(f"Testing scrape from {url}")
            try:
                await scraper.scrape(url)
            except Exception as e:
                logger.error(f"Test scrape failed: {e}")
        logger.info("Test complete")
    else:
        # Run continuously
        try:
            await start_scraper()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            scraper = get_scraper()
            await scraper.stop()


if __name__ == "__main__":
    asyncio.run(main())
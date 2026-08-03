"""
Aviator Scraper - Main implementation

Scrapes crash game data from Aviator sites using multiple methods:
1. WebSocket connections (if available)
2. HTTP API endpoints (if available)
3. HTML parsing (fallback)
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
from bs4 import BeautifulSoup

from .config import settings
from ..db import Round, get_session, session_scope
from ..store import ingest_round
from ..hub import manager as ws_manager

logger = logging.getLogger(__name__)


class AviatorScraper:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.last_scrape: Dict[str, datetime] = {}
        self.consecutive_failures: Dict[str, int] = {}
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]

    async def start(self):
        self.running = True
        logger.info("Starting Aviator scraper")
        
        while self.running:
            for url in settings.aviator_urls:
                try:
                    await self.scrape(url)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                
                # Rate limiting
                await asyncio.sleep(settings.interval_seconds)
            
            # Wait before next cycle
            await asyncio.sleep(settings.interval_seconds)

    async def stop(self):
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Aviator scraper stopped")

    async def scrape(self, url: str):
        current_time = datetime.utcnow()
        
        # Rate limiting check
        if url in self.last_scrape:
            time_since_last = (current_time - self.last_scrape[url]).total_seconds()
            min_interval = 60.0 / settings.requests_per_minute
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {url}")
                await asyncio.sleep(wait_time)
        
        # Try different methods
        try:
            # Method 1: Try WebSocket first
            if await self.try_websocket(url):
                self.last_scrape[url] = datetime.utcnow()
                self.consecutive_failures[url] = 0
                return
        except Exception as e:
            logger.debug(f"WebSocket failed for {url}: {e}")
        
        try:
            # Method 2: Try API endpoint
            if settings.api_endpoints:
                for endpoint in settings.api_endpoints:
                    if await self.try_api(endpoint):
                        self.last_scrape[url] = datetime.utcnow()
                        self.consecutive_failures[url] = 0
                        return
        except Exception as e:
            logger.debug(f"API failed for {url}: {e}")
        
        try:
            # Method 3: HTML parsing
            if await self.try_html_parse(url):
                self.last_scrape[url] = datetime.utcnow()
                self.consecutive_failures[url] = 0
                return
        except Exception as e:
            logger.debug(f"HTML parse failed for {url}: {e}")
        
        # All methods failed
        self.consecutive_failures[url] = self.consecutive_failures.get(url, 0) + 1
        if self.consecutive_failures[url] >= settings.max_retries:
            logger.warning(f"Max retries reached for {url}, disabling")
        
        self.last_scrape[url] = datetime.utcnow()

    async def try_websocket(self, url: str) -> bool:
        try:
            # Extract domain for WebSocket URL
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
            ws_url = f"wss://{domain}/socket.io/?EIO=4&transport=websocket"
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url) as ws:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if self.is_round_data(data):
                                await self.process_round(data, url)
                                return True
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
        except Exception as e:
            logger.debug(f"WebSocket error: {e}")
        return False

    async def try_api(self, endpoint: str) -> bool:
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "application/json",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=settings.timeout_seconds)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            for item in data:
                                if self.is_round_data(item):
                                    await self.process_round(item, endpoint)
                            return True
                        elif self.is_round_data(data):
                            await self.process_round(data, endpoint)
                            return True
        except Exception as e:
            logger.debug(f"API error: {e}")
        return False

    async def try_html_parse(self, url: str) -> bool:
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=settings.timeout_seconds)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Try to find multiplier data in various locations
                        multipliers = self.parse_multipliers_from_html(soup)
                        
                        if multipliers:
                            for multiplier in multipliers:
                                round_data = {
                                    "multiplier": multiplier,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "source": "aviator",
                                    "ingest_method": "scraper",
                                }
                                await self.process_round(round_data, url)
                            return True
        except Exception as e:
            logger.debug(f"HTML parse error: {e}")
        return False

    def is_round_data(self, data: Any) -> bool:
        if not isinstance(data, dict):
            return False
        
        # Check for multiplier field
        multiplier_keys = ['multiplier', 'multi', 'x', 'crashPoint', 'crash_point']
        for key in multiplier_keys:
            if key in data and isinstance(data[key], (int, float)):
                return True
        
        return False

    def parse_multipliers_from_html(self, soup: BeautifulSoup) -> List[float]:
        multipliers = []
        
        # Try to find in script tags (JSON data)
        for script in soup.find_all('script'):
            if script.string:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, (int, float)) and value >= 1.0:
                                multipliers.append(float(value))
                                break
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Try to find in specific classes
        for element in soup.find_all(class_=lambda x: x and 'multiplier' in x.lower()):
            text = element.get_text().strip()
            try:
                multiplier = float(text.replace('x', '').replace(',', ''))
                if multiplier >= 1.0:
                    multipliers.append(multiplier)
            except ValueError:
                pass
        
        # Try to find in data attributes
        for element in soup.find_all(attrs={"data-multiplier": True}):
            try:
                multiplier = float(element['data-multiplier'])
                if multiplier >= 1.0:
                    multipliers.append(multiplier)
            except (ValueError, KeyError):
                pass
        
        return multipliers

    async def process_round(self, round_data: Dict[str, Any], source_url: str):
        try:
            # Normalize the data
            multiplier = round_data.get('multiplier') or round_data.get('multi') or round_data.get('x')
            if multiplier is None:
                multiplier = round_data.get('crashPoint') or round_data.get('crash_point')
            
            if multiplier is None:
                logger.debug(f"No multiplier found in data: {round_data}")
                return
            
            multiplier = float(multiplier)
            timestamp = round_data.get('timestamp') or datetime.utcnow().isoformat()
            
            # Create round data
            data = {
                "source": "aviator",
                "timestamp": timestamp,
                "multiplier": multiplier,
                "ingest_method": "scraper",
                "source_file": source_url,
            }
            
            # Ingest the round
            if settings.store_in_database:
                round_obj = ingest_round(data, "aviator")
                logger.debug(f"Scraped round: {multiplier}x from {source_url}")
            
            # Broadcast via WebSocket
            if settings.broadcast_enabled:
                ws_manager.broadcast_threadsafe(
                    "round:new",
                    data,
                    source="aviator"
                )
            
            return True
        except Exception as e:
            logger.error(f"Error processing round: {e}")
            return False

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session


# Global scraper instance
scraper: Optional[AviatorScraper] = None


def get_scraper() -> AviatorScraper:
    global scraper
    if scraper is None:
        scraper = AviatorScraper()
    return scraper


async def start_scraper():
    scraper = get_scraper()
    await scraper.start()


async def stop_scraper():
    scraper = get_scraper()
    await scraper.stop()
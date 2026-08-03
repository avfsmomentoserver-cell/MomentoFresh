"""
Live Feed Engine for MomentoFresh

Generates provably-fair crash game rounds in real-time.
"""

import asyncio
import hashlib
import logging
import random
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .config import settings
from .db import Round, get_session, session_scope
from .hub import hub

logger = logging.getLogger(__name__)


class LiveFeedEngine:
    """
    Engine for generating live crash game rounds.
    
    Uses provably-fair algorithms to generate multipliers.
    """

    def __init__(self):
        self._running = False
        self._server_seed = self._generate_seed()
        self._client_seed = ""
        self._nonce = 0
        self._round_number = 0
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []

    def _generate_seed(self) -> str:
        """Generate a random server seed."""
        return hashlib.sha256(os.urandom(32)).hexdigest()

    def set_client_seed(self, seed: str):
        """Set the client seed for provably-fair generation."""
        self._client_seed = seed
        logger.info(f"Client seed set: {seed[:16]}...")

    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback for new rounds."""
        self._callbacks.append(callback)

    def _generate_round(self) -> Dict[str, Any]:
        """
        Generate a new provably-fair round.
        
        Uses HMAC-based algorithm for provably-fair results.
        """
        self._nonce += 1
        self._round_number += 1
        
        # Combine seeds and nonce
        combined = f"{self._server_seed}:{self._client_seed}:{self._nonce}"
        
        # Generate hash
        hash_obj = hashlib.sha256(combined.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to float between 0 and 1
        hash_int = int(hash_hex[:13], 16)
        hash_float = hash_int / (10 ** 13)
        
        # Generate multiplier (1.0x to 100.0x range)
        # Using curve: P(crash) = 1 / x, so x = 1 / (1 - hash_float)
        # But cap at 100x
        if hash_float == 0:
            hash_float = 0.0000000000001
        
        crash_point = hash_float
        multiplier = 1.0 / (1.0 - crash_point) if crash_point < 0.99 else 100.0
        multiplier = min(multiplier, 100.0)
        multiplier = max(multiplier, 1.0)
        
        # Determine color based on multiplier
        if multiplier < 1.5:
            color = "red"
        elif multiplier < 2.0:
            color = "orange"
        elif multiplier < 5.0:
            color = "yellow"
        elif multiplier < 10.0:
            color = "green"
        else:
            color = "blue"
        
        round_data = {
            "id": self._round_number,
            "source": "live_feed",
            "timestamp": datetime.utcnow(),
            "multiplier": round(multiplier, 2),
            "color": color,
            "crash_point": crash_point,
            "hash": hash_hex,
            "server_seed": self._server_seed,
            "client_seed": self._client_seed,
            "nonce": self._nonce,
        }
        
        return round_data

    def _notify_callbacks(self, round_data: Dict[str, Any]):
        """Notify all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(round_data)
            except Exception as e:
                logger.error(f"Error in callback: {e}")

    def start(self):
        """Start the feed engine."""
        if self._running:
            logger.warning("Feed engine already running")
            return
        
        self._running = True
        logger.info("Live feed engine started")
        
        # Generate initial round
        self._generate_and_broadcast()

    def stop(self):
        """Stop the feed engine."""
        self._running = False
        logger.info("Live feed engine stopped")

    def _generate_and_broadcast(self):
        """Generate a round and broadcast it."""
        if not self._running:
            return
        
        round_data = self._generate_round()
        
        # Save to database
        try:
            with session_scope() as session:
                round_obj = Round(
                    source=round_data["source"],
                    timestamp=round_data["timestamp"],
                    multiplier=round_data["multiplier"],
                    color=round_data["color"],
                    ingest_method="feed",
                )
                session.add(round_obj)
        except Exception as e:
            logger.error(f"Error saving round to database: {e}")
        
        # Broadcast via WebSocket
        hub.broadcast_threadsafe("round:new", round_data, source=round_data["source"])
        
        # Notify callbacks
        self._notify_callbacks(round_data)
        
        # Schedule next round
        if self._running:
            asyncio.run_coroutine_threadsafe(
                self._schedule_next(),
                hub.get_event_loop()
            )

    async def _schedule_next(self):
        """Schedule the next round generation."""
        await asyncio.sleep(settings.feed_interval_seconds)
        self._generate_and_broadcast()

    def generate_round(self) -> Dict[str, Any]:
        """Generate a single round (for testing)."""
        return self._generate_round()


# Global feed engine instance
feed_engine: Optional[LiveFeedEngine] = None


def get_feed_engine() -> LiveFeedEngine:
    """Get or create the feed engine."""
    global feed_engine
    if feed_engine is None:
        feed_engine = LiveFeedEngine()
    return feed_engine
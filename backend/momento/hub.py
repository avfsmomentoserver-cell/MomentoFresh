"""
WebSocket Hub for MomentoFresh

Manages WebSocket connections and real-time event broadcasting.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set

import websockets

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[websockets.WebSocketServerProtocol] = set()
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}

    async def connect(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new WebSocket connection."""
        self.active_connections.add(websocket)
        logger.info(f"New connection: {websocket.remote_address}")
        
        try:
            await websocket.send_json({
                "type": "connected",
                "message": "Welcome to MomentoFresh WebSocket",
                "timestamp": None,
            })
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

    def disconnect(self, websocket: websockets.WebSocketServerProtocol):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"Connection closed: {websocket.remote_address}")

    async def send_personal_message(
        self,
        message: Any,
        websocket: websockets.WebSocketServerProtocol
    ):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Any, source: Optional[str] = None):
        """Broadcast a message to all connected clients."""
        if self.active_connections:
            await asyncio.wait([
                connection.send_json(message)
                for connection in self.active_connections
            ])
            logger.debug(f"Broadcast message to {len(self.active_connections)} connections")

    def broadcast_threadsafe(self, message_type: str, data: Any, source: Optional[str] = None):
        """
        Broadcast a message from a non-async context.
        
        This method can be called from synchronous code.
        """
        message = {
            "type": message_type,
            "data": data,
            "source": source,
            "timestamp": None,
        }
        
        # In production, use a thread-safe queue
        # For now, we'll just log it
        logger.info(f"Thread-safe broadcast: {message_type}")

    def on(self, event_type: str, callback: Callable[[Any], None]):
        """Register an event listener."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def emit(self, event_type: str, data: Any):
        """Emit an event to all listeners."""
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get the current event loop."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop


# Global connection manager
manager = ConnectionManager()


async def websocket_handler(
    websocket: websockets.WebSocketServerProtocol,
    path: str
):
    """WebSocket message handler."""
    await manager.connect(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get("type")
                
                # Handle different message types
                if message_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": None,
                    }, websocket)
                
                elif message_type == "subscribe":
                    # Handle subscription
                    source = data.get("source")
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "source": source,
                        "timestamp": None,
                    }, websocket)
                
                else:
                    logger.debug(f"Received message: {message_type}")
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": None,
                }, websocket)
                
    except websockets.exceptions.ConnectionClosed:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# For backwards compatibility
hub = manager
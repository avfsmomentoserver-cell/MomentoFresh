"""WebSocket API routes"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..deps import verify_api_key
from ....hub import manager as ws_manager

router = APIRouter(prefix="/ws")


@router.get("/info")
async def ws_info(api_key: str = Depends(verify_api_key)):
    return {
        "active_connections": len(ws_manager.active_connections),
        "status": "running" if ws_manager.active_connections else "idle"
    }


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    api_key: Optional[str] = None
):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process message if needed
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
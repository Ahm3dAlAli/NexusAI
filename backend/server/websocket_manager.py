import asyncio

from fastapi import WebSocket
from nexusai.utils.logger import logger


class WebSocketManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accepts the WebSocket connection and adds it to the active connections."""
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Removes the WebSocket connection from the active connections."""
        try:
            async with self.lock:
                self.active_connections.remove(websocket)
        except ValueError:
            logger.warning(f"Attempted to remove non-existent WebSocket connection")

    async def send_message(self, data: dict, websocket: WebSocket):
        """Sends data to a specific WebSocket connection."""
        await websocket.send_json(data)

    async def receive_message(self, websocket: WebSocket) -> dict:
        """Receives data from a specific WebSocket connection."""
        return await websocket.receive_json()

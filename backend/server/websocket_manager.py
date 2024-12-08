from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts the WebSocket connection and adds it to the active connections."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes the WebSocket connection from the active connections."""
        self.active_connections.remove(websocket)

    async def send_message(self, data: dict, websocket: WebSocket):
        """Sends data to a specific WebSocket connection."""
        await websocket.send_json(data)

    async def receive_message(self, websocket: WebSocket) -> dict:
        """Receives data from a specific WebSocket connection."""
        return await websocket.receive_json()

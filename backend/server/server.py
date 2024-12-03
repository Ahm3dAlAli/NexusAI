from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .websocket_manager import WebSocketManager
from nexusai.agent import process_query

# Models
class QueryRequest(BaseModel):
    query: str

# FastAPI app
app = FastAPI()

# WebSocket manager
manager = WebSocketManager()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints
@app.get("/")
async def read_root():
    return "Hello, World!"

@app.websocket("/ws")
async def process_query(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive and validate message
            data = await websocket.receive_json()
            try:
                request = QueryRequest(**data)
            except ValueError:
                await manager.send_message(
                    {"error": "Invalid request format. Expected {'query': 'your question'}"}, 
                    websocket
                )
                continue

            # Process the query using the agent's workflow
            result = await process_query(request.query)
            await manager.send_message(
                result, 
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

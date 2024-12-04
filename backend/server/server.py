from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .websocket_manager import WebSocketManager
from .models import QueryRequest
from nexusai.agent import process_query
from nexusai.models.outputs import AgentMessage, AgentMessageType

# FastAPI app
app = FastAPI()

# WebSocket manager
manager = WebSocketManager()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints
@app.get("/")
async def read_root():
    return "Hello, World!"

@app.websocket("/ws")
async def process_query_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    # Send intermediate messages
    async def send_intermediate_message(message: AgentMessage):
        await manager.send_message(message.model_dump(), websocket)

    try:
        while True:
            # Receive and validate message
            data = await manager.receive_message(websocket)
            try:
                request = QueryRequest(**data)
            except ValueError:
                await manager.send_message(
                    AgentMessage(
                        type=AgentMessageType.error,
                        content="Invalid request format. Expected {'query': 'your question'}"
                    ).model_dump(),
                    websocket
                )
                continue

            # Process the query using the agent's workflow
            result: AgentMessage = await process_query(
                query=request.query,
                message_callback=send_intermediate_message
            )

            # Send final message
            await manager.send_message(result.model_dump(), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

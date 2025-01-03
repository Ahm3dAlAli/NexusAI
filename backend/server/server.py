from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from server.models import QueryRequest
from server.websocket_manager import WebSocketManager

from nexusai.agent import process_query
from nexusai.config import FRONTEND_URL
from nexusai.models.outputs import AgentMessage, AgentMessageType
from nexusai.utils.logger import logger

# FastAPI app
app = FastAPI()

# WebSocket manager
manager = WebSocketManager()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints
@app.get("/")
async def read_root():
    return "🚀 NexusAI is up and running!"


@app.websocket("/ws")
async def process_query_websocket(websocket: WebSocket):
    """Chat with the agent through a websocket."""

    async def send_intermediate_message(message: AgentMessage):
        """Callback function to send intermediate messages to the client."""
        await manager.send_message(message.model_dump(), websocket)

    await manager.connect(websocket)
    history = []
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
                        content="Invalid request format. Expected {'query': 'your question'}",
                    ).model_dump(),
                    websocket,
                )
                continue

            # Process the query using the agent's workflow
            result: AgentMessage = await process_query(
                query=request.query,
                history=history,
                message_callback=send_intermediate_message,
            )
            history.append(
                AgentMessage(type=AgentMessageType.human, content=request.query)
            )
            history.append(result)

            # Send final message
            await manager.send_message(result.model_dump(), websocket)
    except Exception as e:
        logger.error(e)
    finally:
        manager.disconnect(websocket)

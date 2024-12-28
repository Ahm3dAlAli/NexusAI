from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from nexusai.agent import process_query
from nexusai.config import FRONTEND_URL
from nexusai.models.outputs import AgentMessage, AgentMessageType
from nexusai.utils.logger import logger
from server.models import MessageRequest
from server.utils import validate_token
from server.websocket_manager import WebSocketManager

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

    # Validate token
    token = websocket.query_params.get("token")
    logger.info("Validating token...")
    if not token or not validate_token(token):
        logger.error("Missing or invalid token")
        await websocket.close(code=4001, reason="Missing or invalid token")
        return

    # Connect and process messages
    await manager.connect(websocket)
    history = []
    try:
        while True:
            # Receive and validate message
            data = await manager.receive_message(websocket)
            try:
                request = MessageRequest(**data)
            except ValueError as e:
                logger.error(e)
                await manager.send_message(
                    AgentMessage(
                        order=0,
                        type=AgentMessageType.error,
                        content=str(e),
                    ).model_dump(),
                    websocket,
                )
                continue

            history = request.history or history
            if request.query:
                # Process the query using the agent's workflow
                result: AgentMessage = await process_query(
                    query=request.query,
                    history=history,
                    message_callback=send_intermediate_message,
                )
                history.append(
                    AgentMessage(
                        order=len(history),
                        type=AgentMessageType.human,
                        content=request.query,
                    )
                )
                history.append(result)

                # Send final message
                await manager.send_message(result.model_dump(), websocket)
    except Exception as e:
        logger.error(f"Error with websocket: {e}")
    finally:
        await manager.disconnect(websocket)

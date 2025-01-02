import asyncio

from fastapi import FastAPI, HTTPException, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from nexusai.agent import process_query
from nexusai.chat import process_paper
from nexusai.config import FRONTEND_URL
from nexusai.models.outputs import AgentMessage, AgentMessageType, PaperOutput
from nexusai.utils.logger import logger
from server.models import MessageRequest, PapersRequest
from server.utils import validate_jwt
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


@app.get("/")
async def http_root():
    return "🚀 NexusAI is up and running!"


@app.post("/papers")
async def http_create_papers(
    request: PapersRequest, token: str = Query(None)
) -> list[PaperOutput]:
    """Create papers from URLs concurrently."""
    logger.info("Validating token...")
    if not token or not validate_jwt(token):
        logger.error("Missing or invalid token")
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    try:
        # Process papers concurrently
        tasks = [process_paper(url) for url in request.urls]
        papers = await asyncio.gather(*tasks)
        return [paper for paper in papers if paper]
    except Exception as e:
        logger.error(f"Error processing papers: {e}")
        raise HTTPException(status_code=500, detail="Error processing papers")


@app.websocket("/ws")
async def ws_process_query(websocket: WebSocket):
    """Chat with the agent through a websocket."""

    async def send_intermediate_message(message: AgentMessage):
        """Callback function to send intermediate messages to the client."""
        await manager.send_message(message.model_dump(), websocket)

    # Validate token
    token = websocket.query_params.get("token")
    logger.info("Validating token...")
    if not token or not validate_jwt(token):
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
                    custom_instructions=request.custom_instructions
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

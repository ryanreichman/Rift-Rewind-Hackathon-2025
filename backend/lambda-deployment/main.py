"""
FastAPI server for AI Chat Agent.
Provides REST API and SSE streaming endpoints.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from agents import BedrockAgent
from config import get_settings
from models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ErrorResponse,
    StreamChunk,
    RetrieveRequest,
    RetrieveResponse,
    KnowledgeBaseResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: BedrockAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global agent
    # Startup
    logger.info("Starting AI Chat Agent server...")
    settings = get_settings()

    try:
        agent = BedrockAgent()
        logger.info("Bedrock agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock agent: {e}")
        logger.warning("Server starting without Bedrock agent - API calls will fail")

    yield

    # Shutdown
    logger.info("Shutting down AI Chat Agent server...")


# Initialize FastAPI app
app = FastAPI(
    title="Summoners Reunion AI Agent",
    description="AI chat agent powered by AWS Bedrock and Strands SDK",
    version="1.0.0",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Summoners Reunion AI Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "chat_stream": "/api/chat/stream (POST)",
            "chat": "/api/chat (POST)",
            "retrieve": "/api/knowledge/retrieve (POST)",
            "knowledge_enabled": settings.knowledge_base_enabled
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    bedrock_healthy = False

    if agent:
        try:
            bedrock_healthy = agent.check_health()
        except Exception as e:
            logger.error(f"Health check failed: {e}")

    return HealthResponse(
        status="healthy" if bedrock_healthy else "degraded",
        app_name=settings.app_name,
        timestamp=datetime.utcnow(),
        bedrock_configured=bedrock_healthy
    )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response using Server-Sent Events (SSE).

    This endpoint streams the AI response in real-time as it's generated.
    Supports optional knowledge base retrieval for RAG.
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Bedrock agent not initialized"
        )

    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events with streaming response."""
        request.use_knowledge_base = True
        try:
            # Choose streaming method based on knowledge base usage
            if request.use_knowledge_base:
                # Use knowledge base enhanced response
                stream_func = agent.stream_response_with_knowledge(
                    user_message=request.message,
                    knowledge_base_id=request.knowledge_base_id,
                    conversation_history=request.conversation_history,
                    system_prompt=request.system_prompt
                )
            else:
                # Regular streaming response
                stream_func = agent.stream_response(
                    user_message=request.message,
                    conversation_history=request.conversation_history,
                    system_prompt=request.system_prompt
                )

            # Stream response from agent
            async for chunk in stream_func:
                # Yield each chunk as an SSE event
                yield {
                    "event": "message",
                    "data": StreamChunk(content=chunk, done=False).model_dump_json()
                }

            # Send final event indicating completion
            yield {
                "event": "message",
                "data": StreamChunk(content="", done=True).model_dump_json()
            }

        except Exception as e:
            logger.error(f"Error in stream: {e}")
            yield {
                "event": "error",
                "data": ErrorResponse(
                    error="Stream error",
                    detail=str(e)
                ).model_dump_json()
            }

    return EventSourceResponse(event_generator())


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Get complete chat response (non-streaming).

    This endpoint returns the full AI response after generation is complete.
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Bedrock agent not initialized"
        )

    try:
        # Get complete response from agent
        response_text = await agent.get_response(
            user_message=request.message,
            conversation_history=request.conversation_history,
            system_prompt=request.system_prompt
        )

        return ChatResponse(
            message=response_text,
            role="assistant",
            timestamp=datetime.utcnow(),
            model_id=settings.bedrock_model_id
        )

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


@app.post("/api/knowledge/retrieve", response_model=RetrieveResponse)
async def retrieve_from_knowledge_base(request: RetrieveRequest):
    """
    Retrieve relevant information from AWS Bedrock Knowledge Base.

    This endpoint performs semantic search over your knowledge base and returns
    relevant documents without generating a response.
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Bedrock agent not initialized"
        )

    try:
        # Retrieve from knowledge base
        results = agent.retrieve_from_knowledge_base(
            query=request.query,
            knowledge_base_id=request.knowledge_base_id,
            max_results=request.max_results
        )

        # Convert to response model
        kb_results = [
            KnowledgeBaseResult(
                content=result['content'],
                score=result['score'],
                location=result['location'],
                metadata=result['metadata']
            )
            for result in results
        ]

        return RetrieveResponse(
            results=kb_results,
            query=request.query,
            count=len(kb_results),
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error retrieving from knowledge base: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve from knowledge base: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc),
        timestamp=datetime.utcnow()
    )


# Lambda handler for AWS deployment (using Mangum)
# This allows the FastAPI app to run on AWS Lambda
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="auto")
except ImportError:
    logger.warning("Mangum not installed - Lambda handler not available")
    handler = None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )

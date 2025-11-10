"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Message(BaseModel):
    """Represents a single chat message."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how can you help me?",
                "timestamp": "2025-01-15T10:30:00"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=10000, description="User's message to the AI")
    conversation_history: Optional[List[Message]] = Field(default=[], description="Previous messages in the conversation")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt to guide AI behavior")
    use_knowledge_base: bool = Field(default=False, description="Enable knowledge base retrieval (RAG)")
    knowledge_base_id: Optional[str] = Field(None, description="Specific knowledge base ID to use")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the best strategies for team fights?",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Hello!",
                        "timestamp": "2025-01-15T10:30:00"
                    },
                    {
                        "role": "assistant",
                        "content": "Hello! How can I assist you today?",
                        "timestamp": "2025-01-15T10:30:01"
                    }
                ]
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint (non-streaming)."""

    message: str
    role: Literal["assistant"] = "assistant"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Here are some effective team fight strategies...",
                "role": "assistant",
                "timestamp": "2025-01-15T10:30:05",
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0"
            }
        }


class StreamChunk(BaseModel):
    """Individual chunk in a streaming response."""

    content: str
    done: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello",
                "done": False
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    app_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    bedrock_configured: bool

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "app_name": "Summoners Reunion AI Agent",
                "timestamp": "2025-01-15T10:30:00",
                "bedrock_configured": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "Message cannot be empty",
                "timestamp": "2025-01-15T10:30:00"
            }
        }


class KnowledgeBaseResult(BaseModel):
    """Knowledge base retrieval result."""

    content: str
    score: float
    location: dict = {}
    metadata: dict = {}


class RetrieveRequest(BaseModel):
    """Request model for knowledge base retrieval endpoint."""

    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    knowledge_base_id: Optional[str] = Field(None, description="Knowledge base ID (uses default if not provided)")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results to retrieve")


class RetrieveResponse(BaseModel):
    """Response model for knowledge base retrieval endpoint."""

    results: List[KnowledgeBaseResult]
    query: str
    count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

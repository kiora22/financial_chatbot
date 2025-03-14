from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("chat_router")

# Create router
router = APIRouter()


class ChatMessage(BaseModel):
    """Model for chat messages."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Model for chat requests."""
    messages: List[ChatMessage]
    user_id: str


class ChatResponse(BaseModel):
    """Model for chat responses."""
    message: ChatMessage
    context: Optional[List[str]] = None  # Sources used for RAG


@router.post("/", response_model=ChatResponse)
async def process_chat(chat_request: ChatRequest):
    """Process a chat request and return a response."""
    try:
        logger.info(f"Received chat request from user_id: {chat_request.user_id}")
        
        # For now, just echo back the last message with a prefix
        # In Phase 2, this will use the LLM with RAG
        last_message = chat_request.messages[-1]
        response_text = f"Echo: {last_message.content}"
        
        logger.info(f"Returning chat response for user_id: {chat_request.user_id}")
        return ChatResponse(
            message=ChatMessage(role="assistant", content=response_text),
            context=[]  # No context yet as RAG is not implemented
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@router.get("/history/{user_id}", response_model=List[ChatMessage])
async def get_chat_history(user_id: str):
    """Get chat history for a user."""
    try:
        logger.info(f"Retrieving chat history for user_id: {user_id}")
        
        # For now, return a mock history
        # In later phases, this will retrieve from the database
        mock_history = [
            ChatMessage(role="user", content="Hello!"),
            ChatMessage(role="assistant", content="Hello! How can I help you with your financial questions today?")
        ]
        
        return mock_history
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from config.logging_config import setup_logging
from backend.core.rag_retrieval import rag_retrieval

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
    use_rag: bool = True  # Whether to use RAG for this request


class ContextSource(BaseModel):
    """Model for context sources used in RAG."""
    content: str
    source: str
    score: float


class ChatResponse(BaseModel):
    """Model for chat responses."""
    message: ChatMessage
    context: Optional[List[ContextSource]] = None  # Sources used for RAG


@router.post("/", response_model=ChatResponse)
async def process_chat(chat_request: ChatRequest):
    """Process a chat request and return a response."""
    try:
        logger.info(f"Received chat request from user_id: {chat_request.user_id}")
        
        # Get the last message from the user
        last_message = chat_request.messages[-1]
        
        # Retrieve context from RAG if enabled
        context = []
        if chat_request.use_rag:
            logger.info(f"Using RAG for query: {last_message.content}")
            retrieved_context = await rag_retrieval.retrieve_context(
                query=last_message.content,
                top_k=3,
                threshold=0.7
            )
            
            context = [
                ContextSource(
                    content=item["content"],
                    source=item["source"],
                    score=item["score"]
                )
                for item in retrieved_context
            ]
            
            logger.info(f"Retrieved {len(context)} context items")
        
        # In Phase 2, this would use an LLM with the retrieved context
        # For now, we'll just echo back the query with the context
        
        context_text = ""
        if context:
            context_text = "\n\nRelevant information:\n" + "\n".join([
                f"- {item.content} (Source: {item.source}, Score: {item.score:.2f})"
                for item in context
            ])
        
        response_text = f"Echo: {last_message.content}{context_text}"
        
        logger.info(f"Returning chat response for user_id: {chat_request.user_id}")
        return ChatResponse(
            message=ChatMessage(role="assistant", content=response_text),
            context=context
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


@router.get("/test-rag", response_model=Dict[str, Any])
async def test_rag():
    """Test endpoint for RAG system functionality."""
    try:
        logger.info("Testing RAG system functionality")
        
        # Test the embedding function and database connection
        test_results = await rag_retrieval.test_embedding()
        
        # Test retrieval with a simple query
        query = "What is the submission process for expenses?"
        retrieved_context = await rag_retrieval.retrieve_context(
            query=query,
            top_k=2,
            threshold=0.5
        )
        
        # Prepare response
        response = {
            "status": test_results["status"],
            "embedding_test": test_results,
            "retrieval_test": {
                "query": query,
                "results_count": len(retrieved_context),
                "results": retrieved_context
            }
        }
        
        logger.info(f"RAG test completed with status: {response['status']}")
        return response
        
    except Exception as e:
        logger.error(f"Error testing RAG functionality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing RAG functionality: {str(e)}")
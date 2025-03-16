from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from config.logging_config import setup_logging
from backend.core.rag_retrieval import rag_retrieval
from backend.core.llm_processor import llm_processor
from config.personas import get_available_personas

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
    persona: str = "default"  # Persona to use for the response


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
        retrieved_context_raw = []
        if chat_request.use_rag:
            logger.info(f"Using RAG for query: {last_message.content}")
            retrieved_context_raw = await rag_retrieval.retrieve_context(
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
                for item in retrieved_context_raw
            ]
            
            logger.info(f"Retrieved {len(context)} context items")
        
        # Convert chat history to format expected by LLM processor
        formatted_history = []
        for i, msg in enumerate(chat_request.messages[:-1]):  # Exclude the last message which we handle separately
            formatted_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Generate response using LLM with context and persona
        logger.info(f"Generating response using LLM processor with persona: {chat_request.persona}")
        response_text = await llm_processor.generate_response(
            user_message=last_message.content,
            chat_history=formatted_history if formatted_history else None,
            retrieved_context=retrieved_context_raw if retrieved_context_raw else None,
            persona=chat_request.persona
        )
        
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


@router.post("/parse-budget-request", response_model=Dict[str, Any])
async def parse_budget_request(request: Dict[str, str]):
    """
    Parse a budget modification request into structured data.
    
    Args:
        request: A dictionary containing the user's budget request
        
    Returns:
        Structured budget modification data
    """
    try:
        logger.info("Received budget parsing request")
        
        if "text" not in request:
            raise HTTPException(status_code=400, detail="Missing 'text' field in request")
        
        # Parse the budget request
        parsed_request = await llm_processor.parse_budget_modification(request["text"])
        
        logger.info(f"Successfully parsed budget request: {parsed_request}")
        return parsed_request
    except Exception as e:
        logger.error(f"Error parsing budget request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing budget request: {str(e)}")


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


@router.get("/test-llm", response_model=Dict[str, str])
async def test_llm():
    """Test endpoint for LLM functionality."""
    try:
        logger.info("Testing LLM functionality")
        
        # Generate a response with a simple test query
        test_query = "What are some ways to optimize a marketing budget?"
        
        # Get test context from RAG
        retrieved_context = await rag_retrieval.retrieve_context(
            query=test_query,
            top_k=2,
            threshold=0.6
        )
        
        # Generate response
        response_text = await llm_processor.generate_response(
            user_message=test_query,
            retrieved_context=retrieved_context
        )
        
        return {
            "status": "success",
            "query": test_query,
            "response": response_text
        }
        
    except Exception as e:
        logger.error(f"Error testing LLM functionality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing LLM functionality: {str(e)}")


@router.get("/personas", response_model=List[str])
async def get_personas():
    """Get available chatbot personas."""
    try:
        logger.info("Retrieving available chatbot personas")
        
        # Get personas from configuration
        personas = get_available_personas()
        
        logger.info(f"Found {len(personas)} available personas")
        return personas
        
    except Exception as e:
        logger.error(f"Error retrieving personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving personas: {str(e)}")
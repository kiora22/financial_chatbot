import openai
from typing import List, Dict, Any, Optional

from config.settings import settings
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("llm_processor")

# Set OpenAI API key
openai.api_key = settings.openai_api_key


class LLMProcessor:
    """Class for handling interactions with the OpenAI API."""
    
    def __init__(self):
        """Initialize the LLM processor."""
        # Default model
        self.model = "gpt-4o-mini"
        
        # Default system prompt for financial assistant
        self.system_prompt = (
            "You are a professional financial advisor assistant specialized in budget analysis and management. "
            "You provide concise, accurate financial insights and help with budget planning and modifications. "
            "When discussing financial figures, be precise and clear. "
            "If asked about budget modifications, recommend reasonable adjustments based on business goals and financial best practices. "
            "Always maintain a professional, helpful tone and focus on providing actionable financial advice."
        )
        
        logger.info("LLM processor initialized")
    
    async def generate_response(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        retrieved_context: Optional[List[str]] = None
    ) -> str:
        """
        Generate a response using the OpenAI API.
        
        Args:
            user_message: The user's query
            chat_history: Previous chat history
            retrieved_context: Context retrieved from RAG system
            
        Returns:
            The generated response
        """
        try:
            # Build messages array
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history)
            
            # Add retrieved context if provided
            if retrieved_context and len(retrieved_context) > 0:
                context_message = (
                    "I've retrieved the following information that might be relevant to the user's question:\n\n"
                    + "\n\n".join(retrieved_context)
                    + "\n\nPlease use this information to inform your response if relevant."
                )
                messages.append({"role": "system", "content": context_message})
            
            # Add user message
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Sending request to OpenAI API, message count: {len(messages)}")
            
            # For Phase 1, we'll mock the response since we're not yet actually calling the OpenAI API
            # In Phase 2, this will be replaced with the actual API call
            
            # Mock response for now
            response = "This is a placeholder response from the LLM processor. In Phase 2, this will be replaced with actual responses from the OpenAI API."
            
            logger.info("Generated LLM response successfully")
            return response
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return f"I apologize, but I encountered an error processing your request. Please try again later. Error: {str(e)}"
    
    async def parse_budget_modification(self, user_request: str) -> Dict[str, Any]:
        """
        Parse a budget modification request into structured data.
        
        Args:
            user_request: The user's budget modification request
            
        Returns:
            A dictionary with structured budget modification data
        """
        try:
            logger.info("Parsing budget modification request")
            
            # For Phase 1, we'll return a mock parsed request
            # In Phase 2, this will use the OpenAI API to parse the request
            
            # Mock parsed request for now
            parsed_request = {
                "action": "increase",
                "category": "Marketing",
                "line_item": "Social Media Advertising",
                "amount": None,
                "percent": 10,
                "justification": "Increased focus on digital marketing for Q2"
            }
            
            logger.info("Successfully parsed budget modification request")
            return parsed_request
        
        except Exception as e:
            logger.error(f"Error parsing budget modification: {str(e)}")
            # Return empty structure on error
            return {
                "action": None,
                "category": None,
                "line_item": None,
                "amount": None,
                "percent": None,
                "justification": None
            }


# Create a singleton instance
llm_processor = LLMProcessor()
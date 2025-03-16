from openai import OpenAI
import tiktoken
import time
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from config.settings import settings
from config.logging_config import setup_logging
from config.personas import get_persona_prompt, get_available_personas

# Set up logging
logger = setup_logging("llm_processor")

# Get API key
openai_api_key = settings.openai_api_key


class LLMProcessor:
    """Class for handling interactions with the OpenAI API."""
    
    def __init__(self):
        """Initialize the LLM processor."""
        # OpenAI client
        self.client = OpenAI(api_key=openai_api_key)
        
        # Default model and settings
        self.model = "gpt-4o-mini"
        self.max_tokens = 4096
        self.temperature = 0.7
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Token limits
        self.max_input_tokens = 8000  # Input context window size
        self.max_total_tokens = 4000  # Maximum tokens to use per request
        self.max_completion_tokens = 1000  # Maximum tokens for completion
        
        # Get available personas from the configuration file
        self.available_personas = get_available_personas()
        
        # Set default system prompt
        self.system_prompt = get_persona_prompt("default")
        
        # Encoding for token counting
        self.encoding = tiktoken.encoding_for_model(self.model)
        
        logger.info("LLM processor initialized")
    
    def _count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The number of tokens
        """
        return len(self.encoding.encode(text))
    
    def _count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count the number of tokens in a list of messages.
        
        Args:
            messages: The messages to count tokens for
            
        Returns:
            The number of tokens
        """
        token_count = 0
        for message in messages:
            # Add token count for message content
            token_count += self._count_tokens(message.get("content", ""))
            # Add tokens for message metadata (role, etc.) - typically about 4 tokens
            token_count += 4
        # Add tokens for message formatting
        token_count += 2
        return token_count
    
    def _truncate_messages(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Truncate messages to fit within token budget, preserving the most recent messages.
        
        Args:
            messages: The messages to truncate
            max_tokens: Maximum number of tokens allowed
            
        Returns:
            Truncated messages
        """
        # Always keep system message and last user message
        if len(messages) <= 2:
            return messages
        
        # Count tokens for system message and last user message
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        system_tokens = self._count_tokens(system_msg.get("content", "")) + 4 if system_msg else 0
        
        user_msg = messages[-1]
        user_tokens = self._count_tokens(user_msg.get("content", "")) + 4
        
        # Available token budget for history
        available_tokens = max_tokens - system_tokens - user_tokens - 2
        
        # If not enough budget even for minimal context, reduce system message
        if available_tokens < 0:
            if system_msg:
                # Truncate system message to fit
                max_system_tokens = max(100, max_tokens - user_tokens - 10)
                system_content = system_msg["content"]
                encoded = self.encoding.encode(system_content)
                if len(encoded) > max_system_tokens:
                    system_msg["content"] = self.encoding.decode(encoded[:max_system_tokens]) + "..."
            return [msg for msg in messages if msg["role"] == "system" or msg == user_msg]
        
        # Start with essential messages
        result = [msg for msg in messages if msg["role"] == "system" or msg == user_msg]
        remaining = [msg for msg in messages if msg["role"] != "system" and msg != user_msg]
        
        # Add as many previous messages as fit in the budget, starting from most recent
        token_count = system_tokens + user_tokens + 2
        for msg in reversed(remaining):
            msg_tokens = self._count_tokens(msg.get("content", "")) + 4
            if token_count + msg_tokens <= max_tokens:
                result.insert(1 if system_msg else 0, msg)
                token_count += msg_tokens
            else:
                break
        
        return result
    
    async def generate_response(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        retrieved_context: Optional[List[Dict[str, Any]]] = None,
        persona: str = "default"
    ) -> str:
        """
        Generate a response using the OpenAI API with proper error handling and retry logic.
        
        Args:
            user_message: The user's query
            chat_history: Previous chat history
            retrieved_context: Context retrieved from RAG system
            
        Returns:
            The generated response
        """
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Set the system prompt based on persona from config file
                selected_persona = persona if persona in self.available_personas else "default"
                system_prompt = get_persona_prompt(selected_persona)
                logger.info(f"Using persona: {selected_persona}")
                
                # Build messages array
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add chat history if provided
                if chat_history:
                    messages.extend(chat_history)
                
                # Add retrieved context if provided
                if retrieved_context and len(retrieved_context) > 0:
                    context_parts = []
                    for item in retrieved_context:
                        source_info = f" (Source: {item['source']})" if 'source' in item else ""
                        confidence = f" (Confidence: {item['score']:.2f})" if 'score' in item else ""
                        content = item["content"] if isinstance(item, dict) and "content" in item else item
                        context_parts.append(f"{content}{source_info}{confidence}")
                    
                    context_message = (
                        "I've retrieved the following information that might be relevant to the user's question:\n\n"
                        + "\n\n---\n\n".join(context_parts)
                        + "\n\nPlease use this information to inform your response if relevant. "
                        "Cite specific sources when referencing information from these documents."
                    )
                    messages.append({"role": "system", "content": context_message})
                
                # Add user message
                messages.append({"role": "user", "content": user_message})
                
                # Check token count and truncate if necessary
                token_count = self._count_message_tokens(messages)
                logger.info(f"Total token count before truncation: {token_count}")
                
                if token_count > self.max_input_tokens:
                    messages = self._truncate_messages(messages, self.max_input_tokens)
                    new_token_count = self._count_message_tokens(messages)
                    logger.info(f"Truncated messages to {new_token_count} tokens")
                
                # Calculate max tokens for completion
                available_completion_tokens = min(
                    self.max_completion_tokens,
                    self.max_total_tokens - new_token_count if 'new_token_count' in locals() else self.max_total_tokens - token_count
                )
                
                logger.info(f"Sending request to OpenAI API, message count: {len(messages)}, max tokens: {available_completion_tokens}")
                
                # Make the API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                    temperature=self.temperature,
                    max_tokens=available_completion_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                
                # Log token usage
                if hasattr(response, 'usage'):
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens
                    logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
                
                logger.info("Generated LLM response successfully")
                return response_text
            
            except Exception as e:
                logger.error(f"Error generating LLM response (attempt {retry_count+1}/{self.max_retries+1}): {str(e)}")
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2 ** (retry_count - 1)) * (0.5 + np.random.random())
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    return "I apologize, but I encountered an error processing your request. Please try again later."
    
    async def parse_budget_modification(self, user_request: str) -> Dict[str, Any]:
        """
        Parse a budget modification request into structured data using the OpenAI API.
        
        Args:
            user_request: The user's budget modification request
            
        Returns:
            A dictionary with structured budget modification data
        """
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                logger.info("Parsing budget modification request")
                
                # Create a specialized prompt for extraction
                system_prompt = (
                    "You are an AI assistant that extracts structured data from budget modification requests. "
                    "Extract the following fields from the user's request:\n"
                    "- action: The action to take (increase, decrease, or set)\n"
                    "- category: The budget category to modify\n"
                    "- line_item: The specific line item to modify\n"
                    "- amount: The absolute amount to set or change by (in dollars)\n"
                    "- percent: The percentage to change by\n"
                    "- justification: The business reason for the modification\n\n"
                    "Return the data in JSON format with these exact field names."
                )
                
                # Make the API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_request}
                    ],
                    temperature=0.1,  # Low temperature for more deterministic output
                    max_tokens=500,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    response_format={"type": "json_object"}  # Request JSON format
                )
                
                # Extract the JSON response
                try:
                    import json
                    response_text = response.choices[0].message.content
                    parsed_request = json.loads(response_text)
                    
                    # Ensure all required fields are present
                    required_fields = ["action", "category", "line_item", "amount", "percent", "justification"]
                    for field in required_fields:
                        if field not in parsed_request:
                            parsed_request[field] = None
                    
                    logger.info("Successfully parsed budget modification request")
                    return parsed_request
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {response_text}")
                    raise ValueError("Invalid JSON response from API")
            
            except Exception as e:
                logger.error(f"Error parsing budget modification (attempt {retry_count+1}/{self.max_retries+1}): {str(e)}")
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2 ** (retry_count - 1)) * (0.5 + np.random.random())
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
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
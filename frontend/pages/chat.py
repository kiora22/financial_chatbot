import streamlit as st
import requests
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def chat_page():
    """Main chat page function."""
    st.title("Financial Assistant Chat")
    st.write("Ask questions about your financial data or request budget modifications.")
    
    # Initialize session state for chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize session state for context if it doesn't exist
    if "context" not in st.session_state:
        st.session_state.context = []
    
    # Add a checkbox to enable/disable RAG
    use_rag = st.sidebar.checkbox("Use RAG (Retrieval Augmented Generation)", value=True)
    
    # Add a button to test RAG functionality
    if st.sidebar.button("Test RAG System"):
        test_rag_functionality()
    
    # Add a sidebar section to show context sources
    if st.session_state.context:
        with st.sidebar.expander("Sources Used", expanded=False):
            for idx, source in enumerate(st.session_state.context):
                st.markdown(f"**Source {idx+1}** ({source['source']})")
                st.write(f"Relevance: {source['score']:.2f}")
                st.markdown(f"> {source['content']}")
                st.markdown("---")
    
    # Chat interface
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I help with your financial questions?"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Call the backend API
        try:
            # Display thinking message
            with st.chat_message("assistant"):
                thinking_placeholder = st.empty()
                thinking_placeholder.write("Thinking...")
                
                # Make API call
                response = call_chat_api(
                    messages=st.session_state.chat_history,
                    use_rag=use_rag
                )
                
                # Extract the response details
                assistant_message = response.get("message", {"role": "assistant", "content": "I encountered an error."})
                context = response.get("context", [])
                
                # Store context in session state
                st.session_state.context = context
                
                # Replace thinking message with response
                thinking_placeholder.empty()
                st.write(assistant_message["content"])
                
                # Add assistant message to chat history
                st.session_state.chat_history.append(assistant_message)
        except Exception as e:
            st.error(f"Error: {str(e)}")


def call_chat_api(messages: List[Dict[str, str]], use_rag: bool = True) -> Dict[str, Any]:
    """
    Call the chat API to get a response.
    
    Args:
        messages: List of chat messages
        use_rag: Whether to use RAG for this request
        
    Returns:
        API response
    """
    # Prepare the request
    request_data = {
        "messages": messages,
        "user_id": "streamlit_user",  # Use an actual user ID in a real app
        "use_rag": use_rag
    }
    
    # Make the API call
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat/",
            json=request_data,
            timeout=30  # Timeout after 30 seconds
        )
        
        # Check for errors
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {
            "message": {
                "role": "assistant",
                "content": f"I'm having trouble connecting to the backend service. Error: {str(e)}"
            },
            "context": []
        }


def test_rag_functionality():
    """Test the RAG system functionality."""
    st.sidebar.write("Testing RAG system...")
    
    try:
        # Call the test endpoint
        response = requests.get(
            f"{BACKEND_URL}/api/v1/chat/test-rag",
            timeout=30
        )
        
        # Check for errors
        response.raise_for_status()
        
        # Get the test results
        test_results = response.json()
        
        # Display the test results
        if test_results["status"] == "success":
            st.sidebar.success("RAG system is working properly! ✅")
        elif test_results["status"] == "partial":
            st.sidebar.warning("RAG system is partially working. Some features may be limited.")
        else:
            st.sidebar.error("RAG system is not working correctly. Check backend logs.")
        
        # Show detailed results in an expander
        with st.sidebar.expander("Detailed Test Results", expanded=False):
            st.json(test_results)
        
    except Exception as e:
        st.sidebar.error(f"Error testing RAG system: {str(e)}")


# If this file is run directly, show the chat page
if __name__ == "__main__":
    chat_page()
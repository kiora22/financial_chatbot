import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def chat_page():
    st.title("Financial Assistant Chat")
    st.write("Ask questions about your financial data or request budget modifications.")
    
    # Initialize session state for chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
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
        
        # In Phase 1, we'll simulate the response
        # In Phase 2, this will call the backend API
        try:
            # Display thinking message
            with st.chat_message("assistant"):
                thinking_placeholder = st.empty()
                thinking_placeholder.write("Thinking...")
                
                # Instead of API call, use a mock response for Phase 1
                mock_response = {
                    "message": {
                        "role": "assistant",
                        "content": "This is a simulated response from the financial assistant. In Phase 2, this will be replaced with actual responses from the backend API."
                    },
                    "context": []
                }
                
                # Replace thinking message with response
                thinking_placeholder.empty()
                st.write(mock_response["message"]["content"])
                
                # Add assistant message to chat history
                st.session_state.chat_history.append(mock_response["message"])
        except Exception as e:
            st.error(f"Error: {str(e)}")

# If this file is run directly, show the chat page
if __name__ == "__main__":
    chat_page()
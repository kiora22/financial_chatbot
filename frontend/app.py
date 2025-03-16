import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Financial Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Basic authentication (simplified for prototype)
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.getenv("STREAMLIT_PASSWORD", "password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

# Set default session state values
if "user_id" not in st.session_state:
    st.session_state.user_id = "user123"  # Default user ID for prototype

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Main app layout
def main():
    # Sidebar navigation
    st.sidebar.title("Financial Assistant")
    page = st.sidebar.radio(
        "Navigate to",
        ["Chat", "Budget Manager", "Document Upload"]
    )
    
    # Page routing
    if page == "Chat":
        chat_page()
    elif page == "Budget Manager":
        budget_manager_page()
    elif page == "Document Upload":
        document_upload_page()

# Pages
def chat_page():
    st.title("Financial Assistant Chat")
    st.write("Ask questions about your financial data or request budget modifications.")
    
    # Check backend health
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            st.sidebar.success("Backend connected")
        else:
            st.sidebar.error("Backend connection issue")
    except Exception as e:
        st.sidebar.error(f"Backend connection error: {str(e)}")
    
    # Get available personas from the backend
    try:
        # Fetch personas from backend
        response = requests.get(f"{BACKEND_URL}/api/v1/chat/personas")
        
        if response.status_code == 200:
            personas_data = response.json()
            persona_options = {}
            for persona in personas_data:
                # Convert from snake_case to readable format
                readable_name = " ".join(word.capitalize() for word in persona.split("_"))
                if persona == "default":
                    readable_name = "Default Financial Advisor"
                elif persona == "conservative":
                    readable_name = "Conservative Financial Advisor"
                elif persona == "aggressive":
                    readable_name = "Aggressive Growth Advisor"
                elif persona == "retirement":
                    readable_name = "Retirement Planning Specialist"
                elif persona == "startup":
                    readable_name = "Startup & Venture Capital Advisor"
                persona_options[persona] = readable_name
        else:
            # Fallback if API call fails
            persona_options = {
                "default": "Default Financial Advisor",
                "conservative": "Conservative Financial Advisor",
                "aggressive": "Aggressive Growth Advisor", 
                "retirement": "Retirement Planning Specialist",
                "startup": "Startup & Venture Capital Advisor"
            }
    except Exception as e:
        st.sidebar.warning(f"Could not fetch personas: {str(e)}")
        # Fallback if API call fails
        persona_options = {
            "default": "Default Financial Advisor",
            "conservative": "Conservative Financial Advisor",
            "aggressive": "Aggressive Growth Advisor", 
            "retirement": "Retirement Planning Specialist",
            "startup": "Startup & Venture Capital Advisor"
        }
    
    # Store selected persona in session state
    if "selected_persona" not in st.session_state:
        st.session_state.selected_persona = "default"
    
    selected_persona = st.sidebar.selectbox(
        "Advisor Persona",
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x],
        index=list(persona_options.keys()).index(st.session_state.selected_persona)
    )
    
    # Update session state if changed
    if selected_persona != st.session_state.selected_persona:
        st.session_state.selected_persona = selected_persona
    
    # Add a checkbox to enable/disable RAG
    use_rag = st.sidebar.checkbox("Use Document Knowledge", value=True)
    
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
        
        # Call the backend API for the response
        try:
            # Display thinking message
            with st.chat_message("assistant"):
                thinking_placeholder = st.empty()
                thinking_placeholder.write("Thinking...")
                
                # Prepare the API request
                request_data = {
                    "messages": st.session_state.chat_history,
                    "user_id": st.session_state.user_id,
                    "use_rag": use_rag,
                    "persona": st.session_state.selected_persona
                }
                
                # Make API call
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/chat/",
                    json=request_data,
                    timeout=30
                )
                
                # Check for errors
                response.raise_for_status()
                
                # Parse the response
                chat_response = response.json()
                
                # Store retrieved context in session state for display
                if "context" in chat_response and chat_response["context"]:
                    st.session_state.context = chat_response["context"]
                else:
                    st.session_state.context = []
                
                # Replace thinking message with response
                thinking_placeholder.empty()
                st.write(chat_response["message"]["content"])
                
                # Add assistant message to chat history
                st.session_state.chat_history.append(chat_response["message"])
                
                # Display context sources in the sidebar if available
                if st.session_state.context:
                    with st.sidebar.expander("Sources Used", expanded=False):
                        for idx, source in enumerate(st.session_state.context):
                            st.markdown(f"**Source {idx+1}** ({source['source']})")
                            st.write(f"Relevance: {source['score']:.2f}")
                            st.markdown(f"> {source['content']}")
                            st.markdown("---")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def budget_manager_page():
    st.title("Budget Manager")
    st.write("View and modify your financial budget.")
    
    # Tabs for different budget views
    tab1, tab2, tab3 = st.tabs(["Budget Overview", "Line Items", "Modification History"])
    
    with tab1:
        st.header("Budget Overview")
        
        # Mock categories display
        categories = [
            {"id": 1, "name": "Marketing", "description": "Marketing and advertising expenses", "parent_category_id": None},
            {"id": 2, "name": "Operations", "description": "Operational expenses", "parent_category_id": None},
            {"id": 3, "name": "R&D", "description": "Research and development expenses", "parent_category_id": None}
        ]
        
        # Display categories
        for category in categories:
            with st.expander(f"{category['name']} - Budget Category"):
                st.write(f"**Description:** {category['description']}")
                
                # Create new button for adding line items to this category
                if st.button(f"Add Line Item to {category['name']}", key=f"add_to_{category['id']}"):
                    st.session_state.selected_category_id = category['id']
                    st.session_state.selected_category_name = category['name']
                    st.session_state.show_add_line_item = True
        
        # Add new category form
        with st.expander("Add New Budget Category"):
            with st.form("add_category_form"):
                name = st.text_input("Category Name")
                description = st.text_area("Description")
                submit_button = st.form_submit_button("Add Category")
                
                if submit_button and name:
                    st.success(f"Category '{name}' added successfully! (Simulated)")
    
    with tab2:
        st.header("Budget Line Items")
        
        # Mock line items
        line_items = [
            {"id": 1, "category_id": 1, "name": "Social Media Advertising", "amount": 10000.0, "period": "monthly", "fiscal_year": 2025},
            {"id": 2, "category_id": 1, "name": "Content Production", "amount": 5000.0, "period": "monthly", "fiscal_year": 2025},
            {"id": 3, "category_id": 2, "name": "Office Rent", "amount": 8000.0, "period": "monthly", "fiscal_year": 2025}
        ]
        
        # Filter by category
        categories = [{"id": 0, "name": "All Categories"}] + categories
        selected_category = st.selectbox(
            "Filter by Category",
            options=[c["id"] for c in categories],
            format_func=lambda x: next((c["name"] for c in categories if c["id"] == x), "Unknown"),
            index=0
        )
        
        # Filter line items by selected category
        filtered_items = line_items
        if selected_category != 0:  # 0 is "All Categories"
            filtered_items = [item for item in line_items if item["category_id"] == selected_category]
        
        # Display line items in a table
        if filtered_items:
            data = {
                "ID": [item["id"] for item in filtered_items],
                "Name": [item["name"] for item in filtered_items],
                "Amount": [f"${item['amount']:,.2f}" for item in filtered_items],
                "Period": [item["period"] for item in filtered_items],
                "Fiscal Year": [item["fiscal_year"] for item in filtered_items]
            }
            st.dataframe(data)
            
            # Select line item to modify
            selected_item_id = st.selectbox(
                "Select Line Item to Modify",
                options=[item["id"] for item in filtered_items],
                format_func=lambda x: next((item["name"] for item in filtered_items if item["id"] == x), "Unknown")
            )
            
            # Modification form
            selected_item = next((item for item in filtered_items if item["id"] == selected_item_id), None)
            if selected_item:
                with st.form("modify_budget_form"):
                    st.write(f"Modifying: **{selected_item['name']}**")
                    st.write(f"Current Amount: **${selected_item['amount']:,.2f}**")
                    
                    new_amount = st.number_input("New Amount", min_value=0.0, value=selected_item["amount"], step=100.0)
                    justification = st.text_area("Justification")
                    
                    submit_button = st.form_submit_button("Apply Modification")
                    
                    if submit_button:
                        if new_amount != selected_item["amount"]:
                            st.success(f"Budget modified successfully! (Simulated)")
                            st.info(f"Changed from ${selected_item['amount']:,.2f} to ${new_amount:,.2f}")
                        else:
                            st.warning("No change in amount detected.")
        else:
            st.info("No line items found for the selected category.")
    
    with tab3:
        st.header("Modification History")
        
        # Select line item to view history
        selected_item_id = st.selectbox(
            "Select Line Item",
            options=[item["id"] for item in line_items],
            format_func=lambda x: next((item["name"] for item in line_items if item["id"] == x), "Unknown")
        )
        
        # Mock modification history data
        mock_history = [
            {"id": 1, "line_item_id": 1, "previous_amount": 10000.0, "new_amount": 12000.0, "modification_date": "2025-01-15", "user_id": "user123", "justification": "Increased allocation due to Q1 campaign"},
            {"id": 2, "line_item_id": 1, "previous_amount": 12000.0, "new_amount": 11000.0, "modification_date": "2025-02-10", "user_id": "user123", "justification": "Adjusted based on performance metrics"}
        ]
        
        # Filter history for selected line item
        item_history = [mod for mod in mock_history if mod["line_item_id"] == selected_item_id]
        
        if item_history:
            # Display history in a table
            for mod in item_history:
                with st.expander(f"Modified on {mod['modification_date']}"):
                    st.write(f"**Previous Amount:** ${mod['previous_amount']:,.2f}")
                    st.write(f"**New Amount:** ${mod['new_amount']:,.2f}")
                    st.write(f"**Change:** ${mod['new_amount'] - mod['previous_amount']:,.2f}")
                    st.write(f"**User:** {mod['user_id']}")
                    st.write(f"**Justification:** {mod['justification']}")
        else:
            st.info("No modification history found for this line item.")

def document_upload_page():
    st.title("Document Upload")
    st.write("Upload financial documents to enhance the assistant's knowledge.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "xlsx", "csv", "txt"])
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully! (Simulated)")
        
        # Display file info
        st.write("File Information:")
        st.json({
            "filename": uploaded_file.name,
            "size": f"{uploaded_file.size / 1024:.2f} KB",
            "type": uploaded_file.type
        })
        
        # Process button
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                # Simulate processing delay
                import time
                time.sleep(2)
                
                st.success("Document processed and indexed successfully! (Simulated)")
                st.info("The assistant can now retrieve information from this document when answering queries.")

# Run the app
if check_password():
    main()
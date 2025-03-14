# Architecture Document: Financial Assistant with RAG and Budget Modification (Prototype)

## 1. Overview
This document outlines the architecture for a financial assistant chatbot prototype that utilizes Retrieval-Augmented Generation (RAG) to deliver context-aware responses. The chatbot will act as a business support assistant with a financial perspective, enabling users to query financial data, receive contextual insights, and modify financial budgets in real time. This prototype prioritizes simplicity and rapid development.

## 2. Core Components
### 2.1 Frontend Interface
- **Purpose:** User interaction with the financial assistant.
- **Technology Choice: Streamlit**
  - Dashboard functionality for financial data visualization
  - Simple built-in authentication (password protection)
  - Input field for user queries
  - Financial result display
  - Interactive controls for budget adjustments

### 2.2 Backend API
- **Purpose:** Processes user queries, retrieves financial context, and updates budgets.
- **Technology Choice: FastAPI**
  - REST API endpoints for:
    - Query processing
    - Budget retrieval
    - Budget modification
  - Simple JSON response format
  - API versioning for future compatibility

### 2.3 LLM Processing Module
- **Purpose:** Handles prompt generation, financial persona application, and response synthesis.
- **Technology Choice: OpenAI API (GPT-4o or GPT-4o mini)**
  - Pre-configured financial support persona with domain-specific knowledge
  - Token budget management (set maximum tokens per interaction)
  - Error handling for API failures
  - Response parsing for structured financial outputs

### 2.4 RAG (Retrieval-Augmented Generation) System
- **Purpose:** Enhances responses with relevant financial data and context.
- **Technology Choices:**
  - **Vector Database: ChromaDB** (local instance for simplicity)
  - **Embedding Model: OpenAI Ada 2** embeddings
  - **Document Store: File-based storage** (JSON/CSV for prototype simplicity)
  - **Retrieval Logic:** Top-k similarity search with relevance scoring

### 2.5 Budget Modification Engine
- **Purpose:** Enables LLM to adjust financial forecasts based on user prompts.
- **Technology Choices:**
  - **Financial Data Store: SQLite**
  - **Modification Logic:** Template-based structure for budget adjustments
  - **Data Refresh:** Polling-based updates to the frontend (simple approach for prototype)

### 2.6 Document Ingestion Pipeline
- **Purpose:** Provides easy upload and processing of financial documents for RAG.
- **Technology Choices:**
  - **Document Drop Zone:** Dedicated folder with file watcher
  - **File Formats:** PDF, DOCX, XLSX, CSV, TXT
  - **Ingestion API:** FastAPI endpoints for document upload and status checking
  - **Processing Queue:** Simple queue system for background processing

### 2.7 Logging & Monitoring
- **Purpose:** Tracks system performance and user interactions.
- **Technology Choices:**
  - **Simple logging:** Python's built-in logging module to files
  - **Chat history:** SQLite table for query tracking
  - **Financial modification logging:** Audit trail in SQLite

## 3. Component Design
### 3.1 Request Flow
1. User submits a financial query through the Streamlit interface
2. FastAPI endpoint receives the query and user context
3. LLM module crafts a search query for the RAG system
4. ChromaDB returns relevant financial document chunks
5. LLM generates response with retrieved context
6. If budget modification is requested:
   - LLM parses the modification intent
   - Structured changes are applied to SQLite database
   - Success/failure status is returned
7. Response and updated financial data are displayed in Streamlit

### 3.2 Persona Handling
- System uses a consistent financial expert persona
- Prompt template includes:
  - Financial advisor role definition
  - Instructions for handling numerical precision
  - Guidelines for budget recommendations
  - Example dialogues for common financial scenarios

### 3.3 Financial Data Schema
- **Budget Categories Table:**
  - id (PRIMARY KEY)
  - name (e.g., Marketing, Operations, R&D)
  - description
  - parent_category_id (for hierarchical structure)

- **Budget Line Items Table:**
  - id (PRIMARY KEY)
  - category_id (FOREIGN KEY)
  - name (e.g., Social Media Ads, Content Production)
  - amount
  - period (monthly, quarterly, annual)
  - fiscal_year
  - notes

- **Budget Modifications Table:**
  - id (PRIMARY KEY)
  - line_item_id (FOREIGN KEY)
  - previous_amount
  - new_amount
  - modification_date
  - user_id
  - justification

### 3.4 Document Ingestion Process
1. **Document Upload Methods:**
   - Web interface via Streamlit
   - Direct file drop to monitored folder
   - API endpoint for programmatic uploads

2. **Processing Pipeline:**
   - Document validation (file type, size, content)
   - Text extraction (PDF parsing, DOCX processing)
   - Metadata extraction (author, date, title)
   - Text chunking (by paragraph, section, or fixed size)
   - Embedding generation
   - Vector database storage

3. **Document Management:**
   - Document tagging and categorization
   - Version control for updated documents
   - Deletion and replacement capabilities

### 3.5 Live Budget Modification
- Users can request budget adjustments (e.g., "Increase marketing budget by 10%")
- LLM interprets request using a structured template:
  ```
  {
    "action": "increase|decrease|set",
    "category": "category_name",
    "line_item": "line_item_name|null",
    "amount": value,
    "percent": percentage|null,
    "justification": "reason for change"
  }
  ```
- Validation rules prevent unreasonable changes:
  - Maximum percentage change limits
  - Total budget constraints
  - Required justification for changes above threshold

### 3.6 Error Handling
- **Query Processing Errors:**
  - Timeout handling for LLM calls
  - Fallback responses for API failures
  - Contextual error messages for users

- **Budget Modification Errors:**
  - Validation failures (amount limits, permissions)
  - Data integrity constraints
  - Conflict resolution for concurrent modifications

- **Data Retrieval Errors:**
  - Empty result handling
  - Relevance thresholds for RAG responses
  - Fallback to general financial advice when context is insufficient

## 4. Prompt Engineering
### 4.1 Sample RAG Prompt Template
```
You are a financial assistant with access to the following financial documents:
[RETRIEVED_CONTEXT]

Based on this information and your financial expertise, please answer the user's question:
[USER_QUERY]

If you need to reference specific financial figures, cite the source from the context.
If the information is not available in the context, acknowledge the limits of your knowledge.
```

### 4.2 Sample Budget Modification Prompt
```
You are a financial assistant that helps modify budgets. 
Parse the following request into a structured format:
[USER_REQUEST]

Output format:
{
  "action": "increase|decrease|set",
  "category": "specific_category",
  "line_item": "specific_line_item or null if entire category",
  "amount": absolute_value_or_null,
  "percent": percentage_value_or_null,
  "justification": "extracted reason for change"
}

If the request is ambiguous or missing information, output null for that field.
```

## 5. Evaluation Metrics
- **Response Accuracy:**
  - Correctness of financial calculations
  - Relevance of retrieved context
  - Alignment with financial best practices

- **Budget Modification Success:**
  - Percentage of successfully parsed modification requests
  - Error rate in budget updates
  - User satisfaction with changes

- **Performance Metrics:**
  - Average response time
  - RAG retrieval quality (precision/recall)
  - Token usage efficiency

## 6. Docker Containerization
### 6.1 Container Structure
- **frontend:** Streamlit application
- **backend:** FastAPI service
- **document_processor:** Document ingestion service
- **vector_db:** ChromaDB service
- **financial_db:** SQLite database with volume mount


## 7. Project Repository Structure
```
financial_assistant/
|-- frontend/
|   |-- app.py                      # Streamlit application
|   |-- pages/
|      |-- chat.py                  # Chat interface
|      |-- budget_manager.py        # Budget visualization and editing
|      |-- document_upload.py       # Document ingestion interface
|-- backend/
|   |-- main.py                     # FastAPI application entry point
|   |-- routers/
|      |-- chat.py                  # Chat endpoints
|      |-- budget.py                # Budget modification endpoints
|      |-- documents.py             # Document management endpoints
|   |-- core/
|      |-- llm_processor.py         # LLM interaction handling
|      |-- rag_retrieval.py         # Context retrieval logic
|      |-- budget_modification.py   # Budget change application logic
|-- document_processor/
|   |-- main.py                     # Document processor service
|   |-- processors/
|      |-- pdf_processor.py         # PDF parsing
|      |-- docx_processor.py        # Word document parsing
|      |-- excel_processor.py       # Excel file parsing
|   |-- watcher.py                  # File system watcher
|-- data/
|   |-- documents/                  # Processed document storage
|   |-- uploads/                    # Temporary storage for uploaded files
|   |-- document_drop/              # Monitored folder for automatic ingestion
|   |-- financial_db.sqlite         # SQLite database file
|   |-- vector_store/               # ChromaDB files
|-- utils/
|   |-- text_processing.py          # Text chunking and cleaning
|   |-- embedding_generator.py      # Vector embedding creation
|   |-- schema.py                   # Database models and schemas
|-- config/
|   |-- settings.py                 # Configuration variables
|   |-- logging_config.py           # Logging setup
|-- tests/
|   |-- test_llm.py
|   |-- test_budget_modification.py
|   |-- test_rag.py
|-- dockerfiles/
|   |-- frontend.Dockerfile
|   |-- backend.Dockerfile
|   |-- document_processor.Dockerfile
|-- docker-compose.yml              # Multi-container setup
|-- Makefile                        # Build and deployment commands
|-- requirements.txt                # Dependencies
|-- README.md                       # Project documentation
```

## 8. Implementation Plan
### Phase 1
- Set up Docker containers and basic infrastructure
- Implement SQLite schema for financial data
- Create simple FastAPI endpoints
- Connect OpenAI API for basic query handling

### Phase 2
- Implement RAG system with ChromaDB
- Create document ingestion flow and drop folder
- Build basic budget modification logic
- Add financial data visualization

### Phase 3
- Refine prompt engineering
- Implement error handling and validation
- Add logging and basic analytics
- Polish UI/UX for demo purposes

## 9. Conclusion
This prototype architecture provides a simplified yet functional approach to building a financial assistant chatbot with RAG and real-time budget modification capabilities. The containerized approach with Docker Compose allows for easy deployment and scaling, while the document drop folder and ingestion pipeline provide a straightforward method for adding new knowledge to the system. By focusing on specific technology choices and streamlined implementation, the prototype can be developed quickly while demonstrating core functionality.

# Financial Assistant with RAG and Budget Modification

A financial assistant chatbot prototype that utilizes Retrieval-Augmented Generation (RAG) to deliver context-aware responses. The system acts as a business support assistant with a financial perspective, enabling users to query financial data, receive contextual insights, and modify financial budgets in real time.

## Project Overview

This prototype prioritizes simplicity and rapid development, using:

- **Streamlit** for the frontend interface
- **FastAPI** for the backend API
- **OpenAI API** for LLM processing
- **ChromaDB** for vector storage
- **SQLite** for financial data storage

## Features

- Chat interface for financial queries
- Budget management and visualization
- Document upload and processing for RAG
- Context-aware financial responses
- Support for multiple document formats (PDF, DOCX, XLSX, CSV, TXT)
- Automatic document ingestion and processing

## Project Structure

```
financial_assistant/
|-- frontend/               # Streamlit application
|-- backend/                # FastAPI service
|   |-- routers/            # API endpoints
|   |-- core/               # Business logic
|-- document_processor/     # Document ingestion service
|   |-- processors/         # File type processors
|-- utils/                  # Shared utilities
|-- config/                 # Configuration
|-- data/                   # Data storage
|   |-- document_drop/      # Folder for document ingestion
|   |-- documents/          # Processed documents
|   |-- uploads/            # User-uploaded files
|   |-- vector_store/       # Vector database storage
|-- dockerfiles/            # Docker configuration
|-- docker-compose.yaml     # Multi-container setup
|-- Makefile                # Build and deployment commands
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- (Optional) Git for version control

### Environment Setup

1. Clone the repository
   ```bash
   git clone [repository-url]
   cd financial-assistant
   ```

2. Create an environment file
   ```bash
   touch .env
   ```

3. Edit the `.env` file to add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

### Running with Docker

Build and start the application:

```bash
make setup   # First-time setup: build, initialize database, run
```

Or separately:

```bash
make build   # Build Docker images
make run     # Run the application in detached mode
```

For development:

```bash
make dev     # Run with logs in the foreground
```

### Accessing the Application

- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Docker Management

```bash
make stop    # Stop the application
make clean   # Remove containers, volumes, and temporary files
make logs    # View logs
make shell   # Open a shell in a container
```

## Development Commands

```bash
make init-db         # Initialize the database
make test            # Run tests
make process-docs    # Process documents in the drop folder
```

## Working with RAG

### Adding Documents

To add documents to the RAG system:

1. Place document files in the `data/document_drop` folder
2. The system will automatically process them
3. Alternatively, use the document upload interface in the frontend

Supported document formats:
- PDF (.pdf)
- Microsoft Word (.docx)
- Microsoft Excel (.xlsx, .xls)
- CSV (.csv)
- Plain text (.txt)

### Testing RAG Functionality

1. Access the chat interface
2. Use the "Test RAG System" button in the sidebar
3. View test results to verify system functionality
4. Try asking questions related to your documents

## Project Status

This project follows a phased implementation approach:

- **Phase 1 (Completed)**: Basic infrastructure, API endpoints, UI, and database setup
- **Phase 2 (Current)**: RAG implementation, document processing, and retrieval functionality
- **Phase 3 (Planned)**: LLM integration, budget modification, and frontend enhancements

For detailed implementation status, see [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

## License

[Specify your license here]
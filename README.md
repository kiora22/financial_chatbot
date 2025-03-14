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
- Real-time budget modifications
- Document upload and processing for RAG
- Context-aware financial responses

## Project Structure

```
financial_assistant/
|-- frontend/               # Streamlit application
|-- backend/                # FastAPI service
|   |-- routers/            # API endpoints
|   |-- core/               # Business logic
|-- document_processor/     # Document ingestion service
|-- utils/                  # Shared utilities
|-- config/                 # Configuration
|-- data/                   # Data storage
|-- dockerfiles/            # Docker configuration
|-- docker-compose.yml      # Multi-container setup
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

2. Copy the example environment file and edit it
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file to add your OpenAI API key

### Running with Docker

Build and start the application:

```bash
make setup   # First-time setup: build, initialize database, generate sample data
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
make generate-sample # Generate sample data
make test            # Run tests
make process-docs    # Process documents in the drop folder
```

## Project Status

This project is a prototype in active development and follows a phased implementation approach:

- **Phase 1 (Current)**: Basic infrastructure, API endpoints, UI, and database setup
- **Phase 2 (Planned)**: RAG implementation, document processing, and budget modification
- **Phase 3 (Planned)**: Prompt engineering, error handling, and UX refinements

## License

[Specify your license here]
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.logging_config import setup_logging
from utils.schema import init_db
from backend.routers import chat, budget

# Set up logging
logger = setup_logging("backend")

# Initialize the database
engine = init_db(settings.database_url)

# Create FastAPI app
app = FastAPI(
    title="Financial Assistant API",
    description="API for financial assistant chatbot with RAG and budget modification",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(budget.router, prefix="/api/v1/budget", tags=["budget"])


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Financial Assistant API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    """Run the application directly."""
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False,
        debug=False,
        #reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
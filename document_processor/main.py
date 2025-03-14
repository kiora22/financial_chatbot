import os
import sys

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("document_processor")


def main():
    """Main function for the document processor service."""
    logger.info("Starting document processor service")
    logger.info(f"Watching folder: {settings.document_watch_folder}")
    
    # In Phase 2, this will set up a file watcher and process documents
    # For Phase 1, this is just a placeholder
    
    logger.info("Document processor service started")
    
    # Keep the service running
    try:
        # This would be replaced with the actual file watcher in Phase 2
        import time
        while True:
            logger.debug("Document processor is running...")
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Document processor service stopped")


if __name__ == "__main__":
    """Run the document processor when script is executed directly."""
    main()
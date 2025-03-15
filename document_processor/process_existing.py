import os
import sys
import asyncio

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_processor.main import process_existing_files
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("process_existing")


async def main():
    """Run the process_existing_files function."""
    logger.info("Starting manual processing of existing files")
    await process_existing_files()
    logger.info("Completed manual processing of existing files")


if __name__ == "__main__":
    """Run the script when executed directly."""
    asyncio.run(main())
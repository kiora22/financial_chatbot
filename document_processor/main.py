import os
import sys
import time
import asyncio
import hashlib
import uuid
from typing import Dict, List, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging("document_processor")

# Global execution UUID to track unique process executions
EXECUTION_UUID = str(uuid.uuid4())
logger.info(f"Process execution UUID: {EXECUTION_UUID}")

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from document_processor.processors import get_processor_for_file
from document_processor.vector_db_client import vector_db_client



# We'll use this to track which execution is actually running the watcher
ACTIVE_WATCHER = None
WATCHER_LOCK_FILE = "/tmp/document_processor_watcher.lock"


class DocumentEventHandler(FileSystemEventHandler):
    """
    File system event handler for document processing.
    Watches for new files and modifications and processes them.
    """
    
    def __init__(self, processor):
        self.processor = processor
        self.processing_queue = asyncio.Queue()
        self.processed_files = set()
        
        # Start the processing task
        asyncio.create_task(self._process_queue())
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = event.src_path
            logger.info(f"New file detected: {file_path}")
            asyncio.create_task(self._enqueue_file(file_path))
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            file_path = event.src_path
            logger.info(f"Modified file detected: {file_path}")
            asyncio.create_task(self._enqueue_file(file_path))
    
    async def _enqueue_file(self, file_path: str):
        """Add file to processing queue with debounce to avoid duplicate processing."""
        # Calculate file hash to check if it's changed
        try:
            # Wait a bit to ensure file is fully written
            await asyncio.sleep(2)
            
            # Skip temporary files and hidden files
            filename = os.path.basename(file_path)
            if filename.startswith('.') or filename.startswith('~'):
                logger.debug(f"Skipping temporary/hidden file: {file_path}")
                return
            
            # Get file size in MB
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            max_size = settings.max_document_size_mb
            
            # Skip files that are too large
            if file_size > max_size:
                logger.warning(f"Skipping file {file_path} - size {file_size:.2f} MB exceeds limit of {max_size} MB")
                return
            
            file_hash = self._get_file_hash(file_path)
            file_key = f"{file_path}:{file_hash}"
            
            # If we've already processed this exact file (same path and hash), skip it
            if file_key in self.processed_files:
                logger.debug(f"Skipping already processed file: {file_path}")
                return
            
            # Otherwise, add to the queue
            logger.debug(f"Adding file to processing queue: {file_path}")
            await self.processing_queue.put((file_path, file_hash, file_key))
            
        except Exception as e:
            logger.error(f"Error queueing file {file_path}: {str(e)}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calculate a hash of the file to detect changes."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def _process_queue(self):
        """Process files from the queue."""
        while True:
            try:
                # Get the next file from the queue
                file_path, file_hash, file_key = await self.processing_queue.get()
                
                logger.info(f"Processing file from queue: {file_path}")
                
                # Process the file
                success = await self.processor.process_file(file_path)
                
                # Mark as processed if successful
                if success:
                    self.processed_files.add(file_key)
                    logger.info(f"Successfully processed and marked file: {file_path}")
                
                # If processed files set is getting too large, prune old entries
                if len(self.processed_files) > 1000:
                    logger.info("Pruning processed files cache")
                    self.processed_files = set(list(self.processed_files)[-500:])
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in queue processing: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying


class DocumentProcessor:
    """
    Main document processor service.
    Handles processing documents and storing them in the vector database.
    """
    
    def __init__(self):
        """Initialize the document processor."""
        self.watch_folder = settings.document_watch_folder
        self.documents_folder = "data/documents"
        self.uploads_folder = "data/uploads"
        self.vector_db_client = vector_db_client
        
        # Ensure folders exist
        os.makedirs(self.watch_folder, exist_ok=True)
        os.makedirs(self.documents_folder, exist_ok=True)
        os.makedirs(self.uploads_folder, exist_ok=True)
    
    async def process_file(self, file_path: str) -> bool:
        """
        Process a single document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Get the appropriate processor for this file type
            processor = get_processor_for_file(file_path)
            
            # Process the document
            result = await processor.process(file_path)
            
            if not result["success"]:
                logger.error(f"Processing failed for {file_path}: {result.get('error', 'Unknown error')}")
                return False
            
            # Add chunks to vector database
            chunks = result.get("chunks", [])
            if not chunks:
                logger.warning(f"No chunks found in document: {file_path}")
                return False
            
            logger.info(f"Adding {len(chunks)} chunks to vector database for {file_path}")
            
            # Add each chunk to the vector database
            for chunk in chunks:
                await self.vector_db_client.add_document(
                    document_id=chunk["id"],
                    text=chunk["text"],
                    metadata= ", ".join(chunk["metadata"]) if isinstance(chunk["metadata"], list) else chunk["metadata"]
                )
            
            logger.info(f"Successfully processed document: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
            return False
    
    async def scan_existing_files(self):
        """Scan and process existing files in the watch folder."""
        try:
            logger.info(f"Scanning existing files in {self.watch_folder}")
            
            # Get all files in the watch folder
            files = []
            for root, _, filenames in os.walk(self.watch_folder):
                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                        
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
            
            if not files:
                logger.info("No existing files found to process")
                return
            
            logger.info(f"Found {len(files)} existing files to process")
            
            # Process each file
            for file_path in files:
                await self.process_file(file_path)
            
            logger.info("Completed processing existing files")
            
        except Exception as e:
            logger.error(f"Error scanning existing files: {str(e)}")
    
    async def start_watching(self):
        """Start watching for file system events."""
        try:
            logger.info(f"Starting file system watcher on: {self.watch_folder}")
            
            # Create an observer and event handler
            event_handler = DocumentEventHandler(self)
            observer = Observer()
            observer.schedule(event_handler, self.watch_folder, recursive=True)
            
            # Start the observer
            observer.start()
            logger.info("File system watcher started")
            
            # Keep the service running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            
            observer.join()
            logger.info("File system watcher stopped")
            
        except Exception as e:
            logger.error(f"Error starting file system watcher: {str(e)}")


async def process_existing_files():
    """Scan and process existing files without starting the watcher."""
    #processor = DocumentProcessor()
    #await processor.scan_existing_files()
    pass

async def main():
    """Main function for the document processor service."""
    global ACTIVE_WATCHER, EXECUTION_UUID
    
    logger.info(f"Starting document processor service (UUID: {EXECUTION_UUID})")
    logger.info(f"Watching folder: {settings.document_watch_folder}")
    logger.info(f"Loaded module in PID {os.getpid()}")
    
    # Check if we're the active watcher
    try:
        # Try to read the current active watcher
        if os.path.exists(WATCHER_LOCK_FILE):
            with open(WATCHER_LOCK_FILE, 'r') as f:
                ACTIVE_WATCHER = f.read().strip()
        
        # If no active watcher, we become the active watcher
        if not ACTIVE_WATCHER:
            ACTIVE_WATCHER = EXECUTION_UUID
            with open(WATCHER_LOCK_FILE, 'w') as f:
                f.write(EXECUTION_UUID)
        
        # If we're not the active watcher, exit after scanning files
        if ACTIVE_WATCHER != EXECUTION_UUID:
            logger.info(f"Another watcher is active (UUID: {ACTIVE_WATCHER}). This instance (UUID: {EXECUTION_UUID}) will only process existing files.")
            
            # Process existing files
            processor = DocumentProcessor()
            await processor.scan_existing_files()
            
            logger.info(f"Finished processing existing files. Exiting instance (UUID: {EXECUTION_UUID}).")
            return
        
        # If we are the active watcher, run the full service
        logger.info(f"This instance (UUID: {EXECUTION_UUID}) is the active watcher.")
        
        # Initialize the processor
        processor = DocumentProcessor()
        
        # First process any existing files
        await processor.scan_existing_files()
        
        # Then start watching for new files
        await processor.start_watching()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)


if __name__ == "__main__":
    """Run the document processor when script is executed directly."""
    logger.info(f"__main__ section called (UUID: {EXECUTION_UUID})")
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}", exc_info=True)
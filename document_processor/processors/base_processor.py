"""
Base document processor definition.
All document processors should inherit from this class.
"""

import os
import sys
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.text_processing import clean_text, chunk_text, extract_metadata
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("document_processor")


class BaseDocumentProcessor(ABC):
    """
    Base class for document processors.
    Each specific file type processor should inherit from this.
    """
    
    def __init__(self):
        """Initialize document processor."""
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Processing results with metadata and chunks
        """
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {
                    "success": False,
                    "error": "File not found",
                    "file_path": file_path
                }
            logger.info("File exists")
            
            # Extract text from the document
            extracted_text = await self.extract_text(file_path)
            
            if not extracted_text or extracted_text.strip() == "":
                logger.warning(f"No text extracted from {file_path}")
                return {
                    "success": False,
                    "error": "No text extracted",
                    "file_path": file_path
                }

            # Extract basic metadata
            filename = os.path.basename(file_path)
            file_metadata = extract_metadata(extracted_text, filename)

            # Add processing metadata
            file_metadata["processed_date"] = datetime.now().isoformat()
            file_metadata["processor"] = self.__class__.__name__
            
            # Get additional metadata specific to the file type
            additional_metadata = await self.extract_metadata(file_path)
            if additional_metadata:
                file_metadata.update(additional_metadata)

            # Clean the text
            cleaned_text = clean_text(extracted_text)

            # Chunk the text
            chunks = chunk_text(
                cleaned_text, 
                chunk_size=self.chunk_size, 
                chunk_overlap=self.chunk_overlap
            )

            # Generate chunk IDs
            document_id = str(uuid.uuid4())
            chunk_results = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_{i}"
                chunk_metadata = {
                    "source": filename,
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **file_metadata
                }
                
                chunk_results.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": chunk_metadata
                })

            logger.info(f"Document processed successfully: {file_path}, chunks: {len(chunks)}")
            
            return {
                "success": True,
                "document_id": document_id,
                "file_path": file_path,
                "metadata": file_metadata,
                "chunks": chunk_results,
                "text": cleaned_text,
                "total_chunks": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    @abstractmethod
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text
        """
        pass
    
    async def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a document file.
        This method can be overridden by subclasses to extract file-specific metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted metadata or None
        """
        return None
"""
Text file processor.
Handles plain text files (.txt).
"""

import os
from typing import Dict, Any, Optional

from document_processor.processors.base_processor import BaseDocumentProcessor
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("text_processor")


class TextProcessor(BaseDocumentProcessor):
    """Processor for plain text files."""
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from a plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Extracting text from: {file_path}")
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
            return text
            
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decoding failed for {file_path}, trying with latin-1")
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
            logger.info(f"Successfully extracted {len(text)} characters from {file_path} using latin-1")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    async def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Extracted metadata
        """
        try:
            stat_info = os.stat(file_path)
            
            metadata = {
                "file_size_bytes": stat_info.st_size,
                "created_at": stat_info.st_ctime,
                "modified_at": stat_info.st_mtime,
                "file_extension": "txt"
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
            return None
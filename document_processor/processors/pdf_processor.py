"""
PDF file processor.
Handles PDF files using PyPDF2.
"""

import os
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader

from document_processor.processors.base_processor import BaseDocumentProcessor
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("pdf_processor")


class PDFProcessor(BaseDocumentProcessor):
    """Processor for PDF files."""
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Extracting text from PDF: {file_path}")
            
            # Open the PDF file
            with open(file_path, 'rb') as file:
                # Create a PDF reader object
                pdf = PdfReader(file)
                
                # Extract text from each page
                text = ""
                for page_num in range(len(pdf.pages)):
                    page = pdf.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""
    
    async def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted metadata
        """
        try:
            # Get file stats
            stat_info = os.stat(file_path)
            
            # Initialize metadata with file stats
            metadata = {
                "file_size_bytes": stat_info.st_size,
                "created_at": stat_info.st_ctime,
                "modified_at": stat_info.st_mtime,
                "file_extension": "pdf"
            }
            
            # Extract PDF-specific metadata
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                
                # Get document info if available
                if pdf.metadata:
                    pdf_info = pdf.metadata
                    
                    # Add selected metadata (convert from PDF format if needed)
                    if pdf_info.title:
                        metadata["title"] = pdf_info.title
                    if pdf_info.author:
                        metadata["author"] = pdf_info.author
                    if pdf_info.subject:
                        metadata["subject"] = pdf_info.subject
                    if pdf_info.creator:
                        metadata["creator"] = pdf_info.creator
                
                # Add page count
                metadata["page_count"] = len(pdf.pages)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from PDF {file_path}: {str(e)}")
            return None
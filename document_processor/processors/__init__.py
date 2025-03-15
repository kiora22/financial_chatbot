"""
Document processor initialization module.
This module registers document processors for different file types.
"""

from document_processor.processors.base_processor import BaseDocumentProcessor
from document_processor.processors.text_processor import TextProcessor
from document_processor.processors.pdf_processor import PDFProcessor
from document_processor.processors.docx_processor import DocxProcessor
from document_processor.processors.xlsx_processor import ExcelProcessor
from document_processor.processors.csv_processor import CSVProcessor

# Register processors for different file types
PROCESSORS = {
    # Text files
    "txt": TextProcessor,
    
    # PDF files
    "pdf": PDFProcessor,
    
    # Microsoft Word documents
    "docx": DocxProcessor,
    "doc": DocxProcessor,  # Note: Legacy .doc files may not be fully supported
    
    # Microsoft Excel spreadsheets
    "xlsx": ExcelProcessor,
    "xls": ExcelProcessor,  # Note: Legacy .xls files may not be fully supported
    
    # CSV files
    "csv": CSVProcessor
}

def get_processor_for_file(file_path: str) -> BaseDocumentProcessor:
    """
    Get the appropriate processor for a given file.
    
    Args:
        file_path: The path to the file
        
    Returns:
        A document processor instance
    """
    # Extract file extension
    file_extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
    
    # Get the processor class for this extension
    processor_class = PROCESSORS.get(file_extension, TextProcessor)
    
    # Return a new instance of the processor
    return processor_class()
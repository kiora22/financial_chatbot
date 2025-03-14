import re
from typing import List, Dict, Any, Optional

from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("text_processing")


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, newlines, etc.
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    cleaned_text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    Split text into chunks for processing.
    
    Args:
        text: The text to split
        chunk_size: The maximum size of each chunk
        chunk_overlap: The amount of overlap between chunks
        
    Returns:
        A list of text chunks
    """
    # Clean the text first
    text = clean_text(text)
    
    # For Phase 1, we'll use a simple character-based chunking
    # In Phase 2, this will be enhanced with more intelligent chunking
    
    # If the text is shorter than the chunk size, return it as is
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get the chunk
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        
        # If this is not the last chunk and we're not at the end of the text,
        # try to find a good breaking point (period, question mark, etc.)
        if end < len(text):
            # Look for the last sentence break in the chunk
            last_period = max(
                chunk.rfind('. '),
                chunk.rfind('? '),
                chunk.rfind('! '),
                chunk.rfind('\n')
            )
            
            if last_period != -1:
                # +2 to include the period and space
                end = start + last_period + 2
                chunk = text[start:end]
        
        chunks.append(chunk)
        
        # Move to the next chunk, with overlap
        start = end - chunk_overlap
    
    logger.debug(f"Split text into {len(chunks)} chunks")
    return chunks


def extract_metadata(text: str, filename: str) -> Dict[str, Any]:
    """
    Extract metadata from text and filename.
    
    Args:
        text: The text to extract metadata from
        filename: The filename
        
    Returns:
        A dictionary of metadata
    """
    # For Phase 1, we'll return basic metadata
    # In Phase 2, this will extract more sophisticated metadata
    
    # Get file extension
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    # Extract simple metadata
    metadata = {
        "filename": filename,
        "file_type": file_extension,
        "character_count": len(text),
        "word_count": len(text.split()),
        "processed_date": None  # Will be set when actually processing
    }
    
    return metadata
import re
import datetime
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
    
    # If the text is shorter than the chunk size, return it as is
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):

        #Check that we're not in range of the exit condition, if so, then exit.
        if start + chunk_overlap >= len(text):
            break
        
        # Get the chunk
        end = min(start + chunk_size, len(text))
        logger.info(f"start: {start} , target: {len(text)}, end {end}")
        
        # If this is not the last chunk, try to find a good breaking point
        if end < len(text):
            # Look for natural break points in order of preference
            break_points = [
                text.rfind('. ', start, end),  # Sentence ending with period
                text.rfind('? ', start, end),  # Question
                text.rfind('! ', start, end),  # Exclamation
                text.rfind('\n', start, end),  # Newline
                text.rfind(': ', start, end),  # Colon
                text.rfind('; ', start, end),  # Semicolon
                text.rfind(', ', start, end),  # Comma
            ]
            
            # Find the first valid break point
            last_break = -1
            for point in break_points:
                if point != -1:
                    last_break = point
                    break
                    
            # If we found a valid break point, use it
            if last_break != -1:
                # Include the punctuation and space
                end = last_break + 2
        
        # Get the chunk text
        chunk = text[start:end].strip()
        
        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)
        
        # Move to the next chunk with overlap
        start = end - chunk_overlap
        
        # Ensure we're making progress
        if start >= end:
            start = end
    
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
    # Get file extension
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    # Current timestamp
    current_time = datetime.datetime.now().isoformat()
    
    # Extract simple metadata
    metadata = {
        "filename": filename,
        "file_type": file_extension,
        "character_count": len(text),
        "word_count": len(text.split()),
        "processed_date": current_time
    }
    
    # Try to identify document type based on content patterns
    document_type = determine_document_type(text, filename)
    if document_type:
        metadata["document_type"] = document_type
    
    # Try to extract any dates mentioned in the text
    dates = extract_dates(text)
    if dates:
        metadata["dates_mentioned"] = dates
    
    return metadata


def determine_document_type(text: str, filename: str) -> Optional[str]:
    """
    Try to determine the document type based on content.
    
    Args:
        text: The document text
        filename: The filename
        
    Returns:
        Document type if identified, else None
    """
    # Check file name patterns
    lower_name = filename.lower()
    
    if any(term in lower_name for term in ["budget", "financial", "finance", "fiscal"]):
        return "financial_document"
    elif any(term in lower_name for term in ["policy", "procedure", "guideline"]):
        return "policy_document"
    elif any(term in lower_name for term in ["report", "summary", "analysis"]):
        return "report"
    elif any(term in lower_name for term in ["plan", "strategy", "proposal"]):
        return "plan_document"
    
    # Check content patterns
    lower_text = text.lower()
    
    if "budget" in lower_text and any(term in lower_text for term in ["allocation", "expense", "spending", "cost"]):
        return "financial_document"
    elif any(term in lower_text for term in ["policy", "rule", "guideline", "must", "shall", "required"]):
        return "policy_document"
    elif any(term in lower_text for term in ["quarterly report", "annual report", "financial report"]):
        return "report"
    elif any(term in lower_text for term in ["strategic plan", "proposal", "initiative"]):
        return "plan_document"
    
    return None


def extract_dates(text: str) -> List[str]:
    """
    Extract dates mentioned in text.
    
    Args:
        text: The text to extract dates from
        
    Returns:
        List of date strings found
    """
    # Simple regex patterns for common date formats
    date_patterns = [
        # yyyy-mm-dd
        r'\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b',
        # mm/dd/yyyy 
        r'\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(20\d{2})\b',
        # Month dd, yyyy
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(20\d{2})\b',
        # Fiscal years
        r'\bFY\s*(20\d{2})\b',
        r'\bQ[1-4]\s*(20\d{2})\b',
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Convert tuple matches to strings
            for match in matches:
                if isinstance(match, tuple):
                    # Join components for tuple matches
                    date_str = "".join(match)
                else:
                    date_str = match
                    
                if date_str not in dates:
                    dates.append(date_str)
    
    return dates
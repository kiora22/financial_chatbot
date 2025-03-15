"""
CSV file processor.
Handles .csv files using pandas.
"""

import os
from typing import Dict, Any, Optional
import pandas as pd

from document_processor.processors.base_processor import BaseDocumentProcessor
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("csv_processor")


class CSVProcessor(BaseDocumentProcessor):
    """Processor for CSV files."""
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Extracting text from CSV file: {file_path}")
            
            # Read the CSV file
            df = pd.read_csv(file_path, na_filter=False)
            
            # Skip empty dataframes
            if df.empty:
                logger.warning(f"CSV file {file_path} is empty")
                return ""
            
            # Convert to string representation
            text = ""
            
            # Get column names
            columns_text = "Columns: " + ", ".join(str(col) for col in df.columns) + "\n\n"
            text += columns_text
            
            # Convert dataframe to string representation
            data_text = df.to_string(index=False)
            text += data_text
            
            logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
            return text
            
        except UnicodeDecodeError:
            # Try again with different encoding
            logger.warning(f"UTF-8 decoding failed for {file_path}, trying with latin-1")
            df = pd.read_csv(file_path, encoding='latin-1', na_filter=False)
            
            # Skip empty dataframes
            if df.empty:
                return ""
            
            # Convert to string representation as above
            text = "Columns: " + ", ".join(str(col) for col in df.columns) + "\n\n"
            text += df.to_string(index=False)
            
            logger.info(f"Successfully extracted {len(text)} characters from {file_path} using latin-1")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from CSV {file_path}: {str(e)}")
            return ""
    
    async def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
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
                "file_extension": "csv"
            }
            
            # Extract CSV-specific metadata
            try:
                # Try with default UTF-8 encoding
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                # Try with latin-1 encoding
                df = pd.read_csv(file_path, encoding='latin-1')
            
            # Add row and column counts
            metadata["row_count"] = len(df)
            metadata["column_count"] = len(df.columns)
            metadata["column_names"] = list(df.columns)
            
            # Check if file seems to have a header
            has_header = True
            for col in df.columns:
                # If any column name is a default numeric index, it probably doesn't have a header
                if str(col).isdigit() or str(col) == "Unnamed":
                    has_header = False
                    break
            
            metadata["has_header"] = has_header
            
            # Get data types
            metadata["data_types"] = {col: str(df[col].dtype) for col in df.columns}
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from CSV {file_path}: {str(e)}")
            return None
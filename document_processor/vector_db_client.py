"""
Vector database client for document processor.
This file provides a ChromaDB client for the document processor service.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from chromadb import HttpClient, Settings
from chromadb.utils import embedding_functions

from config.settings import settings
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("vector_db_client")

import requests
import socket

# Test HTTP connectivity
def test_http_connection():
    url = "http://vector_db:8000"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("HTTP connection successful!")
        else:
            logger.info(f"Failed to connect. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.info(f"Error connecting to {url}: {e}")

# Test TCP connectivity
def test_tcp_connection():
    host = "vector_db"
    port = 8000
    try:
        with socket.create_connection((host, port), timeout=5):
            logger.info(f"TCP connection successful to {host}:{port}")
    except socket.error as e:
        logger.info(f"Error connecting to {host}:{port} - {e}")


class VectorDBClient:
    """ChromaDB client for document processor."""
    
    def __init__(self):
        """Initialize the ChromaDB client."""
        self.chromadb_url = settings.chromadb_url
        self.openai_api_key = settings.openai_api_key
        self.collection_name = "financial_documents"
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.max_retry_attempts = 5
        self.retry_delay = 5  # seconds
        
        # Initialize with retry logic
        self._initialize_with_retry()
        
    def _initialize_with_retry(self):
        """Initialize ChromaDB client with retry logic."""
        time.sleep(10)
        # Run the tests
        test_http_connection()
        test_tcp_connection()
        self.chromadb_url = 'http://vector_db:8000'
        logger.info(f"Initializing ChromaDB client with URL: {self.chromadb_url}")
        
        # Configure the OpenAI embedding function
        try:
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.openai_api_key,
                model_name="text-embedding-ada-002"
            )
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI embedding function: {str(e)}")
            logger.warning("Using default embedding function instead")
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Connect to ChromaDB with retry logic
        retry_count = 0
        while retry_count < self.max_retry_attempts:
            try:
                # Connect to ChromaDB
                self.client = HttpClient(
                    host="vector_db",
                    port = 8000,
                    settings = Settings(
                    chroma_server_host= 'vector_db', #settings.chromadb_host,
                    chroma_server_http_port= 8000, #settings.chromadb_port
                    is_persistent = True
                ))
                
                # Get or create collection
                try:
                    self.collection = self.client.get_collection(
                        name=self.collection_name,
                        embedding_function=self.embedding_function
                    )
                    logger.info(f"Connected to existing collection: {self.collection_name}")
                except Exception:
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        embedding_function=self.embedding_function
                    )
                    logger.info(f"Created new collection: {self.collection_name}")
                
                logger.info("ChromaDB client successfully initialized")

                logger.info("Deleting all records in collection")
                existing_ids = self.collection.get()['ids']
                self.collection.delete(ids = existing_ids)

                break
            
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count}/{self.max_retry_attempts} to connect to ChromaDB failed: {str(e)}")
                
                if retry_count < self.max_retry_attempts:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to connect to ChromaDB after {self.max_retry_attempts} attempts")
                    logger.error("Vector database functionality will be unavailable")
    
    async def add_document(
        self,
        document_id: str,
        text: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Add a document to the vector database.
        
        Args:
            document_id: Unique identifier for the document
            text: The text content to embed
            metadata: Additional metadata for the document
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Adding document to vector store: {document_id}")

            # Check if collection exists
            if self.collection is None:
                logger.error("ChromaDB collection is not initialized")
                return False

            # Check if document ID already exists in the collection
            existing_ids = self.collection.get()['ids']
            existing_ids = [x.split("_")[0] for x in existing_ids]

            logger.info(f"Existing IDs: {existing_ids}")
            
            if document_id.split('_')[0] in existing_ids:
                logger.info(f"Document with ID {document_id} already exists in the vector store. Skipping addition.")
                return False

            # Add document to ChromaDB
            self.collection.add(
                ids=[document_id],
                documents=[text],
                metadatas=None  # str(metadata)
            )

            logger.info(f"Successfully added document: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return False


# Create a singleton instance
vector_db_client = VectorDBClient()
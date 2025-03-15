from typing import List, Dict, Any, Optional
import os
import time
import logging
from chromadb import HttpClient, Settings, Collection
from chromadb.utils import embedding_functions
import numpy as np

from config.settings import settings
from config.logging_config import setup_logging

# Set up logging
logger = setup_logging("rag_retrieval")


class RAGRetrieval:
    """Class for retrieving relevant context from the vector database."""
    
    def __init__(self):
        """Initialize the RAG retrieval system."""
        self.chromadb_url = settings.chromadb_url
        self.openai_api_key = settings.openai_api_key
        self.collection_name = "financial_documents"
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.max_retry_attempts = 5
        self.retry_delay = 5  # seconds
        
        # Initialize with retry logic
        time.sleep(20)
        self._initialize_with_retry()
        
    def _initialize_with_retry(self):
        """Initialize ChromaDB client with retry logic."""
        self.chromadb_url = 'http://vector_db:8000'
        logger.info(f"Initializing RAG retrieval with ChromaDB URL: {self.chromadb_url}")
        #logger.info(f"Available collections: {self.client.list_collections()}")

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
                #try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Connected to existing collection: {self.collection_name}")
                #except Exception:
                    #self.collection = self.client.create_collection(
                    #    name=self.collection_name,
                    #    embedding_function=self.embedding_function
                    #)
                    #logger.info(f"Created new collection: {self.collection_name}")
                
                logger.info("RAG retrieval system successfully initialized")
                break
            
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count}/{self.max_retry_attempts} to connect to ChromaDB failed: {str(e)}")
                
                if retry_count < self.max_retry_attempts:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to connect to ChromaDB after {self.max_retry_attempts} attempts")
                    logger.error("RAG retrieval will be unavailable")
    
    async def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector database.
        
        Args:
            query: The query to search for
            top_k: The number of results to retrieve
            threshold: The similarity threshold for results
            
        Returns:
            A list of context documents
        """
        try:
            logger.info(f"Retrieving context for query: {query}, top_k: {top_k}, threshold: {threshold}")
            
            # Check if collection exists
            if self.collection is None:
                logger.warning("ChromaDB collection is not initialized, using fallback mock data")
                return self._get_mock_context()
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Process results
            documents = []
            logger.info(f"Results: {results}")
            if results and 'documents' in results and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    # Skip results below threshold
                    if 'distances' in results and results['distances'][0][i] > threshold:
                        continue
                    
                    # Get metadata
                    metadata = {}
                    if 'metadatas' in results and results['metadatas'][0][i]:
                        metadata = results['metadatas'][0][i]
                    
                    # Calculate score (convert distance to similarity score)
                    score = 1.0
                    if 'distances' in results:
                        # Convert distance to similarity (assuming cosine distance)
                        score = 1.0 - min(1.0, results['distances'][0][i])
                    
                    documents.append({
                        "content": doc,
                        "source": metadata.get("source", "unknown"),
                        "score": score
                    })
            
            # If no results found, return mock data
            if not documents:
                logger.warning("No results found in ChromaDB, using fallback mock data")
                return self._get_mock_context()
            
            logger.info(f"Retrieved {len(documents)} context documents")
            return documents
        
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            logger.warning("Using fallback mock data")
            return self._get_mock_context()
    
    def _get_mock_context(self) -> List[Dict[str, Any]]:
        """Return mock context data for testing or fallback."""
        mock_context = [
            {
                "content": "The marketing budget for Q1 2025 is $30,000, with $10,000 allocated to social media advertising, $5,000 to content production, and $15,000 to events.",
                "source": "Marketing_Plan_2025.pdf",
                "score": 0.92
            },
            {
                "content": "Social media advertising spend is typically increased by 20% during holiday seasons (November-December) to capture increased consumer attention.",
                "source": "Marketing_Strategy.docx",
                "score": 0.85
            },
            {
                "content": "Budget modifications require approval when they exceed 15% of the original allocation. Justification must include expected ROI and impact analysis.",
                "source": "Budget_Policies.pdf",
                "score": 0.78
            }
        ]
        return mock_context
    
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
            
            # Add document to ChromaDB
            self.collection.add(
                ids=[document_id],
                documents=[text],
                metadatas=[metadata]
            )
            
            logger.info(f"Successfully added document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return False
    
    async def test_embedding(self) -> Dict[str, Any]:
        """
        Test the embedding function and vector database connection.
        
        Returns:
            Test results including status and diagnostic information
        """
        results = {
            "status": "unknown",
            "details": {},
            "error": None
        }
        
        try:
            # Test embedding function
            if self.embedding_function:
                test_text = "This is a test document for embedding."
                embedding = self.embedding_function([test_text])
                results["details"]["embedding_dims"] = len(embedding[0])
                results["details"]["embedding_function"] = str(type(self.embedding_function))
            else:
                results["error"] = "Embedding function not initialized"
                results["status"] = "failed"
                return results
            
            # Test ChromaDB connection
            if self.client and self.collection:
                # Add a test document
                test_id = f"test_{int(time.time())}"
                self.collection.add(
                    ids=[test_id],
                    documents=["This is a test document for the financial assistant RAG system."],
                    metadatas=[{"source": "test", "test": True}]
                )
                
                # Query the test document
                results["details"]["collection_name"] = self.collection.name
                collection_count = self.collection.count()
                results["details"]["document_count"] = collection_count
                
                # Query to verify retrieval
                query_results = self.collection.query(
                    query_texts=["test document financial"],
                    n_results=1
                )
                
                # Delete the test document
                self.collection.delete(ids=[test_id])
                
                # Check query results
                if query_results and len(query_results["documents"]) > 0:
                    results["status"] = "success"
                    results["details"]["retrieval_test"] = "passed"
                else:
                    results["status"] = "partial"
                    results["details"]["retrieval_test"] = "failed"
            else:
                results["error"] = "ChromaDB client or collection not initialized"
                results["status"] = "failed"
                return results
                
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            logger.error(f"Error in embedding test: {str(e)}")
        
        return results


# Create a singleton instance
rag_retrieval = RAGRetrieval()
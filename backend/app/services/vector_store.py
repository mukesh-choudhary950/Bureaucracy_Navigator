"""Vector Database Service using ChromaDB"""

import os
import uuid
from typing import List, Dict, Any, Optional
from chromadb import Client, PersistentClient
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing document embeddings and similarity search"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            # Initialize persistent client
            self.client = PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Use HuggingFace embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Get or create collection (without embedding function for custom embeddings)
            self.collection = self.client.get_or_create_collection(
                name="government_documents",
                metadata={"description": "Government procedure documents"}
            )
            
            logger.info("Vector store initialized successfully with HuggingFace embeddings")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise
    
    def add_document_chunks(
        self, 
        chunks: List[str], 
        metadata: List[Dict[str, Any]],
        document_id: Optional[str] = None
    ) -> str:
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of text chunks
            metadata: List of metadata dictionaries for each chunk
            document_id: Optional document ID
            
        Returns:
            Document ID
        """
        try:
            if document_id is None:
                document_id = str(uuid.uuid4())
            
            # Generate IDs for each chunk
            chunk_ids = [f"{document_id}_{i}" for i in range(len(chunks))]
            
            # Add document_id to metadata for each chunk
            for i, meta in enumerate(metadata):
                meta["document_id"] = document_id
                meta["chunk_index"] = i
            
            # Generate embeddings using HuggingFace
            embeddings = self.embeddings.embed_documents(chunks)
            
            # Add to collection with embeddings
            self.collection.add(
                documents=chunks,
                metadatas=metadata,
                ids=chunk_ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to add document chunks: {str(e)}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        n_results: int = 5,
        document_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            document_id: Optional specific document ID to search within
            filters: Optional metadata filters
            
        Returns:
            List of search results with metadata
        """
        try:
            # Build where clause for filtering
            where_clause = {}
            if document_id:
                where_clause["document_id"] = document_id
            if filters:
                where_clause.update(filters)
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Perform search with embeddings
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0,
                        "id": results['ids'][0][i] if results['ids'] and results['ids'][0] else ""
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
        """
        try:
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            chunks = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    chunks.append({
                        "content": doc,
                        "metadata": results['metadatas'][i] if results['metadatas'] else {},
                        "id": results['ids'][i] if results['ids'] else ""
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {str(e)}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            Success status
        """
        try:
            # Get all chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted document {document_id} with {len(results['ids'])} chunks")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "persist_directory": settings.CHROMA_PERSIST_DIRECTORY
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}

# Global instance
vector_store = VectorStoreService()

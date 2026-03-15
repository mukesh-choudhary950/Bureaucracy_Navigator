"""Simple RAG Agent for question answering"""

from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from app.services.vector_store import vector_store
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SimpleRAGAgent:
    """Simple RAG agent for answering questions based on documents"""
    
    def __init__(self):
        """Initialize the RAG agent"""
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama3-8b-8192",
            temperature=0.3
        )
        self.vector_store = vector_store
        logger.info("Simple RAG agent initialized with Groq API and HuggingFace embeddings")
    
    async def answer_question(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Answer a question using RAG approach
        
        Args:
            question: User's question
            max_results: Maximum number of documents to retrieve
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Retrieve relevant documents
            relevant_docs = vector_store.similarity_search(
                query=question,
                n_results=max_results
            )
            
            if not relevant_docs:
                return {
                    "answer": "I couldn't find any relevant information in the uploaded documents to answer your question. Please try rephrasing your question or upload more relevant documents.",
                    "sources": [],
                    "confidence": 0.0,
                    "metadata": {"no_results": True}
                }
            
            # Generate answer
            answer = await self._generate_answer_with_context(question, relevant_docs)
            
            # Calculate confidence based on document relevance
            confidence = self._calculate_confidence(relevant_docs)
            
            # Extract sources
            sources = self._format_sources(relevant_docs)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "metadata": {
                    "documents_used": len(relevant_docs),
                    "model": "gpt-3.5-turbo"
                }
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _generate_answer_with_context(self, question: str, documents: List[Dict[str, Any]]) -> str:
        """Generate answer using Groq with document context"""
        try:
            # Format context
            context_text = self._format_documents_for_context(documents)
            
            system_prompt = """You are a helpful AI assistant specializing in government procedures and bureaucracy. 
            Your role is to answer questions based ONLY on the provided document excerpts. 
            Follow these guidelines:
            
            1. Use only information from the provided context
            2. If the context doesn't contain enough information, say so clearly
            3. Provide clear, step-by-step guidance for procedures
            4. Be helpful, professional, and concise
            5. Cite sources when possible by mentioning document names
            
            Context:
            {context}"""
            
            user_prompt = f"Question: {question}\n\nBased on the provided documents, please provide a comprehensive answer."
            
            # Use LangChain Groq integration
            from langchain.schema import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content=system_prompt.format(context=context_text)),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I encountered an error while generating an answer. Please try again."
    
    def _format_documents_for_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format documents for context in the prompt"""
        if not documents:
            return "No documents available."
        
        context = "Relevant Document Excerpts:\n\n"
        
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            filename = metadata.get("filename", f"Document {i}")
            chunk_index = metadata.get("chunk_index", 0)
            
            context += f"Document {i}: {filename} (Section {chunk_index + 1})\n"
            context += doc["content"] + "\n\n"
        
        return context
    
    def _calculate_confidence(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on document relevance"""
        if not documents:
            return 0.0
        
        # Use average relevance score (inverse of distance)
        total_relevance = sum(1 - doc.get("distance", 1.0) for doc in documents)
        confidence = total_relevance / len(documents)
        
        # Scale to 0-1 range
        return max(0.0, min(1.0, confidence))
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            source = {
                "filename": metadata.get("filename", "Unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "relevance_score": 1 - doc.get("distance", 0),
                "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            }
            sources.append(source)
        
        return sources

# Global instance
simple_rag_agent = SimpleRAGAgent()

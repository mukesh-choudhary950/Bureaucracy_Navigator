from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.vector_store import vector_store
import json
import os
from datetime import datetime

class RAGSystem:
    """Retrieval Augmented Generation system for knowledge base"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama3-8b-8192",
            temperature=0.3
        )
        self.vector_store = vector_store
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with demo government procedure data"""
        # Check if vector store already has data
        try:
            stats = self.vector_store.get_collection_stats()
            if stats.get("total_chunks", 0) > 0:
                return  # Already initialized
        except:
            pass
        
        # Demo documents for common procedures
        demo_documents = [
            {
                "id": "income_cert_telangana",
                "content": """
                Income Certificate Telangana - Complete Procedure:
                
                Required Documents:
                1. Aadhaar Card
                2. Ration Card or Voter ID
                3. Income Proof (Salary Certificate/Form 16/IT Returns)
                4. Address Proof
                5. Passport Size Photographs (2)
                6. Self-Declaration Form
                
                Application Process:
                1. Visit nearest MeeSeva center
                2. Fill application form
                3. Attach self-attested documents
                4. Pay fee of ₹35
                5. Submit application
                
                Timeline: 7 working days
                Authority: Tahsildar/Mandal Revenue Officer
                Validity: 1 year
                
                Online Application:
                - Visit meeseva.telangana.gov.in
                - Register and login
                - Fill online form
                - Upload scanned documents
                - Pay online fee
                - Download acknowledgment
                
                Important Notes:
                - Income certificate is required for educational scholarships
                - Can be used for government welfare schemes
                - Must be renewed annually
                """,
                "metadata": {
                    "procedure": "income_certificate",
                    "state": "telangana",
                    "category": "certificate",
                    "authority": "revenue_department"
                }
            },
            {
                "id": "driving_license_telangana",
                "content": """
                Driving License Telangana - Complete Procedure:
                
                Learner's License:
                Required Documents:
                1. Aadhaar Card
                2. Proof of Address
                3. Proof of Date of Birth
                4. Passport Size Photographs (3)
                
                Process:
                1. Fill application form (online or offline)
                2. Submit documents at RTO
                3. Pass written test
                4. Receive learner's license (valid 6 months)
                
                Permanent License:
                Required Documents:
                1. Learner's License
                2. Original documents submitted for LL
                3. Vehicle registration certificate (if applicable)
                
                Process:
                1. Apply after 30 days of LL
                2. Book driving test slot
                3. Pass driving test
                4. Pay license fee
                5. Receive permanent license
                
                Fees:
                - Learner's License: ₹200
                - Permanent License: ₹300
                - Driving Test: ₹50
                
                Timeline:
                - LL: Same day
                - Permanent: After test clearance
                
                RTO Offices in Hyderabad:
                - Khairatabad RTO
                - Abids RTO
                - Secunderabad RTO
                
                Online Application:
                - Visit transport.telangana.gov.in
                - Create account
                - Fill application
                - Upload documents
                - Pay fee online
                - Book test slot
                
                Important Notes:
                - Minimum age: 18 years for private vehicles
                - Must carry original documents during test
                - International Driving Permit available for foreign countries
                """,
                "metadata": {
                    "procedure": "driving_license",
                    "state": "telangana",
                    "category": "license",
                    "authority": "transport_department"
                }
            },
            {
                "id": "caste_certificate_telangana",
                "content": """
                Caste Certificate Telangana - Complete Procedure:
                
                Required Documents:
                1. Aadhaar Card
                2. Voter ID/Ration Card
                3. Birth Certificate
                4. Parents' Caste Certificate
                5. Address Proof
                6. Passport Size Photographs (2)
                7. Self-Declaration Form
                
                Application Process:
                1. Obtain application form from MRO office
                2. Fill in complete details
                3. Attach all required documents
                4. Submit to Mandal Revenue Officer
                5. Pay prescribed fee
                
                Verification Process:
                1. Document verification at MRO office
                2. Field inquiry by revenue inspector
                3. Verification from village records
                4. Approval by MRO
                
                Timeline: 15-30 working days
                Fee: ₹10-50 (varies by district)
                Validity: Lifetime
                
                Online Application:
                - Visit meeseva.telangana.gov.in
                - Register with Aadhaar
                - Fill caste certificate form
                - Upload documents
                - Pay fee online
                - Track application status
                
                Important Notes:
                - Required for educational reservations
                - Needed for government job reservations
                - Must have parents' caste certificate
                - Field verification mandatory
                
                Caste Categories:
                - SC (Scheduled Castes)
                - ST (Scheduled Tribes)
                - BC (Backward Classes) - A, B, C, D
                - OC (Other Castes) - Not eligible for certificate
                
                Contact:
                - Mandal Revenue Office (MRO)
                - District Revenue Office
                """,
                "metadata": {
                    "procedure": "caste_certificate",
                    "state": "telangana",
                    "category": "certificate",
                    "authority": "revenue_department"
                }
            },
            {
                "id": "birth_certificate_telangana",
                "content": """
                Birth Certificate Telangana - Complete Procedure:
                
                Registration Timeline:
                - Within 21 days: Free
                - 21-30 days: ₹2 late fee
                - 30 days-1 year: ₹5 late fee
                - After 1 year: Court order required
                
                Required Documents:
                1. Hospital Discharge Certificate
                2. Parents' Marriage Certificate
                3. Parents' Aadhaar Cards
                4. Address Proof
                5. Birth Registration Form (from hospital)
                
                Application Process:
                1. Obtain birth registration form
                2. Fill in complete details
                3. Attach required documents
                4. Submit to municipal corporation/panchayat
                5. Pay applicable fee
                
                Registration Authorities:
                - Municipal Corporation: Urban areas
                - Municipality: Semi-urban areas
                - Gram Panchayat: Rural areas
                
                Online Registration:
                - Visit crsorgi.gov.in
                - Create account
                - Fill birth registration form
                - Upload documents
                - Pay fee online
                - Download certificate
                
                Important Notes:
                - Name can be added/changed within 1 year
                - Birth certificate mandatory for school admission
                - Required for passport application
                - Needed for government benefits
                
                Fee Structure:
                - Normal registration: Free
                - Late registration: ₹2-₹100
                - Court order case: Additional court fees
                
                Timeline:
                - Normal: 7-10 days
                - Late registration: 15-30 days
                - Court order: As per court process
                
                Documents for Late Registration:
                - Affidavit from parents
                - School certificate (if applicable)
                - Age proof documents
                - Court order (if >1 year)
                """,
                "metadata": {
                    "procedure": "birth_certificate",
                    "state": "telangana",
                    "category": "certificate",
                    "authority": "municipal_administration"
                }
            }
        ]
        
        # Add documents to collection
        for doc in demo_documents:
            try:
                # Add to vector store
                self.vector_store.add_document_chunks(
                    chunks=[doc["content"]],
                    metadata=[doc["metadata"]],
                    document_id=doc["id"]
                )
            except Exception as e:
                print(f"Error adding document {doc['id']}: {e}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using HuggingFace"""
        try:
            # Use vector store embeddings
            return self.vector_store.embeddings.embed_query(text)
        except Exception as e:
            # Fallback to dummy embedding
            return [0.0] * 384  # MiniLM-L6-v2 has 384 dimensions
    
    async def search_knowledge(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        try:
            # Use vector store for similarity search
            results = self.vector_store.similarity_search(
                query=query,
                n_results=n_results
            )
            
            # Format results to match expected structure
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "distance": result.get("distance", 0),
                    "id": result.get("id", "")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
    
    async def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add new document to knowledge base"""
        try:
            # Use vector store to add document
            doc_id = self.vector_store.add_document_chunks(
                chunks=[content],
                metadata=[metadata]
            )
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    async def get_relevant_context(self, query: str) -> str:
        """Get relevant context for a query"""
        search_results = await self.search_knowledge(query)
        
        if not search_results:
            return "No relevant information found in knowledge base."
        
        # Combine search results into context
        context_parts = []
        for result in search_results:
            context_parts.append(f"Relevant Information:\n{result['content']}")
        
        return "\n\n".join(context_parts)
    
    async def answer_question(self, query: str) -> Dict[str, Any]:
        """Answer a question using RAG"""
        # Get relevant context
        context = await self.get_relevant_context(query)
        
        if "No relevant information found" in context:
            return {
                "answer": "I don't have specific information about this procedure in my knowledge base. Let me search for current information.",
                "sources": [],
                "confidence": "low"
            }
        
        # Generate answer using context
        system_prompt = """You are a helpful assistant for government procedures in India. Use the provided context to answer the user's question. Be specific, accurate, and provide practical guidance."""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context. Include specific steps, documents required, and timeline if available."""
        
        try:
            # Use LangChain Groq integration
            from langchain.schema import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            return {
                "answer": answer,
                "sources": [result["id"] for result in search_results],
                "confidence": "high"
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": "low"
            }

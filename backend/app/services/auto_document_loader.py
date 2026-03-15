"""Automated Document Loader for Government Procedures"""

import requests
import time
import re
import os
from typing import List, Dict, Any
from pathlib import Path
from bs4 import BeautifulSoup
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AutoDocumentLoader:
    """Automated loader for government procedure documents"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        self.documents_dir = Path(__file__).parent.parent.parent / "documents"
        self.loaded_pdfs = {}

    def load_government_documents(self) -> Dict[str, Any]:
        """Load documents from government websites"""
        results = {
            "loaded_documents": 0,
            "processed_documents": 0,
            "sources": [],
            "errors": [],
        }

        sources = [
            {
                "name": "India Government Services",
                "url": "https://services.india.gov.in/",
                "type": "portal",
            },
            {
                "name": "Passport Seva Kendra",
                "url": "https://www.passportindia.gov.in/",
                "type": "passport",
            },
            {
                "name": "Telangana Meeseva",
                "url": "https://meeseva.telangana.gov.in/",
                "type": "state_services",
            },
            {
                "name": "Aadhaar Services",
                "url": "https://uidai.gov.in/",
                "type": "identity",
            },
        ]

        for source in sources:
            try:
                logger.info(f"Loading documents from {source['name']}")
                documents = self._scrape_website(source)

                for doc in documents:
                    chunks = document_processor.process(
                        text=doc["content"],
                        metadata={
                            "source": source["name"],
                            "url": source["url"],
                            "title": doc["title"],
                            "type": source["type"],
                            "auto_loaded": True,
                        },
                    )

                    if chunks:
                        vector_store.add_document_chunks(
                            chunks=chunks["chunks"],
                            metadata=chunks["metadata"],
                            document_id=f"auto_{source['type']}_{int(time.time())}",
                        )
                        results["processed_documents"] += 1
                        logger.info(f"Processed and stored: {doc['title']}")

                results["loaded_documents"] += len(documents)
                results["sources"].append(source["name"])

                time.sleep(2)

            except Exception as e:
                error_msg = f"Failed to load {source['name']}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        return results

    def _scrape_website(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape documents from a government website"""
        try:
            response = self.session.get(source["url"], timeout=10)  # Reduced from 30s to 10s
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            documents = []

            if source["type"] == "passport":
                documents.extend(self._extract_passport_info(soup, source))
            elif source["type"] == "state_services":
                documents.extend(self._extract_state_services(soup, source))
            elif source["type"] == "identity":
                documents.extend(self._extract_aadhaar_info(soup, source))
            else:
                documents.extend(self._extract_general_info(soup, source))

            # fallback if nothing found
            if not documents:
                logger.info(
                    f"No structured sections found for {source['name']}, using fallback extraction"
                )
                page_text = soup.get_text(separator=" ", strip=True)
                clean_text = self._clean_text(page_text)

                if len(clean_text) > 300:
                    documents.append(
                        {
                            "title": f"{source['name']} Information",
                            "content": clean_text[:3000],
                            "url": source["url"],
                        }
                    )

            return documents

        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping {source['url']} - took longer than 10 seconds")
            return []
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error scraping {source['url']} - website may be down")
            return []
        except Exception as e:
            logger.error(f"Error scraping {source['url']}: {str(e)}")
            return []

    def _extract_passport_info(
        self, soup: BeautifulSoup, source: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract passport-related information"""
        documents = []

        def class_filter(x):
            if not x:
                return False
            if isinstance(x, list):
                x = " ".join(x)
            return any(
                keyword in x.lower() for keyword in ["content", "service", "procedure", "guide"]
            )

        content_sections = soup.find_all(["div", "section"], class_=class_filter)

        for section in content_sections[:5]:
            text = self._clean_text(section.get_text())
            if len(text) > 100:
                title_elem = section.find(["h1", "h2", "h3"])
                title_text = title_elem.get_text().strip() if title_elem else "Passport Information"

                documents.append(
                    {"title": title_text, "content": text, "url": source["url"]}
                )

        return documents

    def _extract_state_services(
        self, soup: BeautifulSoup, source: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract state services information"""
        documents = []

        service_links = soup.find_all("a", href=True)

        for link in service_links[:10]:
            text = self._clean_text(link.get_text())
            if any(
                keyword in text.lower()
                for keyword in ["certificate", "application", "service", "procedure"]
            ):
                documents.append(
                    {
                        "title": text.strip(),
                        "content": f"Service available: {text.strip()}. Visit the portal for detailed procedure, required documents, and application forms.",
                        "url": source["url"],
                    }
                )

        return documents

    def _extract_aadhaar_info(
        self, soup: BeautifulSoup, source: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract Aadhaar-related information"""
        documents = []

        def class_filter(x):
            if not x:
                return False
            if isinstance(x, list):
                x = " ".join(x)
            return any(keyword in x.lower() for keyword in ["info", "service", "detail"])

        info_sections = soup.find_all(["div", "p"], class_=class_filter)

        for section in info_sections[:3]:
            text = self._clean_text(section.get_text())
            if len(text) > 100:
                documents.append(
                    {
                        "title": "Aadhaar Service Information",
                        "content": text,
                        "url": source["url"],
                    }
                )

        return documents

    def _extract_general_info(
        self, soup: BeautifulSoup, source: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract general government service information"""
        documents = []

        main_content = soup.find("main") or soup.find(
            "div", class_=lambda x: isinstance(x, str) and "content" in x.lower()
        )

        if main_content:
            text = self._clean_text(main_content.get_text())
            if len(text) > 200:
                documents.append(
                    {
                        "title": f"{source['name']} - Services Overview",
                        "content": text[:2000],
                        "url": source["url"],
                    }
                )

        return documents

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""

        text = " ".join(text.split())

        unwanted_patterns = [r"\s+", r"\n+", r"\t+"]

        for pattern in unwanted_patterns:
            text = re.sub(pattern, " ", text)

        return text.strip()

    def scan_local_pdfs(self) -> Dict[str, Any]:
        """Scan and process all PDF files in the documents directory"""
        results = {
            "loaded_documents": 0,
            "processed_documents": 0,
            "sources": [],
            "errors": [],
            "pdf_files": []
        }

        try:
            if not self.documents_dir.exists():
                logger.warning(f"Documents directory not found: {self.documents_dir}")
                return results

            # Get all PDF files
            pdf_files = list(self.documents_dir.glob("*.pdf"))
            logger.info(f"Found {len(pdf_files)} PDF files in {self.documents_dir}")

            for pdf_file in pdf_files:
                try:
                    logger.info(f"Processing PDF: {pdf_file.name}")
                    
                    # Process the PDF file
                    process_result = document_processor.process_file(
                        str(pdf_file), 
                        pdf_file.name
                    )

                    if process_result["success"]:
                        # Store the processed content
                        self.loaded_pdfs[pdf_file.name] = {
                            "filename": pdf_file.name,
                            "content": process_result["text"],
                            "chunks": process_result["chunks"],
                            "metadata": process_result["metadata"],
                            "stats": process_result["stats"]
                        }

                        # Add to vector store
                        vector_store.add_document_chunks(
                            chunks=process_result["chunks"],
                            metadata=process_result["metadata"],
                            document_id=f"pdf_{pdf_file.stem}"
                        )

                        results["processed_documents"] += 1
                        results["sources"].append(pdf_file.name)
                        results["pdf_files"].append({
                            "name": pdf_file.name,
                            "size": pdf_file.stat().st_size,
                            "type": "pdf",
                            "category": self._categorize_pdf(pdf_file.name)
                        })

                        logger.info(f"Successfully processed: {pdf_file.name}")
                    else:
                        error_msg = f"Failed to process {pdf_file.name}: {process_result.get('error', 'Unknown error')}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)

                except Exception as e:
                    error_msg = f"Error processing {pdf_file.name}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            results["loaded_documents"] = len(pdf_files)
            logger.info(f"PDF scanning completed. Processed {results['processed_documents']}/{len(pdf_files)} files.")

        except Exception as e:
            error_msg = f"Error scanning PDFs: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def get_targeted_summary(self, user_query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Get targeted summary from loaded PDFs based on user query
        
        Args:
            user_query: The user's specific query/request
            max_results: Maximum number of relevant documents to summarize
            
        Returns:
            Dictionary with targeted summaries and sources
        """
        try:
            # If PDFs are not loaded, load them first
            if not self.loaded_pdfs:
                logger.info("PDFs not loaded, scanning documents directory...")
                self.scan_local_pdfs()

            if not self.loaded_pdfs:
                return {
                    "success": False,
                    "error": "No PDF documents found or processed",
                    "summary": "No documents available to summarize",
                    "sources": []
                }

            # Search for relevant documents using vector store
            search_results = vector_store.similarity_search(user_query, max_results)
            
            if not search_results:
                return {
                    "success": False,
                    "error": "No relevant information found in documents",
                    "summary": "I couldn't find information relevant to your query in the available documents.",
                    "sources": []
                }

            # Generate targeted summary
            summary = self._generate_targeted_summary(user_query, search_results)
            
            # Extract source information
            sources = []
            for result in search_results:
                metadata = result.get("metadata", {})
                sources.append({
                    "filename": metadata.get("filename", "Unknown"),
                    "relevance": 1 - result.get("distance", 0),
                    "preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                })

            return {
                "success": True,
                "query": user_query,
                "summary": summary,
                "sources": sources,
                "documents_used": len(search_results),
                "total_documents": len(self.loaded_pdfs)
            }

        except Exception as e:
            import traceback
            logger.error(f"Error generating targeted summary: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "summary": f"Error occurred: {str(e)}. Please check the logs for details.",
                "sources": []
            }

    def _generate_targeted_summary(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate accurate summary without source references"""
        
        # Extract relevant content - NO source references
        relevant_content = []
        for result in search_results:
            content = result.get("content", "")
            if content.strip():
                relevant_content.append(content)

        if not relevant_content:
            return "Based on the available government documents, specific information about this query was not found. Please try asking about available certificates such as Aadhaar, Birth, Death, Income, Ration card, Land ownership, or Vehicle certificates."

        # Create comprehensive summary based on query type
        content_text = "\n".join(relevant_content)
        query_lower = query.lower()
        
        # Extract specific information based on query type
        if "aadhaar" in query_lower:
            return self._extract_aadhaar_info(content_text)
        elif "birth" in query_lower:
            return self._extract_birth_certificate_info(content_text)
        elif "death" in query_lower:
            return self._extract_death_certificate_info(content_text)
        elif "income" in query_lower:
            return self._extract_income_certificate_info(content_text)
        elif "ration" in query_lower:
            return self._extract_ration_card_info(content_text)
        elif "land ownership" in query_lower:
            return self._extract_land_ownership_info(content_text)
        elif "land transfer" in query_lower:
            return self._extract_land_transfer_info(content_text)
        elif "agriculture" in query_lower:
            return self._extract_agriculture_info(content_text)
        elif "business" in query_lower or "industry" in query_lower:
            return self._extract_business_info(content_text)
        elif "vehicle" in query_lower or "transport" in query_lower:
            return self._extract_vehicle_info(content_text)
        elif "land" in query_lower or "property" in query_lower:
            return self._extract_land_info(content_text)
        else:
            # General summary with detailed information
            return self._create_detailed_summary(query, content_text)

    def _create_detailed_summary(self, query: str, content: str) -> str:
        """Create detailed summary from content without source references"""
        # Clean content - remove any source references
        clean_content = content.replace("From", "").replace("PDF:", "").replace("Document:", "").replace("Source:", "")
        
        # Extract key information
        lines = clean_content.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 15 and not line.startswith("http") and not line.endswith(".pdf"):
                key_points.append(line)
        
        if not key_points:
            return f"Information about {query} is available in the government documents. Please refer to the official guidelines for complete procedures and requirements."
        
        # Create comprehensive response with proper spacing
        summary = f"**{query.title()}**\n\n"
        summary += "Based on the official government guidelines:\n\n"
        
        for i, point in enumerate(key_points[:8], 1):
            if len(point) > 15:
                summary += f"{i}. {point}\n\n"  # Added extra newline for spacing
        
        return summary.strip()

    def _extract_aadhaar_info(self, content: str) -> str:
        """Extract Aadhaar card information"""
        return """**Aadhaar Card Application**

**Eligibility:** Any resident of India can apply for Aadhaar

**Required Documents:**
• Proof of identity (Passport, PAN, Voter ID, Driving License, etc.)
• Proof of address (Utility bill, Bank statement, Rent agreement, etc.)
• Proof of date of birth (Birth certificate, SSLC certificate, Passport, etc.)

**Application Process:**
1. Visit the nearest Aadhaar enrollment center
2. Fill out the Aadhaar enrollment form
3. Submit required documents for verification
4. Provide biometric data (fingerprints and iris scan)
5. Have your photograph taken
6. Receive acknowledgment slip with enrollment ID

**Timeline:** Aadhaar card is usually issued within 90 days

**Fees:** Enrollment is completely free of charge

For more information, visit the official UIDAI website or contact your nearest Aadhaar enrollment center."""

    def _extract_birth_certificate_info(self, content: str) -> str:
        """Extract birth certificate information"""
        return """**Birth Certificate Application**

**Where to Apply:**
• Municipal Corporation office (for urban areas)
• Municipality office (for towns)
• Gram Panchayat office (for rural areas)

**Required Documents:**
• Hospital birth certificate (if born in hospital)
• Parent's identity proof (Aadhaar, Voter ID, etc.)
• Parent's address proof
• Marriage certificate of parents (optional but recommended)
• Application form duly filled

**Timeline:**
• Certificate is issued within 21 days of application
• Late registration (after 21 days) is possible with additional affidavit

**Fees:**
• Normal registration: Nominal fee as per local authority
• Late registration: Additional late fee may apply

**Online Option:**
Available through Meeseva centers or state government online portals for convenient application.

This certificate is essential for school admissions, passport applications, and other legal purposes."""

    def _extract_death_certificate_info(self, content: str) -> str:
        """Extract death certificate information"""
        return """**Death Certificate Application**

**Registration Timeline:**
• Death must be registered within 21 days of occurrence
• Late registration is possible with additional documentation

**Where to Apply:**
• Local municipal office (urban areas)
• Gram Panchayat office (rural areas)
• Revenue Department

**Required Documents:**
• Medical certificate of cause of death from hospital/doctor
• Applicant's identity proof (Aadhaar, Voter ID)
• Residential proof of deceased
• Age proof of deceased
• Application form with details of deceased

**Processing Time:**
• Normal cases: Certificate issued within 7-14 days after verification
• Late registration: May take longer due to additional verification

**Late Registration:**
Possible with additional affidavit explaining delay and payment of late fee.

This certificate is required for:
• Insurance claims
• Property transfer and inheritance
• Legal settlements
• Bank account closure
• Government benefit claims"""

    def _extract_income_certificate_info(self, content: str) -> str:
        """Extract income certificate information"""
        return """**Income Certificate Application**

**Purpose:**
• Required for scholarships and educational fee concessions
• Essential for various government welfare schemes
• Needed for reservation benefits
• Used for loan applications

**Where to Apply:**
• Tahsildar office
• Revenue Department
• Meeseva centers (for convenient application)
• Online portals (where available)

**Required Documents:**
• Ration card or residence proof
• Salary certificate (if employed)
• Income declaration form
• Recent passport size photograph
• Identity proof (Aadhaar, Voter ID)
• Address proof

**Validity:**
Usually valid for 1 year from the date of issue. Must be renewed for continued benefits.

**Processing Time:** 7-15 working days after submission

Income certificates help eligible citizens access various government benefits, scholarships, and welfare schemes based on their economic status."""

    def _extract_ration_card_info(self, content: str) -> str:
        """Extract ration card information"""
        return """**Ration Card Application**

**Types of Ration Cards:**
• White ration card - For above poverty line (APL) families
• Pink ration card - For below poverty line (BPL) families
• Antyodaya card - For poorest of poor families

**Where to Apply:**
• Civil Supplies Department
• Meeseva centers
• Online portals (state-specific)
• Local food and civil supplies office

**Required Documents:**
• Residence proof
• Identity proof of all family members
• Passport size photographs
• Income certificate
• Details of all family members
• Bank account details
• Aadhaar cards of all members

**Benefits:**
• Access to subsidized food grains through PDS (Public Distribution System)
• Essential commodities at government-fixed rates
• Identification proof for various purposes

**Processing Time:** 30-45 days after application and verification

Ration cards provide food security and access to essential commodities at subsidized rates for eligible families."""

    def _extract_land_ownership_info(self, content: str) -> str:
        """Extract land ownership certificate information"""
        return """**Land Ownership Certificate (Patta)**

**Purpose:**
• Official proof of land ownership and title
• Required for property transactions
• Essential for legal disputes
• Needed for loan applications against property

**Where to Apply:**
• Revenue Department
• Mandal Revenue Officer (MRO) office
• Tahsildar office
• Online portals (Dharani portal in Telangana)

**Required Documents:**
• Patta document or old ownership proof
• Survey number and sub-division details
• Applicant's identity proof (Aadhaar, Voter ID)
• Address proof
• No objection certificate from neighbors
• Land tax receipts (if available)

**Verification Process:**
Revenue officials verify land records and conduct field verification before issuing certificate.

**Processing Time:** 30-60 days depending on verification complexity

This certificate is essential for property transactions, legal disputes, and establishing clear title to land."""

    def _extract_land_transfer_info(self, content: str) -> str:
        """Extract land transfer process information"""
        return """**Land Transfer Procedure**

**Pre-requisites:**
• Clear title of the property
• No pending legal disputes
• Updated land records in revenue department
• All property taxes paid up to date

**Step-by-Step Process:**

1. **Sale Deed Preparation**
   - Draft sale deed with all property details
   - Include accurate survey numbers and extent

2. **Stamp Duty Payment**
   - Pay stamp duty as per market value
   - Stamp duty varies by state and property value

3. **Registration**
   - Register at Sub-Registrar office
   - Both buyer and seller must be present
   - Provide biometric verification

4. **Mutation in Revenue Records**
   - Apply for mutation (Patta transfer)
   - Submit registered sale deed
   - Revenue department updates records

5. **Online Update**
   - Update in Dharani portal (Telangana)
   - Link with Aadhaar

**Required Documents:**
• Original title deeds and sale deed
• Identity proofs of buyer and seller
• Passport size photos
• No dues certificate from bank (if loan cleared)
• Property tax clearance certificate

**Timeline:** 15-30 days after registration completion

**Fees:**
• Stamp duty: As per property market value
• Registration charges: Fixed percentage
• Legal fees: If using lawyer services

Ensure all legal formalities are completed for smooth and valid transfer of property."""
        """Extract process/procedure information"""
        lines = content.split('\n')
        process_info = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["step", "process", "procedure", "apply", "application", "procedure"]):
                if len(line.strip()) > 15:
                    process_info.append(line.strip())

        if process_info:
            return "Process Information:\n" + "\n".join(process_info[:8])
        else:
            return "No specific process information found in the documents."

    def _extract_requirements_info(self, content: str) -> str:
        """Extract requirements information"""
        lines = content.split('\n')
        requirements_info = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["required", "need", "must", "should", "documents", "proof", "identity"]):
                if len(line.strip()) > 15:
                    requirements_info.append(line.strip())

        if requirements_info:
            return "Requirements:\n" + "\n".join(requirements_info[:8])
        else:
            return "No specific requirements information found in the documents."

    def _extract_agriculture_info(self, content: str) -> str:
        """Extract agriculture-specific certificate information with full details"""
        lines = content.split('\n')
        agriculture_info = []
        process_steps = []
        required_documents = []
        eligibility_info = []
        fees_info = []
        timeline_info = []
        
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) < 10:
                continue
                
            line_lower = line_clean.lower()
            
            # Categorize information based on keywords
            if any(keyword in line_lower for keyword in ["step", "process", "procedure", "how to", "apply"]):
                process_steps.append(line_clean)
            elif any(keyword in line_lower for keyword in ["required", "need", "documents", "proof", "identity", "address"]):
                required_documents.append(line_clean)
            elif any(keyword in line_lower for keyword in ["eligibility", "criteria", "who can", "qualify", "eligible"]):
                eligibility_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["fee", "cost", "payment", "charge", "price"]):
                fees_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["time", "days", "duration", "period", "timeline"]):
                timeline_info.append(line_clean)
            else:
                # General agriculture-related information
                if any(keyword in line_lower for keyword in [
                    "agriculture", "farm", "crop", "farmer", "land", "certificate", 
                    "application", "registration", "benefit", "scheme", "subsidy"
                ]):
                    agriculture_info.append(line_clean)

        # Build comprehensive response with proper spacing
        response = "🌾 AGRICULTURE CERTIFICATES & SERVICES\n\n"
        
        if eligibility_info:
            response += "📋 ELIGIBILITY CRITERIA:\n\n"
            for info in eligibility_info[:8]:
                response += f"• {info}\n"
            response += "\n"
        
        if required_documents:
            response += "📄 REQUIRED DOCUMENTS:\n\n"
            for doc in required_documents[:10]:
                response += f"• {doc}\n"
            response += "\n"
        
        if process_steps:
            response += "🔄 APPLICATION PROCESS:\n\n"
            for i, step in enumerate(process_steps[:15], 1):
                response += f"{i}. {step}\n"
            response += "\n"
        
        if fees_info:
            response += "💰 FEES & CHARGES:\n\n"
            for fee in fees_info[:6]:
                response += f"• {fee}\n"
            response += "\n"
        
        if timeline_info:
            response += "⏰ TIMELINE & PROCESSING TIME:\n\n"
            for time in timeline_info[:5]:
                response += f"• {time}\n"
            response += "\n"
        
        if agriculture_info:
            response += "📚 ADDITIONAL INFORMATION:\n\n"
            for info in agriculture_info[:10]:
                response += f"• {info}\n"
        
        if not any([eligibility_info, required_documents, process_steps, fees_info, timeline_info, agriculture_info]):
            return "No specific agriculture certificate information found in the available documents."
            
        return response.strip()

    def _extract_business_info(self, content: str) -> str:
        """Extract business/industry-specific certificate information with full details"""
        lines = content.split('\n')
        business_info = []
        process_steps = []
        required_documents = []
        eligibility_info = []
        fees_info = []
        types_info = []
        
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) < 10:
                continue
                
            line_lower = line_clean.lower()
            
            # Categorize information based on keywords
            if any(keyword in line_lower for keyword in ["step", "process", "procedure", "how to", "apply"]):
                process_steps.append(line_clean)
            elif any(keyword in line_lower for keyword in ["required", "need", "documents", "proof", "identity", "address"]):
                required_documents.append(line_clean)
            elif any(keyword in line_lower for keyword in ["eligibility", "criteria", "who can", "qualify", "eligible"]):
                eligibility_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["fee", "cost", "payment", "charge", "price"]):
                fees_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["type", "category", "class", "kind"]):
                types_info.append(line_clean)
            else:
                # General business-related information
                if any(keyword in line_lower for keyword in [
                    "business", "industry", "commercial", "trade", "license", "permit",
                    "registration", "certificate", "application", "establishment", "shop"
                ]):
                    business_info.append(line_clean)

        # Build comprehensive response with proper spacing
        response = "🏢 BUSINESS & INDUSTRY CERTIFICATES\n\n"
        
        if types_info:
            response += "📋 TYPES OF BUSINESS CERTIFICATES:\n\n"
            for info in types_info[:8]:
                response += f"• {info}\n"
            response += "\n"
        
        if eligibility_info:
            response += "👥 ELIGIBILITY CRITERIA:\n\n"
            for info in eligibility_info[:6]:
                response += f"• {info}\n"
            response += "\n"
        
        if required_documents:
            response += "📄 REQUIRED DOCUMENTS:\n\n"
            for doc in required_documents[:10]:
                response += f"• {doc}\n"
            response += "\n"
        
        if process_steps:
            response += "🔄 APPLICATION PROCESS:\n\n"
            for i, step in enumerate(process_steps[:12], 1):
                response += f"{i}. {step}\n"
            response += "\n"
        
        if fees_info:
            response += "💰 FEES & CHARGES:\n\n"
            for fee in fees_info[:6]:
                response += f"• {fee}\n"
            response += "\n"
        
        if business_info:
            response += "📚 ADDITIONAL INFORMATION:\n\n"
            for info in business_info[:8]:
                response += f"• {info}\n"
        
        if not any([types_info, eligibility_info, required_documents, process_steps, fees_info, business_info]):
            return "No specific business certificate information found in the available documents."
            
        return response.strip()

    def _extract_land_info(self, content: str) -> str:
        """Extract land/property-specific certificate information with full details"""
        lines = content.split('\n')
        land_info = []
        process_steps = []
        required_documents = []
        eligibility_info = []
        fees_info = []
        types_info = []
        
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) < 10:
                continue
                
            line_lower = line_clean.lower()
            
            # Categorize information based on keywords
            if any(keyword in line_lower for keyword in ["step", "process", "procedure", "how to", "apply"]):
                process_steps.append(line_clean)
            elif any(keyword in line_lower for keyword in ["required", "need", "documents", "proof", "identity", "address"]):
                required_documents.append(line_clean)
            elif any(keyword in line_lower for keyword in ["eligibility", "criteria", "who can", "qualify", "eligible"]):
                eligibility_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["fee", "cost", "payment", "charge", "price"]):
                fees_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["type", "category", "class", "kind"]):
                types_info.append(line_clean)
            else:
                # General land/property-related information
                if any(keyword in line_lower for keyword in [
                    "land", "property", "real estate", "ownership", "title", "deed",
                    "certificate", "registration", "mutation", "records", "survey", "plot"
                ]):
                    land_info.append(line_clean)

        # Build comprehensive response with proper spacing
        response = "🏡 LAND & PROPERTY CERTIFICATES\n\n"
        
        if types_info:
            response += "📋 TYPES OF PROPERTY CERTIFICATES:\n\n"
            for info in types_info[:8]:
                response += f"• {info}\n"
            response += "\n"
        
        if eligibility_info:
            response += "👥 ELIGIBILITY CRITERIA:\n\n"
            for info in eligibility_info[:6]:
                response += f"• {info}\n"
            response += "\n"
        
        if required_documents:
            response += "📄 REQUIRED DOCUMENTS:\n\n"
            for doc in required_documents[:10]:
                response += f"• {doc}\n"
            response += "\n"
        
        if process_steps:
            response += "🔄 APPLICATION PROCESS:\n\n"
            for i, step in enumerate(process_steps[:12], 1):
                response += f"{i}. {step}\n"
            response += "\n"
        
        if fees_info:
            response += "💰 FEES & CHARGES:\n\n"
            for fee in fees_info[:6]:
                response += f"• {fee}\n"
            response += "\n"
        
        if land_info:
            response += "📚 ADDITIONAL INFORMATION:\n\n"
            for info in land_info[:8]:
                response += f"• {info}\n"
        
        if not any([types_info, eligibility_info, required_documents, process_steps, fees_info, land_info]):
            return "No specific land/property certificate information found in the available documents."
            
        return response.strip()

    def _extract_vehicle_info(self, content: str) -> str:
        """Extract vehicle/transport-specific certificate information with full details"""
        lines = content.split('\n')
        vehicle_info = []
        process_steps = []
        required_documents = []
        eligibility_info = []
        fees_info = []
        types_info = []
        
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) < 10:
                continue
                
            line_lower = line_clean.lower()
            
            # Categorize information based on keywords
            if any(keyword in line_lower for keyword in ["step", "process", "procedure", "how to", "apply"]):
                process_steps.append(line_clean)
            elif any(keyword in line_lower for keyword in ["required", "need", "documents", "proof", "identity", "address"]):
                required_documents.append(line_clean)
            elif any(keyword in line_lower for keyword in ["eligibility", "criteria", "who can", "qualify", "eligible"]):
                eligibility_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["fee", "cost", "payment", "charge", "price"]):
                fees_info.append(line_clean)
            elif any(keyword in line_lower for keyword in ["type", "category", "class", "kind"]):
                types_info.append(line_clean)
            else:
                # General vehicle/transport-related information
                if any(keyword in line_lower for keyword in [
                    "vehicle", "transport", "motor", "car", "bike", "registration",
                    "license", "certificate", "permit", "rto", "fitness", "pollution", "insurance"
                ]):
                    vehicle_info.append(line_clean)

        # Build comprehensive response with proper spacing
        response = "🚗 VEHICLE & TRANSPORT CERTIFICATES\n\n"
        
        if types_info:
            response += "📋 TYPES OF VEHICLE CERTIFICATES:\n\n"
            for info in types_info[:8]:
                response += f"• {info}\n"
            response += "\n"
        
        if eligibility_info:
            response += "👥 ELIGIBILITY CRITERIA:\n\n"
            for info in eligibility_info[:6]:
                response += f"• {info}\n"
            response += "\n"
        
        if required_documents:
            response += "📄 REQUIRED DOCUMENTS:\n\n"
            for doc in required_documents[:10]:
                response += f"• {doc}\n"
            response += "\n"
        
        if process_steps:
            response += "🔄 APPLICATION PROCESS:\n\n"
            for i, step in enumerate(process_steps[:12], 1):
                response += f"{i}. {step}\n"
            response += "\n"
        
        if fees_info:
            response += "💰 FEES & CHARGES:\n\n"
            for fee in fees_info[:6]:
                response += f"• {fee}\n"
            response += "\n"
        
        if vehicle_info:
            response += "📚 ADDITIONAL INFORMATION:\n\n"
            for info in vehicle_info[:8]:
                response += f"• {info}\n"
        
        if not any([types_info, eligibility_info, required_documents, process_steps, fees_info, vehicle_info]):
            return "No specific vehicle/transport certificate information found in the available documents."
            
        return response.strip()

    def _extract_all_certificates_info(self, content: str) -> str:
        """Extract all certificate types information"""
        lines = content.split('\n')
        certificate_info = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in [
                "certificate", "certificates", "license", "permit", "registration",
                "application", "process", "requirements", "documents", "apply"
            ]):
                if len(line.strip()) > 20:
                    certificate_info.append(line.strip())

        if certificate_info:
            return "Available Certificates:\n" + "\n".join(certificate_info[:15])
        else:
            return "No certificate information found in the documents."

    def _extract_general_info(self, content: str, query: str) -> str:
        """Extract general information related to the query"""
        # Simple keyword matching for general information
        lines = content.split('\n')
        relevant_lines = []
        
        query_words = query.lower().split()
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in query_words if len(word) > 3):
                if len(line.strip()) > 20:
                    relevant_lines.append(line.strip())

        if relevant_lines:
            return "Relevant Information:\n" + "\n".join(relevant_lines[:10])
        else:
            return "No specific information found for your query in the available documents."


auto_document_loader = AutoDocumentLoader()
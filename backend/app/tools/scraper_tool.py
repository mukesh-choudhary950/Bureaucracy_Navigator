import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re
from app.tools.base import BaseTool, ToolResult
from urllib.parse import urljoin, urlparse

class ScraperTool(BaseTool):
    name = "scraper_tool"
    description = "Scrape procedure details from government websites"
    
    async def execute(self, url: str, content_type: str = "text") -> ToolResult:
        """Scrape content from a government website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            if content_type == "procedure":
                data = self._extract_procedure_info(soup, url)
            elif content_type == "documents":
                data = self._extract_document_requirements(soup, url)
            else:
                data = self._extract_general_content(soup, url)
            
            return ToolResult(
                success=True,
                data=data,
                metadata={"url": url, "content_type": content_type}
            )
            
        except requests.RequestException as e:
            return ToolResult(
                success=False,
                error=f"Failed to fetch URL: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Scraping error: {str(e)}"
            )
    
    def _extract_procedure_info(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract step-by-step procedure information"""
        content = {
            "title": "",
            "steps": [],
            "authority": "",
            "timeline": "",
            "fees": "",
            "contact": ""
        }
        
        # Extract title
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            content["title"] = title_tag.get_text().strip()
        
        # Look for procedure steps
        step_patterns = [
            r'step\s*\d+',
            r'procedure',
            r'process',
            r'how to',
            r'guidelines'
        ]
        
        # Find ordered lists or numbered headings
        lists_found = soup.find_all(['ol', 'ul'])
        for lst in lists_found:
            items = lst.find_all('li')
            if len(items) > 1:  # Only include lists with multiple items
                for item in items:
                    step_text = item.get_text().strip()
                    if len(step_text) > 10:  # Filter out very short items
                        content["steps"].append(step_text)
        
        # Look for authority information
        authority_keywords = ['authority', 'department', 'office', 'issued by']
        for keyword in authority_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                parent = elem.parent
                if parent and len(parent.get_text().strip()) > 20:
                    content["authority"] = parent.get_text().strip()
                    break
        
        # Look for timeline information
        timeline_keywords = ['days', 'weeks', 'timeline', 'duration', 'working days']
        for keyword in timeline_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                if len(elem.strip()) > 5:
                    content["timeline"] = elem.strip()
                    break
        
        # Look for fee information
        fee_keywords = ['fee', 'cost', 'charges', 'payment', 'rs.', '₹']
        for keyword in fee_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                if len(elem.strip()) > 5:
                    content["fees"] = elem.strip()
                    break
        
        return content
    
    def _extract_document_requirements(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract document requirements from web page"""
        documents = {
            "required_documents": [],
            "optional_documents": [],
            "formats": []
        }
        
        # Look for document lists
        doc_keywords = [
            'documents required',
            'required documents',
            'documents needed',
            'proof of',
            'identity proof',
            'address proof'
        ]
        
        for keyword in doc_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                parent = elem.parent
                if parent:
                    # Look for nearby lists
                    next_sibling = parent.find_next_sibling(['ul', 'ol'])
                    if next_sibling:
                        items = next_sibling.find_all('li')
                        for item in items:
                            doc_text = item.get_text().strip()
                            if len(doc_text) > 5:
                                documents["required_documents"].append(doc_text)
        
        # Look for format requirements
        format_keywords = ['format', 'size', 'pdf', 'jpg', 'scan', 'self-attested']
        for keyword in format_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                if len(elem.strip()) > 5:
                    documents["formats"].append(elem.strip())
        
        return documents
    
    def _extract_general_content(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract general text content"""
        # Get main content areas
        main_content = soup.find('main') or soup.find('div', class_='content') or soup
        
        # Extract text
        text = main_content.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return {
            "title": soup.find('title').get_text() if soup.find('title') else "",
            "content": text[:5000],  # Limit content length
            "url": base_url
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the government website to scrape"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["text", "procedure", "documents"],
                    "description": "Type of content to extract",
                    "default": "text"
                }
            },
            "required": ["url"]
        }

import pdfplumber
from PIL import Image
import pytesseract
import io
from typing import Dict, Any, List
from app.tools.base import BaseTool, ToolResult
import os

class DocumentParserTool(BaseTool):
    name = "document_parser"
    description = "Extract text from uploaded PDFs or images"
    
    async def execute(self, file_path: str, file_type: str = "auto") -> ToolResult:
        """Extract text from document file"""
        try:
            if not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            # Auto-detect file type if not specified
            if file_type == "auto":
                file_type = self._detect_file_type(file_path)
            
            if file_type.lower() == "pdf":
                text = self._extract_from_pdf(file_path)
            elif file_type.lower() in ["jpg", "jpeg", "png", "bmp", "tiff"]:
                text = self._extract_from_image(file_path)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported file type: {file_type}"
                )
            
            # Extract structured information
            structured_data = self._extract_structured_info(text)
            
            return ToolResult(
                success=True,
                data={
                    "raw_text": text,
                    "structured_data": structured_data,
                    "file_type": file_type,
                    "file_path": file_path
                },
                metadata={"extraction_method": file_type}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Document parsing error: {str(e)}"
            )
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext[1:] if ext else "unknown"
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
        
        return text.strip()
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image file using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            raise Exception(f"Image OCR failed: {str(e)}")
    
    def _extract_structured_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from document text"""
        structured = {
            "names": [],
            "dates": [],
            "addresses": [],
            "numbers": [],
            "keywords": []
        }
        
        # Common patterns for government documents
        import re
        
        # Extract names (simple pattern)
        name_patterns = [
            r'[A-Z][a-z]+ [A-Z][a-z]+',
            r'Mr\.?\s+[A-Z][a-z]+ [A-Z][a-z]+',
            r'Ms\.?\s+[A-Z][a-z]+ [A-Z][a-z]+'
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            structured["names"].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            structured["dates"].extend(matches)
        
        # Extract addresses (simple pattern)
        address_pattern = r'\d+\s+[^,]+,\s*[^,]+,\s*[^,]+'
        addresses = re.findall(address_pattern, text)
        structured["addresses"].extend(addresses)
        
        # Extract numbers (phone, aadhaar, etc.)
        number_patterns = [
            r'\d{10}',  # Phone numbers
            r'\d{12}',  # Aadhaar numbers
            r'\d{6,8}'  # Other government IDs
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            structured["numbers"].extend(matches)
        
        # Extract government document keywords
        gov_keywords = [
            'certificate', 'application', 'form', 'signature', 'verified',
            'approved', 'rejected', 'pending', 'submitted', 'authority',
            'department', 'government', 'official', 'seal', 'stamp'
        ]
        
        text_lower = text.lower()
        for keyword in gov_keywords:
            if keyword in text_lower:
                structured["keywords"].append(keyword)
        
        # Remove duplicates and limit results
        for key in structured:
            structured[key] = list(set(structured[key]))[:10]  # Limit to 10 items
        
        return structured
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file"
                },
                "file_type": {
                    "type": "string",
                    "enum": ["auto", "pdf", "jpg", "jpeg", "png", "bmp", "tiff"],
                    "description": "File type (auto-detect if not specified)",
                    "default": "auto"
                }
            },
            "required": ["file_path"]
        }

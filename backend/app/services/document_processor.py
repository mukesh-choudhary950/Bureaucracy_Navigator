"""Document Processing Service"""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import pdfplumber
import pytesseract
from PIL import Image
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing and splitting documents"""
    
    def __init__(self):
        """Initialize the document processor"""
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Supported file types
        self.supported_extensions = {'.pdf', '.txt', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        
        logger.info("Document processor initialized")
    
    def process_file(self, file_path: str, filename: str = None) -> Dict[str, Any]:
        """
        Process a file and extract text
        
        Args:
            file_path: Path to the file
            filename: Original filename
            
        Returns:
            Dictionary with processing results
        """
        try:
            if filename is None:
                filename = os.path.basename(file_path)
            
            file_ext = Path(filename).suffix.lower()
            
            if file_ext not in self.supported_extensions:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_ext}",
                    "supported_types": list(self.supported_extensions)
                }
            
            # Extract text based on file type
            if file_ext == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                text = self._extract_image_text(file_path)
            elif file_ext == '.txt':
                text = self._extract_txt_text(file_path)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_ext}"
                }
            
            if not text.strip():
                return {
                    "success": False,
                    "error": "No text could be extracted from the file"
                }
            
            # Split text into chunks
            chunks = self._split_text(text)
            
            # Create metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "filename": filename,
                    "file_type": file_ext,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "char_count": len(chunk),
                    "source": file_path
                }
                chunk_metadata.append(metadata)
            
            return {
                "success": True,
                "text": text,
                "chunks": chunks,
                "metadata": chunk_metadata,
                "stats": {
                    "total_characters": len(text),
                    "total_chunks": len(chunks),
                    "file_type": file_ext,
                    "filename": filename
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def _extract_image_text(self, file_path: str) -> str:
        """Extract text from image file using OCR"""
        try:
            # Open image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting image text: {str(e)}")
            raise
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e:
                logger.error(f"Error reading text file: {str(e)}")
                raise
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks using LangChain"""
        try:
            # Create LangChain document
            doc = Document(page_content=text)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Extract text from chunks
            return [chunk.page_content for chunk in chunks]
            
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            # Fallback to simple splitting
            return [text[i:i+1000] for i in range(0, len(text), 800)]
    
    def process_uploaded_file(
        self, 
        file_content: bytes, 
        filename: str,
        upload_dir: str = None
    ) -> Dict[str, Any]:
        """
        Process uploaded file content
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            upload_dir: Directory to save the file
            
        Returns:
            Processing results
        """
        try:
            if upload_dir is None:
                upload_dir = settings.UPLOAD_DIR
            
            # Create upload directory if it doesn't exist
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_ext = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Process the file
            result = self.process_file(file_path, filename)
            
            # Add file path to result
            if result["success"]:
                result["file_path"] = file_path
                result["stored_filename"] = unique_filename
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing uploaded file: {str(e)}")
            return {
                "success": False,
                "error": f"Upload processing error: {str(e)}"
            }
    
    def process(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process raw text content and split into chunks
        
        Args:
            text: Raw text content to process
            metadata: Optional metadata to attach to chunks
            
        Returns:
            Dictionary with chunks and metadata
        """
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "No text content provided",
                    "chunks": [],
                    "metadata": []
                }
            
            # Split text into chunks
            chunks = self._split_text(text)
            
            # Create metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "char_count": len(chunk),
                    "source": "auto_loaded"
                }
                
                # Add provided metadata
                if metadata:
                    chunk_meta.update(metadata)
                
                chunk_metadata.append(chunk_meta)
            
            return {
                "success": True,
                "chunks": chunks,
                "metadata": chunk_metadata,
                "stats": {
                    "total_characters": len(text),
                    "total_chunks": len(chunks)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return {
                "success": False,
                "error": f"Text processing error: {str(e)}",
                "chunks": [],
                "metadata": []
            }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats"""
        return {
            "text": [".txt"],
            "pdf": [".pdf"],
            "images": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]
        }

# Global instance
document_processor = DocumentProcessor()

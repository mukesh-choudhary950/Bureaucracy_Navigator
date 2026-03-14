from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.tools.document_parser import DocumentParserTool
from app.models.user import Document, User
from app.agent.memory import MemorySystem
import os
import uuid
import aiofiles
from typing import Dict, Any

router = APIRouter()

# Initialize components
document_parser = DocumentParserTool()
memory_system = MemorySystem()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = 1,  # Default user for demo
    db: Session = Depends(get_db)
):
    """Upload and parse a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Parse document
        parse_result = await document_parser.execute(file_path)
        
        # Store document record
        document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            content_type=file.content_type or "application/octet-stream",
            extracted_text=parse_result.data.get("raw_text", "") if parse_result.success else "",
            metadata={
                "file_size": len(file_content),
                "parsing_success": parse_result.success,
                "structured_data": parse_result.data.get("structured_data", {}) if parse_result.success else {},
                "parsing_error": parse_result.error if not parse_result.success else None
            }
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Store in memory system
        if parse_result.success:
            memory_system.store_document_memory(user_id, {
                "type": "uploaded_document",
                "filename": file.filename,
                "file_path": file_path,
                "content_type": file.content_type,
                "structured_data": parse_result.data.get("structured_data", {}),
                "document_id": document.id
            })
        
        return {
            "message": "Document uploaded and parsed successfully",
            "document_id": document.id,
            "filename": file.filename,
            "file_size": len(file_content),
            "parsing_success": parse_result.success,
            "extracted_text": parse_result.data.get("raw_text", "")[:500] if parse_result.success else None,
            "structured_data": parse_result.data.get("structured_data", {}) if parse_result.success else None,
            "error": parse_result.error if not parse_result.success else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@router.get("/documents")
async def get_user_documents(
    user_id: int = 1,  # Default user for demo
    db: Session = Depends(get_db)
):
    """Get all documents for a user"""
    documents = db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).all()
    
    result = []
    for doc in documents:
        result.append({
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "file_size": doc.metadata.get("file_size", 0) if doc.metadata else 0,
            "extracted_text": doc.extracted_text[:200] if doc.extracted_text else None,
            "structured_data": doc.metadata.get("structured_data", {}) if doc.metadata else {},
            "created_at": doc.created_at,
            "parsing_success": doc.metadata.get("parsing_success", True) if doc.metadata else True
        })
    
    return {"documents": result}

@router.get("/document/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get specific document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "content_type": document.content_type,
        "file_path": document.file_path,
        "extracted_text": document.extracted_text,
        "metadata": document.metadata,
        "created_at": document.created_at
    }

@router.delete("/document/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document deletion failed: {str(e)}")

@router.post("/document/{document_id}/extract")
async def re_extract_document(document_id: int, db: Session = Depends(get_db)):
    """Re-extract text from a document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Re-parse document
        parse_result = await document_parser.execute(document.file_path)
        
        if parse_result.success:
            # Update document record
            document.extracted_text = parse_result.data.get("raw_text", "")
            if document.metadata:
                document.metadata["structured_data"] = parse_result.data.get("structured_data", {})
                document.metadata["parsing_success"] = True
                document.metadata["parsing_error"] = None
            db.commit()
            
            return {
                "message": "Document re-extracted successfully",
                "extracted_text": parse_result.data.get("raw_text", ""),
                "structured_data": parse_result.data.get("structured_data", {})
            }
        else:
            raise HTTPException(status_code=500, detail=f"Document extraction failed: {parse_result.error}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document re-extraction failed: {str(e)}")

@router.get("/document/{document_id}/download")
async def download_document(document_id: int, db: Session = Depends(get_db)):
    """Get download URL for a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return {
        "filename": document.filename,
        "file_path": document.file_path,
        "content_type": document.content_type,
        "download_ready": True
    }

@router.post("/documents/search")
async def search_documents(
    request: Dict[str, Any],
    user_id: int = 1,  # Default user for demo
    db: Session = Depends(get_db)
):
    """Search through user documents"""
    try:
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Get all user documents
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        
        # Simple text search
        results = []
        query_lower = query.lower()
        
        for doc in documents:
            if doc.extracted_text and query_lower in doc.extracted_text.lower():
                results.append({
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "content_type": doc.content_type,
                    "matched_text": doc.extracted_text[:200] + "..." if len(doc.extracted_text) > 200 else doc.extracted_text,
                    "created_at": doc.created_at
                })
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document search failed: {str(e)}")

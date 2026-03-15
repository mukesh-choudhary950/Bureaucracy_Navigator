from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Check file type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Process document content
        if file_extension == '.pdf':
            from app.services.document_processor import document_processor
            text = document_processor._extract_pdf_text(file_content)
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            from app.services.document_processor import document_processor
            text = document_processor._extract_image_text(file_content)
        else:  # .txt
            text = file_content.decode('utf-8')
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Process text and create chunks
        chunks = document_processor.process(
            text=text,
            metadata={
                "filename": file.filename,
                "file_size": len(file_content),
                "content_type": file.content_type,
                "document_id": document_id
            }
        )
        
        # Store in vector database
        if chunks and chunks.get("chunks"):
            vector_store.add_document_chunks(
                chunks=chunks["chunks"],
                metadata=chunks["metadata"],
                document_id=document_id
            )
            
            return {
                "message": "Document uploaded and processed successfully",
                "document_id": document_id,
                "filename": file.filename,
                "file_size": len(file_content),
                "chunks_processed": len(chunks["chunks"]),
                "extracted_text_preview": text[:200] + "..." if len(text) > 200 else text
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to process document")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        stats = vector_store.get_collection_stats()
        return {
            "documents": stats.get("total_documents", 0),
            "total_chunks": stats.get("total_chunks", 0),
            "message": "Document listing available"
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving documents")

@router.get("/document/{document_id}")
async def get_document(document_id: str):
    """Get document by ID"""
    try:
        # This would require implementing document retrieval from vector store
        return {"message": f"Document {document_id} retrieval not implemented yet"}
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving document")

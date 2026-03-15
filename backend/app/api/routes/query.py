from fastapi import APIRouter, HTTPException
from app.agent.simple_rag import simple_rag_agent
from app.services.initialization import initialization_service
from app.services.vector_store import vector_store
from app.services.auto_document_loader import auto_document_loader
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter()

class SimpleQueryRequest(BaseModel):
    question: str
    max_results: int = 5

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class TargetedSummaryRequest(BaseModel):
    query: str
    max_results: int = 3

@router.post("/ask-simple")
async def ask_simple_question(request: SimpleQueryRequest):
    """Simple RAG question answering"""
    try:
        result = await simple_rag_agent.answer_question(request.question, request.max_results)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(request: SearchRequest):
    """Search documents without AI generation"""
    try:
        results = vector_store.similarity_search(request.query, request.max_results)
        return {
            "query": request.query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = vector_store.get_collection_stats()
        return {
            "vector_store": stats,
            "auto_load_status": initialization_service.get_initialization_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auto-load-status")
async def get_auto_load_status():
    """Get automatic document loading status"""
    return initialization_service.get_initialization_status()

@router.post("/scan-pdfs")
async def scan_pdfs():
    """Scan and process all PDF files in documents directory"""
    try:
        result = auto_document_loader.scan_local_pdfs()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug-docs")
async def debug_documents():
    """Debug endpoint to check document status"""
    try:
        return {
            "loaded_pdfs_count": len(auto_document_loader.loaded_pdfs),
            "loaded_pdfs": list(auto_document_loader.loaded_pdfs.keys()),
            "vector_store_stats": vector_store.get_collection_stats() if hasattr(vector_store, 'get_collection_stats') else "Not available"
        }
    except Exception as e:
        return {
            "error": str(e),
            "loaded_pdfs_count": 0,
            "loaded_pdfs": [],
            "vector_store_stats": "Error"
        }

@router.post("/targeted-summary")
async def get_targeted_summary(request: TargetedSummaryRequest):
    """Get targeted summary from local documents only"""
    try:
        # Get summary from local PDF documents only
        result = auto_document_loader.get_targeted_summary(
            request.query,
            request.max_results
        )
        
        # Check if the result was successful
        if result.get("success", False):
            return {
                "success": True,
                "summary": result.get("summary", "No summary available"),
                "sources": []  # Sources are hidden
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "summary": None
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": None
        }

@router.get("/pdf-status")
async def get_pdf_status():
    """Get status of loaded PDFs"""
    try:
        loaded_pdfs = auto_document_loader.loaded_pdfs
        return {
            "total_pdfs": len(loaded_pdfs),
            "pdf_files": list(loaded_pdfs.keys()),
            "categories": {
                name: info.get("category", "General") 
                for name, info in loaded_pdfs.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""Service Initialization Module"""

import asyncio
import logging
from app.services.auto_document_loader import auto_document_loader
from app.core.config import settings

logger = logging.getLogger(__name__)

class InitializationService:
    """Service to initialize system with automated document loading"""
    
    def __init__(self):
        self.auto_loader = auto_document_loader
        self.initialized = False
    
    async def initialize_system(self):
        """Initialize system with automated document loading - runs in background"""
        logger.info("🚀 Starting Bureaucracy Navigator Agent initialization...")
        
        # Run document loading in background task so it doesn't block startup
        asyncio.create_task(self._load_documents_async())
        
        logger.info("✅ API is ready! Document loading will continue in background.")
        return True
    
    async def _load_documents_async(self):
        """Load documents asynchronously without blocking"""
        try:
            # Add a small delay to ensure API is fully started first
            await asyncio.sleep(2)
            
            logger.info("📄 Loading government documents in background...")
            results = self.auto_loader.load_government_documents()
            
            # Log results
            logger.info(f"✅ Auto-load completed:")
            logger.info(f"   - Sources attempted: {len(results['sources'])}")
            logger.info(f"   - Documents loaded: {results['loaded_documents']}")
            logger.info(f"   - Documents processed: {results['processed_documents']}")
            
            if results['errors']:
                logger.warning(f"⚠️  Errors encountered: {len(results['errors'])}")
                for error in results['errors']:
                    logger.warning(f"   - {error}")
            
            self.initialized = True
            logger.info("🎯 Background document loading complete!")
            
        except Exception as e:
            logger.error(f"❌ Background document loading failed: {str(e)}")
    
    def get_initialization_status(self) -> dict:
        """Get status of last initialization"""
        return {
            "auto_load_enabled": True,
            "sources_configured": [
                "India Government Services",
                "Passport Seva Kendra", 
                "Telangana Meeseva",
                "Aadhaar Services"
            ],
            "last_run": "Server startup",
            "initialized": self.initialized
        }

# Global instance
initialization_service = InitializationService()

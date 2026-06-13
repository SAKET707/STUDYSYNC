import logging
from qdrant_client import QdrantClient
from config.settings import settings

logger = logging.getLogger(__name__)

class QdrantClientFactory:
    """
    Infrastructure Factory Layer Module.
    Responsibility: Handle core instantiation and low-level configuration of the connection client pool.
    Strictly isolated from schema execution (DDL) and vector operations (CRUD).
    """

    @staticmethod
    def create() -> QdrantClient:
        """
        Builds and registers a thread-safe, unified QdrantClient network wrapper.
        Enforces validation checks against critical environment contexts before initializing connection channels.
        """
        if not settings.QDRANT_URL:
            logger.error("Database connection failure: QDRANT_URL configuration is missing or empty.")
            raise ValueError("QDRANT_URL must be defined within your configuration layer before starting services.")

        logger.info(f"Initializing persistent network connection pool targeting Qdrant cluster: '{settings.QDRANT_URL}'")
        
        try:
           
            api_key_value = settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
            
            return QdrantClient(
                url=settings.QDRANT_URL,
                api_key=api_key_value,
                timeout=60.0  
            )
        except Exception as e:
            logger.exception(f"Fatal orchestration error encountered while establishing Qdrant Client pool: {e}")
            raise
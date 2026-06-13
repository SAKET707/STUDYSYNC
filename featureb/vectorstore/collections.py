import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType
)


from config.constants import COLLECTION_NAME, EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

class QdrantCollectionManager:
    """
    Infrastructure Layer Module.
    Responsibility: Handle Data Definition Language (DDL) state definitions for Qdrant.
    Strictly isolated from client creation, vector insertion, or search routines.
    """

    def __init__(self, client: QdrantClient):
       
        self.client = client

    def cluster_health_check(self) -> bool:
        """
        Executes a rapid, lightweight cluster ping to verify connection stability.
        Useful for FastAPI startup events, Docker health probes, or readiness checks.
        """
        try:
            
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Database network health assertion failed: {e}")
            return False

    def collection_exists(self, collection_name: str = COLLECTION_NAME) -> bool:
        """
        Queries the Qdrant cluster to verify if the targeting collection space exists.
        """
        try:
            return self.client.collection_exists(collection_name=collection_name)
        except Exception as e:
            logger.error(f"Failed infrastructure check for collection '{collection_name}': {e}")
            raise

    def _create_payload_indexes(
    self,
    collection_name: str
    ) -> None:
        """
        Creates payload indexes required for metadata filtering.

        Indexed Fields:
            - chapter      (keyword)
            - chunk_type   (keyword)
            - class_number (integer)
        """

        logger.info(
            f"Creating payload indexes for '{collection_name}'"
        )

        try:
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="chapter",
                field_schema=PayloadSchemaType.KEYWORD
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="chunk_type",
                field_schema=PayloadSchemaType.KEYWORD
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="class_number",
                field_schema=PayloadSchemaType.INTEGER
            )

            logger.info(
                f"Payload indexes created successfully for '{collection_name}'"
            )

        except Exception as e:
            logger.exception(
                f"Failed creating payload indexes for "
                f"'{collection_name}': {e}"
            )
            raise

    def create_collection(
        self, 
        collection_name: str = COLLECTION_NAME, 
        dimension: int = EMBEDDING_DIMENSION
    ) -> bool:
        """
        Creates a raw storage partition matching the target embedding shapes.
        Guarded with an active short-circuit existence safety sweep.
        """
        if dimension <= 0:
            raise ValueError(
                f"Invalid vector dimension: {dimension}"
            )
        
        if self.collection_exists(collection_name):
            logger.info(f"Collection '{collection_name}' already exists. Skipping creation block.")
            return True

        logger.info(f"Initializing Qdrant Collection structure: '{collection_name}' [Dimension: {dimension}]")
        try:
            self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=Distance.COSINE
            )
        )
            self._create_payload_indexes(
            collection_name=collection_name
            )
            logger.info(f"Successfully initialized storage context for '{collection_name}'.")
            return True
        
        except Exception as e:
            logger.exception(f"Fatal error during cluster infrastructure creation for '{collection_name}': {e}")
            raise

    def delete_collection(self, collection_name: str = COLLECTION_NAME) -> bool:
        """
        Flushes data vectors and clears out the collection workspace completely.
        Guarded with an active short-circuit missing validation check.
        """
       
        if not self.collection_exists(collection_name):
            logger.info(f"Collection '{collection_name}' does not exist. Skipping deletion block.")
            return True

        logger.warning(f"CRITICAL DATA TRUNCATION INITIATED: Dropping collection '{collection_name}' completely!")
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Successfully flushed and dropped tracking collection '{collection_name}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to drop storage partition for collection '{collection_name}': {e}")
            raise

    def recreate_collection(
        self, 
        collection_name: str = COLLECTION_NAME, 
        dimension: int = EMBEDDING_DIMENSION
    ) -> bool:
        """
        Development utility routine: Forces structural lifecycle rebuilding to clear layout schemas.
        """
        logger.info(f"Executing active structural database reset on target workspace: '{collection_name}'")
        self.delete_collection(collection_name)
        return self.create_collection(collection_name=collection_name, dimension=dimension)
import logging
from typing import List, Union

import torch
from sentence_transformers import SentenceTransformer

from ingestion.schemas import (
    ParentChunk,
    ChildChunk,
    EmbeddedChunk
)

logger = logging.getLogger(__name__)


class TextbookEmbedder:
    """
    Component 3 of the Ingestion Pipeline.

    Responsibility:
        Convert ParentChunk and ChildChunk objects into
        normalized embedding vectors.

    Input:
        ParentChunk | ChildChunk

    Output:
        EmbeddedChunk

    Notes:
        - Uses BAAI/bge-large-en-v1.5
        - Generates 1024-dimensional vectors
        - Supports batch processing
        - Produces unit-normalized embeddings for Qdrant
    """

    EXPECTED_DIMENSION = 1024

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        batch_size: int = 32,
    ):
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self.batch_size = batch_size

       
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

        logger.info(
            f"Loading embedding model '{model_name}' "
            f"on device '{self.device}'"
        )

        self.model = SentenceTransformer(
            model_name,
            device=self.device
        )

    def generate_embeddings(
        self,
        chunks: List[Union[ParentChunk, ChildChunk]]
    ) -> List[EmbeddedChunk]:
        """
        Generate embeddings for a batch of chunks.

        Args:
            chunks:
                List of ParentChunk or ChildChunk objects.

        Returns:
            List[EmbeddedChunk]
        """

        if not chunks:
            logger.warning(
                "Embedding request received empty chunk list."
            )
            return []

        logger.info(
            f"Generating embeddings for {len(chunks)} chunks."
        )

        texts = [chunk.text for chunk in chunks]

        with torch.inference_mode():
            vectors = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

        # Safety validation
        if vectors.shape[1] != self.EXPECTED_DIMENSION:
            raise ValueError(
                f"Expected embedding dimension "
                f"{self.EXPECTED_DIMENSION}, "
                f"received {vectors.shape[1]}"
            )

        embedded_chunks = []

        for chunk, vector in zip(chunks, vectors):
            embedded_chunks.append(
                EmbeddedChunk(
                    chunk=chunk,
                    embedding=vector.tolist()
                )
            )

        logger.info(
            f"Successfully embedded "
            f"{len(embedded_chunks)} chunks."
        )

        return embedded_chunks
    
    def embed_query(self, text: str) -> List[float]:
            """
            Executes real-time normalization and embedding for a single query string.
            Hides the ML implementation details from the retrieval layers.
            """
            if not text or not text.strip():
                raise ValueError("Cannot embed an empty query string.")

            vector = self.model.encode(
                text,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return vector.tolist()
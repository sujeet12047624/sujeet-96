"""Semantic RAG Search Engine using OpenAI Embeddings + Qdrant."""

import logging
import uuid

import openai
from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


class RAGEngine:
    """Handles document ingestion, chunking, embedding, and semantic search."""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.qdrant = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()

    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            collections = [c.name for c in self.qdrant.get_collections().collections]
            if self.collection_name not in collections:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=EMBEDDING_DIM,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("Created Qdrant collection: %s", self.collection_name)
        except Exception as e:
            logger.warning("Could not ensure Qdrant collection: %s", e)

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks of ~500 tokens."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + CHUNK_SIZE
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - CHUNK_OVERLAP
        return chunks

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Compute embeddings via text-embedding-3-small."""
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.exception("Embedding computation failed")
            return []

    def ingest_text(self, text: str, metadata: dict):
        """Chunk, embed, and upsert text into Qdrant."""
        chunks = self._chunk_text(text)
        if not chunks:
            return

        embeddings = self._get_embeddings(chunks)
        if not embeddings:
            return

        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        **metadata,
                    },
                )
            )

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info("Ingested %d chunks for: %s", len(points), metadata.get("title", "unknown"))

    def search(self, query: str, top_k: int = 5) -> dict:
        """Semantic search: embed query, find nearest vectors, return results."""
        query_embeddings = self._get_embeddings([query])
        if not query_embeddings:
            return {"results": [], "error": "Failed to compute query embedding"}

        try:
            hits = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embeddings[0],
                limit=top_k,
            )
            results = []
            for hit in hits:
                results.append(
                    {
                        "text": hit.payload.get("text", ""),
                        "score": round(hit.score, 4),
                        "metadata": {
                            k: v
                            for k, v in hit.payload.items()
                            if k not in ("text",)
                        },
                    }
                )
            return {"query": query, "results": results, "total": len(results)}
        except Exception as e:
            logger.exception("Semantic search failed")
            return {"results": [], "error": str(e)}

    def ingest_pdf(self, pdf_path: str, metadata: dict):
        """Extract text from PDF, then ingest."""
        try:
            import PyPDF2

            text_parts = []
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            full_text = "\n".join(text_parts)
            self.ingest_text(full_text, metadata)
        except Exception as e:
            logger.exception("PDF ingestion failed for %s", pdf_path)

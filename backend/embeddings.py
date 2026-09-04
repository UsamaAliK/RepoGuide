import asyncio
import logging
from sentence_transformers import SentenceTransformer
from .config import settings

logger = logging.getLogger(__name__)

# --- local sentence-transformers model (loaded once, lazy) ---

_model = None

def _get_model():
    global _model
    if _model is None:
        logger.info(f"Loading local {settings.EMBEDDING_DIMENSIONS}-dim embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

# --- sync batch embed (called via asyncio.to_thread) ---

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts locally with {dim}-dimension vectors."""
    if not texts:
        return []
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return [e.tolist() for e in embeddings]

# --- async wrappers ---

async def embed_text(
    texts: list[str],
    **kwargs
) -> list[list[float]]:
    """Embed texts asynchronously using local model."""
    if not texts:
        return []
    return await asyncio.to_thread(embed_batch, texts)

async def embed_query(text: str) -> list[float]:
    """Embed a single query."""
    result = await embed_text([text])
    return result[0] if result else []
from dotenv import load_dotenv
import os
import httpx

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")

async def rerank(query: str, documents: list[str], top_n: int) -> list[tuple[int, float]]:
    """Rerank documents using Jina AI Reranker API.

    Returns list of (original_index, relevance_score) sorted by relevance descending.
    """
    if not documents:
        return []

    url = "https://api.jina.ai/v1/rerank"
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "jina-reranker-v1-base-en",
        "query": query,
        "documents": documents,
        "top_n": top_n,
    }

    resp = httpx.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    results = sorted(data["results"], key=lambda x: x["relevance_score"], reverse=True)
    return [(r["index"], r["relevance_score"]) for r in results]

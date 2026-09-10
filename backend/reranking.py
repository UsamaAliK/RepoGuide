from dotenv import load_dotenv
import os
import asyncio
import httpx

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")

TIMEOUT = 30.0
RETRIES = 2

async def rerank(query: str, documents: list[str], top_n: int) -> list[tuple[int, float]]:
    """Rerank documents using Jina AI Reranker API.

    Returns list of (original_index, relevance_score) sorted by relevance descending.
    Async client (no event-loop blocking); 30s timeout; one retry for transient
    errors/rate limits (429) per AGENTS known-issues.
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

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(RETRIES):
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 429 and attempt < RETRIES - 1:
                    await asyncio.sleep(2)
                    continue
                resp.raise_for_status()
                data = resp.json()
                results = sorted(data["results"], key=lambda x: x["relevance_score"], reverse=True)
                return [(r["index"], r["relevance_score"]) for r in results]
            except (httpx.HTTPError, KeyError):
                if attempt < RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                raise
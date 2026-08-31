import asyncio
import time
import json
import google.generativeai as genai
from .config import EMBEDDING_DIMENSIONS,GEMINI_API_KEY
import urllib.request
from .llm import generate_answer
from .github import download_repo_zip,parse_github_url,get_repo_metadata
from .chunking import chunk_files
from .embeddings import embed_text,embed_batch
from .vector_storage import add_chunks,query_chunks

genai.configure(api_key=GEMINI_API_KEY)

TOP_K=5

def latest_commit_sha(owner: str, repo: str, branch: str) -> str:
    """Fetch the current commit SHA for a branch."""
    with urllib.request.urlopen(
        f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    ) as r:
        return json.load(r)["sha"]
async def index_repo(url:str)->dict:
    info=parse_github_url(url)
    owner=info["owner"]
    repo=info["repo"]
    meta=await get_repo_metadata(owner,repo)
    branch=meta["default_branch"]
    downloaded=await download_repo_zip(owner,repo,branch)
    files=downloaded["filtered files"]
    if not files:
        raise ValueError("No filterable file found in this repo")
    commit_sha= await asyncio.to_thread(latest_commit_sha,owner,repo,branch)
    chunks= await asyncio.to_thread(chunk_files,files,commit_sha,owner,repo)
    if not chunks:
        raise ValueError("Repositry produced no chunks")
    texts=[c["text"] for c in chunks]
    vectors=await embed_text(texts,task_type="RETRIEVAL_DOCUMENT")
    if not all (len(v)==EMBEDDING_DIMENSIONS for v in vectors):
        raise ValueError("Embedding dimension mismatch")
    await asyncio.to_thread(add_chunks, chunks, vectors)

    return {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "commit_sha": commit_sha,
        "file_count": len(files),
        "chunk_count": len(chunks),
    }

    


    
async def ask(question: str, url: str, top_k: int = TOP_K) -> dict:
    info = parse_github_url(url)
    owner, repo = info["owner"], info["repo"]
    qvec = await asyncio.to_thread(
        lambda: embed_batch([question], task_type="RETRIEVAL_QUERY")[0]
    )
    docs, metas, distances = await asyncio.to_thread(
        query_chunks, owner, repo, qvec, top_k
    )
    if not docs:
        return {"answer": "No matching code found in this repository.", "sources": []}

    context = "\n\n".join(docs)
    answer = await asyncio.to_thread(generate_answer,question, context)
    sources = [
        {
            "file_path": m["file_path"],
            "start_line": m["start_line"],
            "end_line": m["end_line"],
            "commit_sha": m["commit_sha"],
            "distance": round(d, 5),
        }
        for m, d in zip(metas, distances)
    ]
    return {"answer": answer, "sources": sources}
from fastapi import FastAPI, HTTPException
from .schemas import RepoRequest, RepoResponse
from .github import fetch_repo_files
from .chunking import chunk_files
from .embeddings import generate_embeddings
from .database import store_chunks

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "RepoGuide running"}






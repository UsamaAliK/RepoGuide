from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from .schemas import RepoRequest, RepoResponse,AskRequest,AskResponse
from .rag import index_repo, ask

# --- FastAPI routes ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
async def root():
    return {"message": "RepoGuide running"}

# POST /index — download, filter, chunk, embed, store a repo

@app.post("/index", response_model=RepoResponse)
async def index(request: RepoRequest):
    try:
        result = await index_repo(request.url)
        return RepoResponse(
            url=request.url,
            status="success",
            message="Repository indexed successfully",
            file_count=result["file_count"],
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /ask — embed question → search chroma → neighbors → LLM → answer + sources

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        result = await ask(request.question, request.url)
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

# --- request/response models for the API ---

class RepoRequest(BaseModel):
    """POST /index — body: {"url": "https://github.com/owner/repo"}"""
    url:str

class RepoResponse(BaseModel):
    """POST /index — response after indexing a repo"""
    url:str
    status:str
    message:str
    file_count:int

class AskRequest(BaseModel):
    """POST /ask — body: {"url": "...", "question": "..."}"""
    url:str
    question:str

class Source(BaseModel):
    """A source link back to the exact file + line range in the repo"""
    file_path: str
    start_line: int
    end_line: int
    commit_sha: str
    score: float

class AskResponse(BaseModel):
    """POST /ask — response: answer text + source links"""
    answer:str
    sources:list[Source]
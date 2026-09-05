from pydantic import BaseModel, ConfigDict
from pydantic import field_validator,HttpUrl
from datetime import datetime

# --- request/response models for the API ---

class RepoRequest(BaseModel):
    """POST /index — body: {"url": "https://github.com/owner/repo"}"""
    url:str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if not v.startswith("https://github.com/"):
            raise ValueError("URL must be a GitHub repository URL")
        return v
class RepoResponse(BaseModel):
    """POST /index — response after indexing a repo"""
    url:str
    status:str
    message:str
    file_count:int
class RepoInfo(BaseModel):
    """Repository information returned after indexing"""
    model_config=ConfigDict(from_attributes=True)
    id:int
    github_url:str
    owner:str
    repo_name:str
    branch:str
    commit_sha:str
    status:str
    created_at:datetime
class AskRequest(BaseModel):
    """POST /ask — body: {"url": "...", "question": "..."}"""
    url:str
    question:str

class Source(BaseModel):
    """A source link back to the exact file + line range in the repo"""
    model_config=ConfigDict(from_attributes=True)
    file_path: str
    start_line: int
    end_line: int
    commit_sha: str
    score: float

class AskResponse(BaseModel):
    """POST /ask — response: answer text + source links"""
    answer:str
    sources:list[Source]

class MessageInfo(BaseModel):
    """A message in a conversation"""
    model_config=ConfigDict(from_attributes=True)
    id:int
    role:str
    content:str
    created_at:datetime
    sources:list[Source]
class ConversationInfo(BaseModel):
    """A conversation in a repository"""
    model_config=ConfigDict(from_attributes=True)
    id:int
    repository_id:int
    title:str
    created_at:datetime
    updated_at:datetime
class ChatRequest(BaseModel):
    """POST /api/chat — body: {"url": "...", "question": "...", "conversation_id": 0} (0 creates a new conversation)"""
    url:str
    question:str
    conversation_id:int
class ChatResponse(BaseModel):
    """POST /api/chat — response: answer text + source links + conversation id"""
    answer:str
    conversation_id:int
    sources:list[Source]
class RegisterRequest(BaseModel):
    """POST /api/register — body: {"username": "...", "password": "..."}"""
    username:str
    password:str
class LoginRequest(BaseModel):
    """POST /api/login — body: {"username": "...", "password": "..."}"""
    username:str
    password:str
class TokenResponse(BaseModel):
    """POST /api/login — response: {"access_token": "...", "token_type": "bearer"}"""
    access_token:str
    token_type:str="bearer"
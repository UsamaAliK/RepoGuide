from pydantic import BaseModel


class RepoRequest(BaseModel):
    url:str

class RepoResponse(BaseModel):
    url:str
    status:str
    message:str
    file_count:int

class AskRequest(BaseModel):
    url:str
    question:str

class Source(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    commit_sha: str
    distance: float

class AskResponse(BaseModel):
    answer:str
    sources:list[Source]
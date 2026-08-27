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

class AskResponse(BaseModel):
    source:list[str]
    answer:str
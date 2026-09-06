from fastapi import FastAPI, HTTPException,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (RepoRequest, RepoResponse,
                      ConversationInfo,MessageInfo,RepoInfo,ChatRequest,
                      ChatResponse,RegisterRequest,LoginRequest,TokenResponse)
from .database import get_db
from .rag import index_repo, ask
from .models import User, Repository, Conversation, Message, MessageSource
from .auth import password_hash, verify_password, create_access_token,current_user

# --- FastAPI routes ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
async def root():
    return {"message": "RepoGuide running"}

# POST /index — download, filter, chunk, embed, store a repo

@app.post("/index", response_model=RepoResponse)
async def index(request: RepoRequest,db: Annotated[AsyncSession, Depends(get_db)],user:Annotated[User,Depends(current_user)]):
    try:
        result = await index_repo(request.url)
        existing = (await db.execute(
            select(Repository).where(
                Repository.owner == result["owner"],
                Repository.repo_name == result["repo"],
                Repository.user_id == user.id,
            )
        )).scalar_one_or_none()
        if existing is None:
            db.add(Repository(
                user_id=user.id,
                github_url=request.url,
                owner=result["owner"],
                repo_name=result["repo"],
                branch=result["branch"],
                commit_sha=result["commit_sha"],
                status="indexed",
            ))
            await db.commit()

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

@app.get("/api/repositories", response_model=list[RepoInfo])
async def get_repositories(db: Annotated[AsyncSession, Depends(get_db)],user:Annotated[User,Depends(current_user)]):
    try:
        result = await db.execute(select(Repository).where(Repository.user_id == user.id))
        repositories = result.scalars().all()
        return repositories
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repositories/{repo_id}", response_model=RepoInfo)
async def get_repository(repo_id: int, db: Annotated[AsyncSession, Depends(get_db)],user:Annotated[User,Depends(current_user)]):
    try:
        result = await db.execute(select(Repository).where(Repository.id == repo_id))
        repository = result.scalar_one_or_none()
        if repository is None:
            raise HTTPException(status_code=404, detail="Repository not found")
        if repository.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this repository")
        return repository
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations", response_model=list[ConversationInfo])
async def get_all_conversations(db: Annotated[AsyncSession, Depends(get_db)],user:Annotated[User,Depends(current_user)]):
    try:
        result = await db.execute(select(Conversation).where(Conversation.user_id == user.id))
        conversations = result.scalars().all()
        return conversations
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{repo_id}", response_model=list[ConversationInfo])
async def get_conversations(repo_id: int, db: Annotated[AsyncSession, Depends(get_db)],user:Annotated[User,Depends(current_user)]):
    try:
        repo = await db.execute(select(Repository).where(Repository.id == repo_id))
        repo = repo.scalar_one_or_none()
        if repo is None:
            raise HTTPException(status_code=404, detail="Repository not found")
        if repo.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this repository")
        result = await db.execute(select(Conversation).where(
            Conversation.repository_id == repo_id,
            Conversation.user_id == user.id,
        ))
        conversations = result.scalars().all()
        return conversations
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{conversation_id}", response_model=list[MessageInfo])
async def get_messages(conversation_id: int, db: Annotated[AsyncSession, Depends(get_db)],user:Annotated[User,Depends(current_user)]):
    try:
        conversation = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = conversation.scalar_one_or_none()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        result = await db.execute(select(Message).options(selectinload(Message.sources)).where(Message.conversation_id == conversation_id))
        messages = result.scalars().all()
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Annotated[AsyncSession,Depends(get_db)],user:Annotated[User,Depends(current_user)]):


    repo=await db.execute(select(Repository).where(Repository.github_url==request.url,Repository.user_id==user.id))
    repo=repo.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    conversation=None
    if request.conversation_id!=0:
        conversation=await db.execute(select(Conversation).where(
            Conversation.id==request.conversation_id,
            Conversation.user_id==user.id,
        ))
        conversation=conversation.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.repository_id != repo.id:
            raise HTTPException(status_code=404, detail="Conversation does not belong to this repository")
    # ask question
    try:
        result=await ask(request.question,request.url)
        if conversation is None:
            conversation=Conversation(repository_id=repo.id,title=repo.repo_name,user_id=user.id)
            db.add(conversation)
            await db.flush()
        # store question and answer in messages
        question_message=Message(
            conversation_id=conversation.id,
            role="user",
            content=request.question,
        )
        answer_message=Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
        )
        db.add_all([question_message,answer_message])
        await db.flush()
        # store sources tied to the assistant message
        for s in result["sources"]:
            db.add(MessageSource(
                message_id=answer_message.id,
                file_path=s["file_path"],
                start_line=s["start_line"],
                end_line=s["end_line"],
                commit_sha=s["commit_sha"],
                score=s["score"],
            ))
        await db.commit()
        return ChatResponse(
            answer=result["answer"],
            conversation_id=conversation.id,
            sources=result["sources"],
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/api/register", response_model=TokenResponse)
async def register(request:RegisterRequest,db:Annotated[AsyncSession,Depends(get_db)]):
    """Register a new user and return a JWT token"""
    try:
        existing_user=await db.execute(select(User).where(User.username==request.username))
        existing_user=existing_user.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400,detail="Username already exists")
        hashed_password=password_hash(request.password)
        new_user=User(username=request.username,password_hash=hashed_password)
        db.add(new_user)
        db.flush()
        token=create_access_token(new_user.id)
        await db.commit()
        return TokenResponse(access_token=token,token_type="bearer")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/api/login",response_model=TokenResponse)
async def login(request:LoginRequest,db:Annotated[AsyncSession,Depends(get_db)]):
    """Login a user and return a JWT token"""
    try:
        user=await db.execute(select(User).where(User.username==request.username))
        user=user.scalar_one_or_none()
        password_valid=verify_password(request.password,user.password_hash) if user else False
        if not user or not password_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")
        token=create_access_token(user.id)
        return TokenResponse(access_token=token,token_type="bearer")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    
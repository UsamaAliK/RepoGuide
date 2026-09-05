from datetime import datetime,timedelta,timezone
import jwt
import bcrypt
from sqlalchemy import select
from .config import settings
from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from typing import Annotated
from fastapi import FastAPI, HTTPException,Depends,status
from .models import User, Repository, Conversation, Message, MessageSource


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def passsword_hash(password:str)->str:
    """Hash a passsword using bcrypt"""
    salt=bcrypt.gensalt()
    hashed=bcrypt.hashpw(password.encode(),salt)
    return hashed.decode()

def verify_password(password:str,hashed:str)->bool:
    """Verify a password against a hashed value"""
    return bcrypt.checkpw(password.encode(),hashed.encode())

def create_access_token(user_id:int)->str:
    """Create  a JWT access token with an optional expiration time"""
    expires_at=datetime.now(timezone.utc)+timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    payload={
        "sub":str(user_id),
        "exp":expires_at
    }
    token=jwt.encode(payload,settings.JWT_SECRET,algorithm=settings.JWT_ALGORITHM)
    return token

async def current_user(token:Annotated[str,Depends(oauth2_scheme)],db:Annotated[AsyncSession,Depends(get_db)])->User:
    """Get the current user from the jwt token"""
    try:
        payload=jwt.decode(token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGORITHM])
        user_id=int(payload["sub"])
    except (jwt.ExpiredSignatureError,jwt.InvalidTokenError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token",
                            headers={"WWW-Authenticate":"Bearer"})
    user=await db.execute(select(User).where(User.id==user_id))
    user=user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found",
                            headers={"WWW-Authenticate":"Bearer"})
    return user





    


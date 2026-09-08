from datetime import datetime,timedelta,timezone
import jwt
import bcrypt
import hashlib
import secrets
from sqlalchemy import select
from .config import settings
from .models import User, RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .database import get_db
from typing import Annotated
from fastapi import FastAPI, HTTPException,Depends,status
from .models import User, Repository, Conversation, Message, MessageSource


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def password_hash(password:str)->str:
    """Hash a password using bcrypt"""
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

def hash_token(token:str)->str:
    """Hash a refresh token so the raw value is never stored in the DB"""
    return hashlib.sha256(token.encode()).hexdigest()

async def create_refresh_token(db: AsyncSession, user_id: int) -> str:
    """Generate a raw refresh token, store only its hash + expiry, return the raw token"""
    raw = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(
        user_id=user_id,
        token_hash=hash_token(raw),
        expires_at=expires_at,
    ))
    await db.flush()
    return raw

async def get_valid_refresh_token(db: AsyncSession, raw_token: str) -> RefreshToken:
    """Look up a refresh token, verifying it exists, is not revoked/expired, and belongs to a user"""
    token_hash = hash_token(raw_token)
    row = (await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )).scalar_one_or_none()
    if row is None or row.revoked or row.expires_at < datetime.now(timezone.utc):
        return None
    return row

async def current_user(token:Annotated[str,Depends(oauth2_scheme)],db:Annotated[AsyncSession,Depends(get_db)])->User:
    """Get the current user from the jwt token"""
    try:
        payload=jwt.decode(token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGORITHM])
        user_id=int(payload["sub"])
    except (jwt.ExpiredSignatureError,jwt.InvalidTokenError,ValueError,KeyError,TypeError):
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





    


from datetime import datetime, timedelta
from typing import Optional

import hashlib
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import database

security = HTTPBearer()
TOKENS: dict[str, int] = {}  # token -> user_id
TOKEN_EXPIRY: dict[str, datetime] = {}
TOKEN_TTL = timedelta(hours=12)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_token(user_id: int) -> str:
    token = secrets.token_hex(32)
    TOKENS[token] = user_id
    TOKEN_EXPIRY[token] = datetime.utcnow() + TOKEN_TTL
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials
    user_id = TOKENS.get(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    if TOKEN_EXPIRY[token] < datetime.utcnow():
        del TOKENS[token]
        del TOKEN_EXPIRY[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    return user_id

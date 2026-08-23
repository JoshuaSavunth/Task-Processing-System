from fastapi import APIRouter, HTTPException, status

from app import database
from app.auth import hash_password, create_token

router = APIRouter()


@router.post("/register")
def register(username: str, password: str) -> dict[str, str]:
    existing = database.get_user_by_username(username)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    password_hash = hash_password(password)
    user_id = database.create_user(username, password_hash)
    token = create_token(user_id)
    return {"token": token}


@router.post("/login")
def login(username: str, password: str) -> dict[str, str]:
    user = database.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    password_hash = hash_password(password)
    if user["password_hash"] != password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_token(user["id"])
    return {"token": token}

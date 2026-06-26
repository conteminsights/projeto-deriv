"""
ZeeK.Web — Auth Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, hash_password
from app.models.user import User

router = APIRouter()


@router.post("/register")
async def register(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Return JWT
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(days=7),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }


@router.post("/login")
async def login(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    """Login and return JWT token."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(days=7),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }

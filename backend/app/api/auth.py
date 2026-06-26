"""
ZeeK.Web — Auth Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, hash_password
from app.models.user import User

router = APIRouter()


@router.post("/register")
async def register(email: str, password: str, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # TODO: implementar
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/login")
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    """Login and return JWT token."""
    # TODO: implementar
    raise HTTPException(status_code=501, detail="Not implemented yet")

"""
ZeeK.Web — Token PAT Endpoints (CRUD criptografado)
"""
import base64
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Header
from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.token import DerivToken
from app.config import settings

router = APIRouter()


def _get_fernet() -> Fernet:
    """Derive a Fernet key from the app secret."""
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


@router.post("/")
async def create_token(
    token_value: str,
    label: str = "",
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Save an encrypted PAT token."""
    payload = decode_token(authorization.replace("Bearer ", "")) if authorization else None
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload["sub"])

    fernet = _get_fernet()
    token_encrypted = fernet.encrypt(token_value.encode()).decode()
    token_hash = hashlib.sha256(token_value.encode()).hexdigest()

    result = await db.execute(
        select(DerivToken).where(DerivToken.user_id == user_id, DerivToken.label == label)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.token_hash = token_hash
        existing.token_encrypted = token_encrypted
        existing.is_active = True
    else:
        new_token = DerivToken(
            user_id=user_id,
            token_hash=token_hash,
            token_encrypted=token_encrypted,
            label=label,
            is_active=True,
        )
        db.add(new_token)

    await db.commit()
    return {"message": "Token saved", "label": label}


@router.get("/")
async def list_tokens(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List saved tokens (without revealing the value)."""
    payload = decode_token(authorization.replace("Bearer ", "")) if authorization else None
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload["sub"])

    result = await db.execute(
        select(DerivToken).where(
            DerivToken.user_id == user_id, DerivToken.is_active == True
        )
    )
    tokens = result.scalars().all()
    return [
        {
            "id": t.id,
            "label": t.label,
            "last_used": t.last_used.isoformat() if t.last_used else None,
            "created_at": t.created_at.isoformat(),
        }
        for t in tokens
    ]


@router.delete("/{token_id}")
async def delete_token(
    token_id: int,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a saved token."""
    payload = decode_token(authorization.replace("Bearer ", "")) if authorization else None
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload["sub"])

    result = await db.execute(
        select(DerivToken).where(
            DerivToken.id == token_id, DerivToken.user_id == user_id
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    token.is_active = False
    await db.commit()
    return {"message": "Token deleted"}

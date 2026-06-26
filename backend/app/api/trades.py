"""
ZeeK.Web — Trade History Endpoints (stub for Fase 2)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_trades():
    """List trades (stub)."""
    return {"trades": [], "total": 0}

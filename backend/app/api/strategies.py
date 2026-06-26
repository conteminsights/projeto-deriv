"""
ZeeK.Web — Strategy Endpoints (stub for Fase 3)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_strategies():
    """List strategies (stub)."""
    return {"strategies": []}

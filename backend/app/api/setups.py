"""
ZeeK.Web — Setup Management Endpoints (stub for Fase 6)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_setups():
    """List setups (stub)."""
    return {"setups": []}

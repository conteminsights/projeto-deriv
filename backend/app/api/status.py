"""
ZeeK.Web — Status Endpoints (stub for Fase 2)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_status():
    """Return basic server status."""
    return {"status": "ok", "version": "1.0.0", "connected": False, "balance": None}

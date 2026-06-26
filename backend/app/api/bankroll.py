"""
ZeeK.Web — Bankroll Endpoints (stub for Fase 4)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_bankroll():
    """Get bankroll config (stub)."""
    return {"balance": 0, "initial_stake": 2.0, "martingale": False}

"""
ZeeK.Web — API Router (agrega todos os endpoints)
"""
from fastapi import APIRouter

from app.api import auth, tokens, status, strategies, bankroll, trades, setups, ws

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tokens.router, prefix="/tokens", tags=["tokens"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(bankroll.router, prefix="/bankroll", tags=["bankroll"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(setups.router, prefix="/setups", tags=["setups"])
api_router.include_router(ws.router, prefix="/ws", tags=["ws"])

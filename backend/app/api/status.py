"""
ZeeK.Web — Status Endpoints

Real-time connection status, balance, and market info from DerivWorker.
"""
from fastapi import APIRouter, Depends

from app.workers.deriv_worker import deriv_worker

router = APIRouter()


@router.get("/")
async def get_status():
    """Return current server and Deriv connection status."""
    return {
        "server": "ok",
        "version": "1.0.0",
        "deriv_connected": deriv_worker.connected,
        "balance": deriv_worker.balance,
        "active_symbols": list(deriv_worker.active_symbols),
        "latest_ticks": {
            sym: {"epoch": t.get("epoch"), "quote": t.get("quote")}
            for sym, t in deriv_worker.latest_ticks.items()
        },
    }

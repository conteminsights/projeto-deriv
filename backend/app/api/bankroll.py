"""
ZeeK.Web — Bankroll & Defense API Endpoints

Configuração e estado da banca, defesas, limites.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from app.core.security import decode_token
from app.services.bankroll import bankroll_manager, DefenseState

router = APIRouter()


# ─── Schemas ────────────────────────────────────────────────

class MartingaleSchema(BaseModel):
    enabled: bool = False
    multiplier: float = 2.0
    max_steps: int = 5


class MultiplierSchema(BaseModel):
    enabled: bool = False
    value: float = 2.0


class MiniMetaSchema(BaseModel):
    enabled: bool = False
    profit_target: float = 50.0
    max_entries: int = 0


class LimitsSchema(BaseModel):
    enabled: bool = False
    daily_loss_limit: float = 0.0
    daily_profit_target: float = 0.0
    session_loss_limit: float = 0.0
    consecutive_loss_limit: int = 0


class AutoReloadSchema(BaseModel):
    enabled: bool = False
    reload_after_minutes: int = 30
    reload_after_entries: int = 0


class DefenseConfigSchema(BaseModel):
    mode: str = "none"  # none, barrier, soros_master, soros_slave
    barrier: int = 3
    master_page_id: Optional[str] = None


class BankrollUpdateSchema(BaseModel):
    initial_stake: Optional[float] = None
    martingale: Optional[MartingaleSchema] = None
    multiplier: Optional[MultiplierSchema] = None
    mini_meta: Optional[MiniMetaSchema] = None
    limits: Optional[LimitsSchema] = None
    auto_reload: Optional[AutoReloadSchema] = None


# ─── Endpoints ──────────────────────────────────────────────

@router.get("/")
async def get_bankroll():
    """Get current bankroll config and state."""
    return {
        "config": bankroll_manager.config_dict,
        "state": bankroll_manager.state_dict,
    }


@router.put("/config")
async def update_bankroll(config: BankrollUpdateSchema):
    """Update bankroll configuration."""
    if config.initial_stake is not None:
        bankroll_manager.initial_stake = config.initial_stake
        bankroll_manager.current_stake = config.initial_stake
    if config.martingale is not None:
        bankroll_manager.martingale.enabled = config.martingale.enabled
        bankroll_manager.martingale.multiplier = config.martingale.multiplier
        bankroll_manager.martingale.max_steps = config.martingale.max_steps
    if config.multiplier is not None:
        bankroll_manager.multiplier.enabled = config.multiplier.enabled
        bankroll_manager.multiplier.value = config.multiplier.value
    if config.mini_meta is not None:
        bankroll_manager.mini_meta.enabled = config.mini_meta.enabled
        bankroll_manager.mini_meta.profit_target = config.mini_meta.profit_target
        bankroll_manager.mini_meta.max_entries = config.mini_meta.max_entries
    if config.limits is not None:
        bankroll_manager.limits.enabled = config.limits.enabled
        bankroll_manager.limits.daily_loss_limit = config.limits.daily_loss_limit
        bankroll_manager.limits.daily_profit_target = config.limits.daily_profit_target
        bankroll_manager.limits.session_loss_limit = config.limits.session_loss_limit
        bankroll_manager.limits.consecutive_loss_limit = config.limits.consecutive_loss_limit
    if config.auto_reload is not None:
        bankroll_manager.auto_reload.enabled = config.auto_reload.enabled
        bankroll_manager.auto_reload.reload_after_minutes = config.auto_reload.reload_after_minutes
        bankroll_manager.auto_reload.reload_after_entries = config.auto_reload.reload_after_entries

    return {"message": "Bankroll updated", "config": bankroll_manager.config_dict}


@router.get("/defense/{page_id}")
async def get_defense(page_id: str):
    """Get defense state for a page."""
    defense = bankroll_manager.get_defense(page_id)
    return {
        "page_id": page_id,
        "mode": defense.mode,
        "barrier": defense.barrier,
        "consecutive_losses": defense.consecutive_losses,
        "waiting_for_barrier": defense.waiting_for_barrier,
    }


@router.put("/defense/{page_id}")
async def update_defense(page_id: str, config: DefenseConfigSchema):
    """Update defense configuration for a page."""
    defense = bankroll_manager.get_defense(page_id)
    defense.mode = config.mode
    defense.barrier = config.barrier

    if config.mode == "soros_master" and config.master_page_id:
        bankroll_manager.add_soros_pair(page_id, config.master_page_id)

    return {"message": f"Defense for {page_id} updated", "mode": defense.mode}


@router.post("/soros/pair")
async def create_soros_pair(master_id: str, slave_id: str):
    """Create a MASTER/SLAVE pair."""
    bankroll_manager.add_soros_pair(master_id, slave_id)
    return {"message": f"Soros pair: {master_id} MASTER -> {slave_id} SLAVE"}


@router.post("/reset")
async def reset_session():
    """Reset session state."""
    bankroll_manager.reset_session()
    return {"message": "Session reset", "state": bankroll_manager.state_dict}


@router.post("/stop")
async def stop_trading():
    """Stop all trading."""
    bankroll_manager.stop()
    return {"message": "Trading stopped"}

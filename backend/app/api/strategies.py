"""
ZeeK.Web — Strategy CRUD Endpoints
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.setup import Setup
from app.schemas.strategy import StrategyCreate, StrategyUpdate
from app.services.page_manager import page_manager
from app.services.strategy_runner import strategy_runner
from app.services.bankroll import bankroll_manager

logger = logging.getLogger(__name__)

router = APIRouter()


async def _get_user(authorization: str | None) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(payload["sub"])


def _setup_to_response(s: Setup) -> dict:
    return {
        "id": s.id,
        "user_id": s.user_id,
        "name": s.name,
        "description": s.description or "",
        "is_builtin": s.is_builtin,
        "pages": json.loads(s.pages_data) if s.pages_data else [],
        "management": json.loads(s.management_data) if s.management_data else {},
        "created_at": s.created_at.isoformat() if s.created_at else "",
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


@router.get("/")
async def list_strategies(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all strategies for the authenticated user."""
    user_id = await _get_user(authorization)
    result = await db.execute(
        select(Setup).where(Setup.user_id == user_id).order_by(Setup.created_at.desc())
    )
    strategies = result.scalars().all()
    return [_setup_to_response(s) for s in strategies]


@router.post("/")
async def create_strategy(
    strategy: StrategyCreate,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trading strategy."""
    user_id = await _get_user(authorization)

    setup = Setup(
        user_id=user_id,
        name=strategy.name,
        description=strategy.description,
        is_builtin=False,
        pages_data=json.dumps([p.model_dump() for p in strategy.pages]),
        management_data=json.dumps(strategy.management.model_dump()),
    )
    db.add(setup)
    await db.commit()
    await db.refresh(setup)
    return _setup_to_response(setup)


@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: int,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific strategy."""
    user_id = await _get_user(authorization)
    result = await db.execute(
        select(Setup).where(Setup.id == strategy_id, Setup.user_id == user_id)
    )
    setup = result.scalar_one_or_none()
    if not setup:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return _setup_to_response(setup)


@router.put("/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    strategy: StrategyUpdate,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Update a strategy."""
    user_id = await _get_user(authorization)
    result = await db.execute(
        select(Setup).where(Setup.id == strategy_id, Setup.user_id == user_id)
    )
    setup = result.scalar_one_or_none()
    if not setup:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if strategy.name is not None:
        setup.name = strategy.name
    if strategy.description is not None:
        setup.description = strategy.description
    if strategy.pages is not None:
        setup.pages_data = json.dumps([p.model_dump() for p in strategy.pages])
    if strategy.management is not None:
        setup.management_data = json.dumps(strategy.management.model_dump())

    await db.commit()
    await db.refresh(setup)
    return _setup_to_response(setup)


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete a strategy."""
    user_id = await _get_user(authorization)
    result = await db.execute(
        select(Setup).where(Setup.id == strategy_id, Setup.user_id == user_id)
    )
    setup = result.scalar_one_or_none()
    if not setup:
        raise HTTPException(status_code=404, detail="Strategy not found")

    await db.delete(setup)
    await db.commit()
    return {"message": "Strategy deleted"}


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: int,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Load a strategy into the StrategyRunner and start operating."""
    user_id = await _get_user(authorization)
    result = await db.execute(
        select(Setup).where(Setup.id == strategy_id, Setup.user_id == user_id)
    )
    setup = result.scalar_one_or_none()
    if not setup:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy_runner.load_setup(
        pages_data=setup.pages_data or "[]",
        management_data=setup.management_data or "{}",
    )
    strategy_runner.start()

    # Sync bankroll config from management_data
    if setup.management_data:
        mgmt = json.loads(setup.management_data)
        bankroll_manager.initial_stake = mgmt.get("initial_stake", 2.0)
        bankroll_manager.current_stake = mgmt.get("initial_stake", 2.0)
        bankroll_manager.mini_meta.enabled = mgmt.get("mini_meta_enabled", False)
        bankroll_manager.mini_meta.profit_target = mgmt.get("mini_meta_target", 50.0)
        bankroll_manager.mini_meta.max_entries = mgmt.get("mini_meta_max_entries", 0)
        bankroll_manager.auto_reload.enabled = mgmt.get("auto_reload_enabled", False)
        bankroll_manager.auto_reload.reload_after_minutes = mgmt.get("auto_reload_minutes", 30)
        bankroll_manager.auto_reload.reload_after_entries = mgmt.get("auto_reload_entries", 0)
        bankroll_manager.limits.enabled = mgmt.get("limits_enabled", False)
        bankroll_manager.limits.daily_loss_limit = mgmt.get("daily_loss_limit", 0)
        bankroll_manager.limits.daily_profit_target = mgmt.get("daily_profit_target", 0)
        bankroll_manager.limits.session_loss_limit = mgmt.get("session_loss_limit", 0)
        bankroll_manager.limits.consecutive_loss_limit = mgmt.get("consecutive_loss_limit", 0)
        bankroll_manager.martingale.enabled = mgmt.get("martingale_enabled", False)
        bankroll_manager.martingale.multiplier = mgmt.get("martingale_multiplier", 2.0)
        bankroll_manager.martingale.max_steps = mgmt.get("martingale_max_steps", 5)
        bankroll_manager.multiplier.enabled = mgmt.get("multiplier_enabled", False)
        bankroll_manager.multiplier.value = mgmt.get("multiplier_value", 2.0)
        logger.info(f"Bankroll config synced from strategy '{setup.name}'")

    return {"message": f"Strategy '{setup.name}' activated", "active": True}


@router.post("/stop")
async def stop_strategy():
    """Stop the StrategyRunner."""
    await strategy_runner.stop()
    page_manager.stop_all()
    return {"message": "All strategies stopped", "active": False}

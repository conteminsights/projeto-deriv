"""
ZeeK.Web — Strategy CRUD Endpoints
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.setup import Setup
from app.schemas.strategy import StrategyCreate, StrategyUpdate
from app.services.page_manager import page_manager
from app.services.strategy_runner import strategy_runner

router = APIRouter()


def _get_user(authorization: str) -> int:
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
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all strategies for the authenticated user."""
    user_id = _get_user(authorization)
    result = await db.execute(
        select(Setup).where(Setup.user_id == user_id).order_by(Setup.created_at.desc())
    )
    strategies = result.scalars().all()
    return [_setup_to_response(s) for s in strategies]


@router.post("/")
async def create_strategy(
    strategy: StrategyCreate,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trading strategy."""
    user_id = _get_user(authorization)

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
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific strategy."""
    user_id = _get_user(authorization)
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
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Update a strategy."""
    user_id = _get_user(authorization)
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
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete a strategy."""
    user_id = _get_user(authorization)
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
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Load a strategy into the StrategyRunner and start operating."""
    user_id = _get_user(authorization)
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

    return {"message": f"Strategy '{setup.name}' activated", "active": True}


@router.post("/stop")
async def stop_strategy():
    """Stop the StrategyRunner."""
    await strategy_runner.stop()
    page_manager.stop_all()
    return {"message": "All strategies stopped", "active": False}

#!/usr/bin/env python3
"""
ZeeK.Web — Seed Data Script
Creates initial admin user and built-in setups.

Usage: python scripts/seed-data.py
"""
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import engine, async_session, Base
from app.core.security import hash_password
from app.models.setup import Setup


async def seed():
    print("🌱 Seeding database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create built-in setups (example)
    builtin_setups = [
        {
            "name": "SMA Cross",
            "description": "Estratégia básica: CALL quando preço cruza SMA 20 para cima",
            "is_builtin": True,
            "pages_data": json.dumps([
                {
                    "name": "Página 1",
                    "market": "R_100",
                    "mode": "CALL_PUT",
                    "rules": [
                        {
                            "condition": {"indicator": "price", "operator": "cross_above", "value": "sma_20"},
                            "contract_type": "CALL",
                            "duration": 1,
                            "duration_unit": "t"
                        }
                    ]
                }
            ]),
            "management_data": json.dumps({
                "initial_stake": 2.0,
                "martingale": {"enabled": True, "multiplier": 2.0, "max_steps": 5}
            })
        }
    ]

    async with async_session() as session:
        for setup_data in builtin_setups:
            setup = Setup(
                user_id=1,  # admin user
                name=setup_data["name"],
                description=setup_data["description"],
                is_builtin=setup_data["is_builtin"],
                pages_data=setup_data["pages_data"],
                management_data=setup_data["management_data"],
            )
            session.add(setup)

        await session.commit()

    print("✅ Seed concluído!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

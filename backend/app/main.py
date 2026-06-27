"""
ZeeK.Web — Main Application Entrypoint
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.core.database import engine, Base
from app.api.ws import manager
from app.workers.deriv_worker import deriv_worker
from app.services.order_manager import order_manager

logger = logging.getLogger(__name__)


async def broadcast_loop():
    """Periodically push ticks and balance to all connected WebSocket clients."""
    while True:
        try:
            await asyncio.sleep(0.3)  # ~3 updates per second

            if not manager.active_connections:
                continue

            # Broadcast latest ticks
            for symbol, tick in list(deriv_worker.latest_ticks.items()):
                await manager.broadcast({
                    "type": "tick",
                    "symbol": symbol,
                    "tick": tick,
                })

            # Broadcast balance on change
            if deriv_worker.balance:
                await manager.broadcast({
                    "type": "balance",
                    "balance": deriv_worker.balance,
                })

            # Broadcast connection status
            await manager.broadcast({
                "type": "deriv_status",
                "connected": deriv_worker.connected,
            })

            # Broadcast latest trade results
            if order_manager.trade_history:
                last_trade = order_manager.trade_history[-1]
                await manager.broadcast({
                    "type": "trade_result",
                    "contract": last_trade,
                })

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Broadcast error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    broadcast_task = asyncio.create_task(broadcast_loop())
    logger.info("Broadcast loop started")

    yield

    # Shutdown
    broadcast_task.cancel()
    await deriv_worker.stop()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

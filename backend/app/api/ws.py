"""
ZeeK.Web — WebSocket Handler (tempo real)

Connects frontend clients to the DerivWorker for real-time ticks,
balance updates, and contract status.
"""
import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.workers.deriv_worker import deriv_worker
from app.services.page_manager import page_manager
from app.services.strategy_runner import strategy_runner
from app.services.order_manager import order_manager
from app.services.bankroll import bankroll_manager

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections to frontend clients."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for c in dead:
            self.disconnect(c)


manager = ConnectionManager()


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time trading data."""
    # Validate JWT token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Missing token"})
        await websocket.close()
        return

    user = decode_token(token)
    if not user:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Invalid token"})
        await websocket.close()
        return

    await manager.connect(websocket)
    user_id = int(user["sub"])
    logger.info(f"WS client connected: user {user_id}")

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "subscribe_ticks":
                symbol = data.get("symbol", "R_100")
                ok = await deriv_worker.subscribe_market(symbol)
                await websocket.send_json({
                    "type": "subscribed",
                    "symbol": symbol,
                    "success": ok,
                })

            elif action == "unsubscribe_ticks":
                symbol = data.get("symbol")
                if symbol:
                    await deriv_worker.unsubscribe_market(symbol)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "symbol": symbol,
                    })

            elif action == "get_status":
                await websocket.send_json({
                    "type": "status",
                    "connected": deriv_worker.connected,
                    "balance": deriv_worker.balance,
                    "active_symbols": list(deriv_worker.active_symbols),
                })

            elif action == "get_tick":
                symbol = data.get("symbol", "R_100")
                tick = deriv_worker.latest_ticks.get(symbol)
                await websocket.send_json({
                    "type": "tick",
                    "symbol": symbol,
                    "tick": tick,
                })

            elif action == "get_tick_history":
                symbol = data.get("symbol", "R_100")
                history = list(deriv_worker.tick_history.get(symbol, []))
                await websocket.send_json({
                    "type": "tick_history",
                    "symbol": symbol,
                    "ticks": history,
                })

            elif action == "get_contracts":
                await websocket.send_json({
                    "type": "contracts",
                    "contracts": deriv_worker.contract_updates[-50:],
                })

            elif action == "connect_deriv":
                pat_token = data.get("pat_token", "").strip()
                if pat_token:
                    # Stop any existing connection
                    await deriv_worker.stop()
                    # Small delay before starting fresh
                    await asyncio.sleep(0.5)
                    await deriv_worker.start(pat_token)
                    await websocket.send_json({
                        "type": "deriv_connecting",
                        "message": "Connecting to Deriv...",
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "pat_token required",
                    })

            elif action == "disconnect_deriv":
                await deriv_worker.stop()
                await websocket.send_json({
                    "type": "deriv_disconnected",
                })

            elif action == "start_operating":
                page_id = data.get("page_id", "default")
                operating = page_manager.toggle_operation(page_id)
                if operating:
                    strategy_runner.start()
                await websocket.send_json({
                    "type": "operating_status",
                    "page_id": page_id,
                    "operating": operating,
                })

            elif action == "load_strategy":
                strategy_id = data.get("strategy_id")
                if not strategy_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "strategy_id required",
                    })
                    continue

                from app.core.database import async_session
                from app.models.setup import Setup
                from sqlalchemy import select

                async with async_session() as db:
                    result = await db.execute(
                        select(Setup).where(Setup.id == strategy_id)
                    )
                    setup = result.scalar_one_or_none()
                    if not setup:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Estratégia não encontrada",
                        })
                        continue

                    # Stop current runner and clear pages
                    await strategy_runner.stop()
                    page_manager.pages.clear()

                    # Load the new setup
                    strategy_runner.load_setup(
                        pages_data=setup.pages_data or "[]",
                        management_data=setup.management_data or "{}",
                    )

                    # Re-engage auto-reload from management config
                    if setup.management_data:
                        mgmt = json.loads(setup.management_data)
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

                    pages_count = len(json.loads(setup.pages_data or "[]"))
                    await websocket.send_json({
                        "type": "strategy_loaded",
                        "name": setup.name,
                        "pages_count": pages_count,
                    })
                    logger.info(f"Strategy loaded via WS: {setup.name} ({pages_count} pages)")

            elif action == "sell_contract":
                contract_id = data.get("contract_id", "")
                price = data.get("price", 0)
                if contract_id and price > 0:
                    result = await order_manager.sell_contract(contract_id, price)
                    await websocket.send_json({
                        "type": "sell_result",
                        "contract_id": contract_id,
                        "result": result,
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "contract_id and price required",
                    })

            elif action == "cancel_contract":
                contract_id = data.get("contract_id", "")
                if contract_id:
                    result = await order_manager.cancel_contract(contract_id)
                    await websocket.send_json({
                        "type": "cancel_result",
                        "contract_id": contract_id,
                        "result": result,
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "contract_id required",
                    })

            elif action == "get_accounts":
                await websocket.send_json({
                    "type": "accounts",
                    "accounts": deriv_worker.accounts,
                    "current_loginid": deriv_worker.current_loginid,
                })

            elif action == "switch_account":
                loginid = data.get("loginid", "")
                if loginid and deriv_worker.client and deriv_worker.client.ws:
                    # Switch by re-authorizing with the new loginid
                    token = deriv_worker.client.token or ""
                    resp = await deriv_worker.client.authorize(token)
                    new_loginid = resp.get("authorize", {}).get("loginid")
                    if new_loginid:
                        deriv_worker.current_loginid = new_loginid
                        # Re-subscribe balance for new account
                        await deriv_worker.client.subscribe_balance()
                    await websocket.send_json({
                        "type": "account_switched",
                        "loginid": new_loginid,
                        "accounts": deriv_worker.accounts,
                    })

            elif action == "stop_operating":
                page_manager.stop_all()
                await strategy_runner.stop()
                await websocket.send_json({
                    "type": "operating_status",
                    "operating": False,
                    "message": "All pages stopped",
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                })

    except WebSocketDisconnect:
        logger.info(f"WS client disconnected: user {user_id}")
    except Exception as e:
        logger.error(f"WS error: {e}")
    finally:
        manager.disconnect(websocket)

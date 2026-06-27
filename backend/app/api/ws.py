"""
ZeeK.Web — WebSocket Handler (tempo real)

Connects frontend clients to the DerivWorker for real-time ticks,
balance updates, and contract status.
"""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.workers.deriv_worker import deriv_worker
from app.services.page_manager import page_manager
from app.services.strategy_runner import strategy_runner
from app.services.order_manager import order_manager

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
                pat_token = data.get("pat_token", "")
                if pat_token:
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

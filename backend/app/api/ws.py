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

"""
ZeeK.Web — WebSocket Handler (tempo real)
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.security import decode_token

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time trading."""
    await websocket.accept()

    # Validate JWT token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.send_json({"type": "error", "message": "Missing token"})
        await websocket.close()
        return

    user = decode_token(token)
    if not user:
        await websocket.send_json({"type": "error", "message": "Invalid token"})
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "start_page":
                # TODO: iniciar operação na página
                pass
            elif action == "stop_page":
                # TODO: parar operação
                pass
            elif action == "subscribe_ticks":
                symbol = data.get("symbol")
                # TODO: inscrever em ticks
                pass
            elif action == "request_history":
                symbol = data.get("symbol")
                count = data.get("count", 500)
                # TODO: enviar ticks históricos
                pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})

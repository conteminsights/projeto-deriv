"""
ZeeK.Web — Deriv Client (WebSocket connection to Deriv API)

This is the core service that manages the WebSocket connection to the Deriv
trading platform. It handles authentication, tick subscriptions, proposals,
buy orders, and contract monitoring.
"""
import asyncio
import json
import logging
from typing import Callable, Coroutine

import websockets

logger = logging.getLogger(__name__)


class DerivClient:
    """
    Manages a single WebSocket connection to the Deriv API.
    
    Usage:
        client = DerivClient(app_id=1089)
        await client.connect()
        await client.authorize("your_pat_token")
        await client.subscribe_ticks("R_100")
        
        # Receive ticks via callback
        client.on_tick = lambda tick: print(tick)
        
        # Place an order
        proposal = await client.get_proposal({
            "contract_type": "CALL",
            "amount": 10,
            ...
        })
        result = await client.buy_contract(proposal["id"], proposal["ask_price"])
    """

    def __init__(self, app_id: int = 1089):
        self.app_id = app_id
        self.ws: websockets.WebSocketClientProtocol | None = None
        self.token: str | None = None
        self.authorized: bool = False
        self._request_id: int = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._running: bool = False

        # Callbacks (set by user)
        self.on_tick: Callable[[dict], Coroutine] | None = None
        self.on_balance: Callable[[dict], Coroutine] | None = None
        self.on_transaction: Callable[[dict], Coroutine] | None = None
        self.on_contract: Callable[[dict], Coroutine] | None = None
        self.on_error: Callable[[dict], Coroutine] | None = None

    async def connect(self):
        """Open WebSocket connection to Deriv."""
        url = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"
        self.ws = await websockets.connect(url)
        self._running = True
        asyncio.create_task(self._message_loop())
        logger.info("Connected to Deriv")

    async def disconnect(self):
        """Close WebSocket connection."""
        self._running = False
        if self.ws:
            await self.ws.close()
            self.ws = None
        logger.info("Disconnected from Deriv")

    async def authorize(self, token: str) -> dict:
        """Authenticate with PAT token."""
        self.token = token
        response = await self._send_and_wait({"authorize": token})
        if "error" in response:
            raise Exception(f"Authorization failed: {response['error']}")
        self.authorized = True
        logger.info("Authorized with Deriv")
        return response

    async def subscribe_ticks(self, symbol: str) -> str:
        """Subscribe to tick stream for a symbol."""
        response = await self._send_and_wait({
            "subscribe": 1, "ticks": symbol
        })
        sub_id = response.get("subscription", {}).get("id")
        logger.info(f"Subscribed to ticks: {symbol}")
        return sub_id

    async def subscribe_balance(self):
        """Subscribe to balance updates."""
        return await self._send_and_wait({
            "subscribe": 1, "balance": 1
        })

    async def subscribe_transactions(self):
        """Subscribe to transaction notifications."""
        return await self._send_and_wait({
            "subscribe": 1, "transaction": 1
        })

    async def get_proposal(self, params: dict) -> dict:
        """Get a price proposal for a contract."""
        msg = {"proposal": 1, **params}
        return await self._send_and_wait(msg)

    async def buy_contract(self, proposal_id: str, price: float) -> dict:
        """Buy a contract at the proposed price."""
        msg = {"buy": proposal_id, "price": price}
        return await self._send_and_wait(msg)

    async def forget(self, sub_id: str):
        """Unsubscribe from a stream."""
        return await self._send_and_wait({"forget": sub_id})

    async def _send_and_wait(self, msg: dict, timeout: float = 15.0) -> dict:
        """Send message and wait for response."""
        self._request_id += 1
        req_id = self._request_id
        msg["req_id"] = req_id

        future = asyncio.get_event_loop().create_future()
        self._pending[req_id] = future

        await self.ws.send(json.dumps(msg))
        return await asyncio.wait_for(future, timeout)

    async def _message_loop(self):
        """Main message receiving loop."""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._process_message(data)
        except websockets.ConnectionClosed:
            logger.warning("Deriv WebSocket connection closed")
        finally:
            self._running = False

    async def _process_message(self, data: dict):
        """Process incoming message from Deriv."""
        # Check if it's a response to a pending request
        req_id = data.get("req_id")
        if req_id and req_id in self._pending:
            self._pending[req_id].set_result(data)
            del self._pending[req_id]
            return

        # Stream updates
        if "ticks" in data:
            if self.on_tick:
                await self.on_tick(data["ticks"])
        elif "balance" in data:
            if self.on_balance:
                await self.on_balance(data["balance"])
        elif "transaction" in data:
            if self.on_transaction:
                await self.on_transaction(data["transaction"])
        elif "proposal_open_contract" in data:
            if self.on_contract:
                await self.on_contract(data["proposal_open_contract"])
        elif "error" in data:
            if self.on_error:
                await self.on_error(data["error"])
            logger.error(f"Deriv error: {data['error']}")

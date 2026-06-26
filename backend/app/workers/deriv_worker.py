"""
ZeeK.Web — Deriv Worker (Background Connection Manager)

Manages the DerivClient lifecycle: connect, authorize, reconnect on failure,
and expose current state (ticks, balance, connection status) to the rest of the app.
"""
import asyncio
import logging
from typing import Optional

from app.services.deriv_client import DerivClient

logger = logging.getLogger(__name__)


class DerivWorker:
    """Singleton background worker that owns the Deriv WebSocket connection."""

    def __init__(self):
        self.client: Optional[DerivClient] = None
        self._task: Optional[asyncio.Task] = None
        self._token: Optional[str] = None

        # Current state
        self.connected: bool = False
        self.balance: Optional[dict] = None
        self.active_symbols: set[str] = set()
        self.latest_ticks: dict[str, dict] = {}  # symbol -> last tick
        self.contract_updates: list[dict] = []

    async def start(self, token: str):
        """Start the worker with a PAT token. Connects and authorizes."""
        self._token = token
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        """Stop the worker and disconnect."""
        if self._task:
            self._task.cancel()
            self._task = None
        if self.client:
            await self.client.disconnect()
            self.client = None
        self.connected = False

    async def _run(self):
        """Main loop: connect, authorize, keep alive."""
        while True:
            try:
                self.client = DerivClient(app_id=24332)

                # Wire callbacks
                self.client.on_tick = self._on_tick
                self.client.on_balance = self._on_balance
                self.client.on_transaction = self._on_transaction
                self.client.on_contract = self._on_contract
                self.client.on_error = self._on_error

                await self.client.connect()
                await self.client.authorize(self._token)
                await self.client.subscribe_balance()
                self.connected = True
                logger.info("DerivWorker: connected and authorized")

                # Re-subscribe to any active symbols
                for symbol in list(self.active_symbols):
                    await self.client.subscribe_ticks(symbol)

                # Keep running — _message_loop keeps the connection alive
                while self.client and self.client._running:
                    await asyncio.sleep(1)

            except asyncio.CancelledError:
                logger.info("DerivWorker: cancelled")
                break
            except Exception as e:
                logger.error(f"DerivWorker: error {e}, reconnecting in 5s")
                self.connected = False
                if self.client:
                    await self.client.disconnect()
                await asyncio.sleep(5)

    async def subscribe_market(self, symbol: str) -> bool:
        """Subscribe to a market's tick stream."""
        if symbol in self.active_symbols:
            return True
        self.active_symbols.add(symbol)
        if self.client and self.connected:
            try:
                await self.client.subscribe_ticks(symbol)
                return True
            except Exception:
                self.active_symbols.discard(symbol)
                return False
        return True  # will subscribe when connected

    async def unsubscribe_market(self, symbol: str):
        """Unsubscribe from a market."""
        self.active_symbols.discard(symbol)
        if self.client and self.connected:
            try:
                await self.client.forget(symbol)
            except Exception:
                pass

    async def _on_tick(self, tick: dict):
        symbol = tick.get("symbol")
        if symbol:
            self.latest_ticks[symbol] = tick

    async def _on_balance(self, balance: dict):
        self.balance = balance

    async def _on_transaction(self, transaction: dict):
        logger.info(f"Transaction: {transaction}")

    async def _on_contract(self, contract: dict):
        self.contract_updates.append(contract)

    async def _on_error(self, error: dict):
        logger.error(f"Deriv error: {error}")


# Global singleton
deriv_worker = DerivWorker()

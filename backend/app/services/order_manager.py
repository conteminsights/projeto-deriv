"""
ZeeK.Web — Order Manager

Manages buy/sell order execution via the Deriv API.
Handles proposal requests, buy execution, and contract monitoring.
"""
import asyncio
import logging
from typing import Optional, Callable

from app.workers.deriv_worker import deriv_worker

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Executes trades through the connected DerivClient.
    Manages proposal requests, buy/sell, and tracks active contracts.
    """

    def __init__(self):
        self.active_contracts: dict[str, dict] = {}  # contract_id -> info
        self.trade_history: list[dict] = []
        self._on_trade_callback: Optional[Callable] = None

    def on_trade(self, callback: Callable):
        """Register callback for completed trades."""
        self._on_trade_callback = callback

    async def place_order(
        self,
        symbol: str,
        contract_type: str,
        stake: float,
        duration: int = 1,
        duration_unit: str = "t",
        multiplier: int = 0,
        barrier: int = 0,
    ) -> Optional[dict]:
        """
        Place a trade order.
        Supports CALL/PUT, MULTIPLIER (MULTUP/MULTDOWN), and DIGIT (DIGITODD/DIGITEVEN/DIGITOVER/DIGITUNDER) contract types.
        Returns the contract result dict or None on failure.
        """
        client = deriv_worker.client
        if not client or not deriv_worker.connected:
            logger.warning("Cannot place order: Deriv not connected")
            return None

        try:
            # Build proposal params based on contract type
            params = {
                "contract_type": contract_type,
                "amount": stake,
                "basis": "stake",
                "duration": duration,
                "duration_unit": duration_unit,
                "symbol": symbol,
                "currency": "USD",
            }

            # Add multiplier-specific params
            if multiplier > 0:
                params["multiplier"] = multiplier

            # Add barrier for DIGITOVER/DIGITUNDER
            if contract_type in ("DIGITOVER", "DIGITUNDER") and barrier > 0:
                params["barrier"] = barrier

            # 1. Get proposal
            proposal = await client.get_proposal(params)

            if "error" in proposal:
                logger.error(f"Proposal error: {proposal['error']}")
                return None

            proposal_id = proposal.get("proposal", {}).get("id")
            ask_price = proposal.get("proposal", {}).get("ask_price")
            if not proposal_id or ask_price is None:
                return None

            # 2. Buy
            buy_result = await client.buy_contract(proposal_id, ask_price)

            if "error" in buy_result:
                logger.error(f"Buy error: {buy_result['error']}")
                return None

            contract_id = buy_result.get("buy", {}).get("contract_id")
            if contract_id:
                self.active_contracts[contract_id] = {
                    "contract_id": contract_id,
                    "symbol": symbol,
                    "contract_type": contract_type,
                    "stake": stake,
                    "buy_price": ask_price,
                    "status": "open",
                }

            logger.info(f"Order placed: {contract_type} {symbol} @ {ask_price}")
            return buy_result

        except Exception as e:
            logger.error(f"Order failed: {e}")
            return None

    async def monitor_contract(self, contract_id: str, poll_interval: float = 1.0, timeout: float = 300.0) -> Optional[dict]:
        """Monitor a contract until it settles, polling periodically."""
        client = deriv_worker.client
        if not client:
            return None

        import time
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                msg = {"proposal_open_contract": 1, "contract_id": contract_id}
                response = await client._send_and_wait(msg, timeout=10)

                contract = response.get("proposal_open_contract", {})
                status = contract.get("status")

                if status == "open":
                    await asyncio.sleep(poll_interval)
                    continue

                if status in ("won", "lost"):
                    profit = contract.get("profit", 0)
                    self._settle_contract(contract_id, status, profit)
                    return contract

                # Unknown status, keep waiting
                await asyncio.sleep(poll_interval)

            except asyncio.TimeoutError:
                logger.warning(f"Monitor timeout for {contract_id}, retrying...")
                continue
            except Exception as e:
                logger.error(f"Monitor error for {contract_id}: {e}")
                return None

        logger.warning(f"Monitor timeout after {timeout}s for {contract_id}")
        return None

    def _settle_contract(self, contract_id: str, status: str, profit: float):
        """Mark a contract as settled."""
        if contract_id in self.active_contracts:
            contract = self.active_contracts[contract_id]
            contract["status"] = status
            contract["profit"] = profit
            self.trade_history.append(contract)
            del self.active_contracts[contract_id]

            if self._on_trade_callback:
                self._on_trade_callback(contract)

    @property
    def total_profit(self) -> float:
        return sum(t.get("profit", 0) for t in self.trade_history)

    @property
    def open_count(self) -> int:
        return len(self.active_contracts)

    async def sell_contract(self, contract_id: str, price: float) -> Optional[dict]:
        """Sell an active contract before expiry."""
        client = deriv_worker.client
        if not client:
            return None
        try:
            result = await client.sell_contract(contract_id, price)
            if "error" not in result:
                self._settle_contract(contract_id, "sold", price)
            return result
        except Exception as e:
            logger.error(f"Sell error: {e}")
            return None

    async def cancel_contract(self, contract_id: str) -> Optional[dict]:
        """Cancel a contract."""
        client = deriv_worker.client
        if not client:
            return None
        try:
            return await client.cancel_contract(contract_id)
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return None


# Global singleton
order_manager = OrderManager()

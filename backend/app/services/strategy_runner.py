"""
ZeeK.Web — Strategy Runner

Connects the tick stream from DerivWorker to the StrategyEngine,
evaluates rules on each tick, and executes orders via OrderManager.
"""
import asyncio
import json
import logging
from typing import Optional

from app.services.strategy_engine import StrategyEngine, TriggerCondition, Rule
from app.services.order_manager import order_manager
from app.services.page_manager import page_manager
from app.services.bankroll import bankroll_manager, DefenseState
from app.workers.deriv_worker import deriv_worker

logger = logging.getLogger(__name__)


class StrategyRunner:
    """
    Runs continuously: on each new tick, evaluates all active pages'
    strategies and executes matching orders.
    """

    def __init__(self):
        self.engine = StrategyEngine()
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Track last evaluated tick per symbol to avoid re-evaluation
        self._last_eval: dict[str, float] = {}

    def load_setup(self, pages_data: str, management_data: str):
        """Load a setup configuration into the engine."""
        import json

        pages = json.loads(pages_data) if pages_data else []
        management = json.loads(management_data) if management_data else {}

        for page_data in pages:
            page_id = f"page_{id(page_data)}"
            rules = []
            for r in page_data.get("rules", []):
                cond = r.get("condition", {})
                condition = TriggerCondition(
                    indicator=cond.get("indicator", "price"),
                    operator=cond.get("operator", ">"),
                    value=cond.get("value", 0),
                    timeframe=cond.get("timeframe", 14),
                )
                rule = Rule(
                    condition=condition,
                    contract_type=r.get("contract_type", "CALL"),
                    duration=r.get("duration", 1),
                    duration_unit=r.get("duration_unit", "t"),
                )
                rules.append(rule)

            mode = page_data.get("mode", "AND")
            market = page_data.get("market", "R_100")
            page_manager.add_page(page_id, page_data.get("name", "Página 1"), market)
            self.engine.add_page(page_id, rules, mode)

    def start(self):
        """Start the evaluation loop in the background."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("StrategyRunner started")

    async def stop(self):
        """Stop the evaluation loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("StrategyRunner stopped")

    async def _run(self):
        """Main evaluation loop."""
        while self._running:
            try:
                # Check each active page
                for page_id, page in list(page_manager.pages.items()):
                    if not page.operating:
                        continue

                    symbol = page.market
                    prices = self._get_prices(symbol)
                    if len(prices) < 2:
                        continue

                    # Check if we already evaluated this tick
                    last_tick = deriv_worker.latest_ticks.get(symbol, {}).get("epoch")
                    last_eval = self._last_eval.get(symbol)
                    if last_tick is not None and last_tick == last_eval:
                        continue
                    self._last_eval[symbol] = last_tick

                    # Evaluate strategy
                    action = self.engine.evaluate(page_id, prices)
                    if action:
                        logger.info(
                            f"Signal triggered: {page.name} "
                            f"-> {action['contract_type']}"
                        )
                        await self._execute_action(page, action)

                await asyncio.sleep(0.2)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"StrategyRunner error: {e}")
                await asyncio.sleep(1)

    def _get_prices(self, symbol: str) -> list:
        """Extract price history from tick buffer for indicator calculation."""
        history = deriv_worker.tick_history.get(symbol)
        if not history or len(history) < 2:
            tick = deriv_worker.latest_ticks.get(symbol)
            if tick and "quote" in tick:
                return [tick["quote"]]
            return []
        return [t["quote"] for t in history if t.get("quote") is not None]

    async def _execute_action(self, page, action: dict):
        """Execute a trading signal: proposal -> buy -> monitor -> result -> bankroll."""
        stake = bankroll_manager.current_stake

        # Check defense before placing order
        defense = bankroll_manager.get_defense(page.id)
        if not defense.should_operate():
            logger.info(f"{page.name}: defesa bloqueou operação")
            return

        # Check limits
        if bankroll_manager.check_limits():
            logger.warning(f"{page.name}: limites globais excedidos, parando")
            await self.stop()
            return

        # 1. Place order (proposal + buy)
        result = await order_manager.place_order(
            symbol=page.market,
            contract_type=action["contract_type"],
            stake=stake,
        )
        if not result or "error" in result:
            logger.warning(f"{page.name}: ordem falhou")
            return

        contract_id = result.get("buy", {}).get("contract_id")
        if not contract_id:
            return

        page.active_contract_id = contract_id
        logger.info(f"{page.name}: ordem executada #{contract_id}")

        # 2. Monitor contract until settlement
        buy_price = result.get("buy", {}).get("buy_price", stake)
        contract = await order_manager.monitor_contract(contract_id)
        if not contract:
            logger.warning(f"{page.name}: falha ao monitorar contrato")
            return

        # 3. Determine result
        status = contract.get("status")
        is_won = status == "won"
        profit = contract.get("profit", 0)

        if is_won:
            profit_pct = (profit / buy_price) * 100
        else:
            profit_pct = ((profit - buy_price) / buy_price) * 100

        logger.info(f"{page.name}: contrato {status}, profit={profit:.2f}")

        # 4. Update bankroll
        bankroll_manager.record_trade_result(profit)
        bankroll_manager.calculate_next_stake(is_won)

        # 5. Update page stats
        page_manager.record_trade(page.id, profit)
        defense.on_win() if is_won else defense.on_loss()

        # 6. Notify Soros pairs if MASTER
        bankroll_manager.notify_master_result(page.id, is_won)

        # 7. Check mini-meta
        if bankroll_manager.check_mini_meta():
            logger.info(f"{page.name}: mini-meta atingida, parando")
            await self.stop()

        # 8. Check auto-reload
        bankroll_manager.check_auto_reload()


# Global singleton
strategy_runner = StrategyRunner()

"""
ZeeK.Web — Strategy Engine

Avalia regras CUSTOM a cada tick e decide se deve enviar ordens.
"""
from typing import List, Optional
from app.services.indicators import sma, ema, rsi, bollinger_bands, macd


class TriggerCondition:
    """A single trigger condition in a CUSTOM rule."""

    def __init__(self, indicator: str, operator: str, value, timeframe: int = 1):
        self.indicator = indicator
        self.operator = operator
        self.value = value
        self.timeframe = timeframe

    def evaluate(self, prices: List[float]) -> bool:
        """Evaluate this condition against current price data."""
        if len(prices) < 2:
            return False

        current_price = prices[-1]
        indicator_value = self._get_indicator_value(prices)

        if indicator_value is None:
            return False

        # Operators
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
        }

        op_func = ops.get(self.operator)
        if op_func:
            return op_func(current_price, indicator_value)

        # Cross operators
        if self.operator == "cross_above" and len(prices) >= 3:
            return prices[-2] <= indicator_value and current_price > indicator_value
        if self.operator == "cross_below" and len(prices) >= 3:
            return prices[-2] >= indicator_value and current_price < indicator_value

        return False

    def _get_indicator_value(self, prices: List[float]) -> Optional[float]:
        """Calculate the indicator value for comparison."""
        if self.indicator == "price":
            return prices[-1]
        elif self.indicator == "sma":
            vals = sma(prices, self.timeframe)
            return vals[-1] if vals else None
        elif self.indicator == "ema":
            vals = ema(prices, self.timeframe)
            return vals[-1] if vals else None
        elif self.indicator == "rsi":
            vals = rsi(prices, self.timeframe)
            return vals[-1] if vals else None
        return None


class Rule:
    """A complete CUSTOM rule."""

    def __init__(self, condition: TriggerCondition, contract_type: str,
                 duration: int = 1, duration_unit: str = "t",
                 multiplier: int = 0):
        self.condition = condition
        self.contract_type = contract_type
        self.duration = duration
        self.duration_unit = duration_unit
        self.multiplier = multiplier  # > 0 for MULTIPLIER mode

    def evaluate(self, prices: List[float]) -> Optional[dict]:
        """Returns action dict if condition met, None otherwise."""
        if self.condition.evaluate(prices):
            return {
                "contract_type": self.contract_type,
                "duration": self.duration,
                "duration_unit": self.duration_unit,
                "multiplier": self.multiplier,
            }
        return None


class StrategyEngine:
    """
    Evaluates all rules for all pages on every tick.
    """

    def __init__(self):
        self.pages: dict = {}

    def add_page(self, page_id: str, rules: List[Rule], mode: str = "AND"):
        """Register a page with its rules."""
        self.pages[page_id] = {"rules": rules, "mode": mode}

    def evaluate(self, page_id: str, prices: List[float]) -> Optional[dict]:
        """Evaluate all rules for a page. Returns action dict or None."""
        page = self.pages.get(page_id)
        if not page:
            return None

        results = []
        for rule in page["rules"]:
            signal = rule.evaluate(prices)
            results.append(signal)

        if page["mode"] == "AND":
            if all(r is not None for r in results):
                action = results[0]
                # Ensure multiplier is set from the first matching rule
                return action
            return None
        else:  # OR
            for rule, signal in zip(page["rules"], results):
                if signal:
                    return signal
            return None

"""
ZeeK.Web — Technical Indicators

Reimplementação dos indicadores usados no ZeeK.Bot original:
SMA, EMA, RSI, MACD, Bollinger Bands
"""
import statistics
import math
from typing import List, Optional, Tuple


def sma(values: List[float], period: int) -> List[Optional[float]]:
    """Simple Moving Average."""
    result: List[Optional[float]] = []
    for i in range(len(values)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(values[i - period + 1:i + 1]) / period)
    return result


def ema(values: List[float], period: int) -> List[Optional[float]]:
    """Exponential Moving Average."""
    k = 2 / (period + 1)
    result: List[Optional[float]] = []
    ema_prev: Optional[float] = None

    for i, price in enumerate(values):
        if ema_prev is None:
            ema_prev = price
            result.append(None if i < period - 1 else price)
        else:
            ema_val = price * k + ema_prev * (1 - k)
            ema_prev = ema_val
            result.append(ema_val if i >= period - 1 else None)

    return result


def rsi(values: List[float], period: int = 14) -> List[Optional[float]]:
    """Relative Strength Index."""
    if len(values) < period + 1:
        return [None] * len(values)

    gains, losses = [], []
    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    result: List[Optional[float]] = [None] * period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        if avg_loss == 0:
            rs = float('inf')
        else:
            rs = avg_gain / avg_loss
        result.append(100 - (100 / (1 + rs)))

        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    return result


def bollinger_bands(
    values: List[float],
    period: int = 20,
    deviation: float = 2.0
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """Bollinger Bands (middle, upper, lower)."""
    middle = sma(values, period)
    upper: List[Optional[float]] = []
    lower: List[Optional[float]] = []

    for i in range(len(values)):
        if middle[i] is None:
            upper.append(None)
            lower.append(None)
        else:
            window = values[max(0, i - period + 1):i + 1]
            std = statistics.stdev(window) if len(window) > 1 else 0
            upper.append(middle[i] + deviation * std)
            lower.append(middle[i] - deviation * std)

    return middle, upper, lower


def macd(
    values: List[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """MACD (MACD line, Signal line, Histogram)."""
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)

    macd_line: List[Optional[float]] = []
    for i in range(len(values)):
        if ema_fast[i] is None or ema_slow[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(ema_fast[i] - ema_slow[i])

    # Calculate signal line (EMA of MACD line)
    macd_values = [v for v in macd_line if v is not None]
    signal_ema = ema(macd_values, signal)

    # Rebuild signal line with None padding
    signal_line: List[Optional[float]] = []
    none_count = len(macd_line) - len(macd_values)
    for _ in range(none_count):
        signal_line.append(None)
    signal_line.extend(signal_ema)

    # Histogram
    histogram: List[Optional[float]] = []
    for i in range(len(macd_line)):
        if macd_line[i] is None or signal_line[i] is None:
            histogram.append(None)
        else:
            histogram.append(macd_line[i] - signal_line[i])

    return macd_line, signal_line, histogram

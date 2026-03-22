"""Historical prices for modeling charts (yfinance). Falls back gracefully on failure."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def load_adjusted_close_matrix(
    symbols: list[str],
    lookback_days: int,
    *,
    max_tickers: int = 10,
    min_rows: int = 5,
) -> tuple[np.ndarray, list[str]] | None:
    """
    Download daily adjusted close prices aligned on common trading days.

    Returns ``(prices, symbols_kept)`` with ``prices`` shape ``(T, K)``, or ``None``
    if yfinance is unavailable or no usable data (callers should use synthetic paths).
    """
    try:
        import yfinance as yf  # type: ignore[import-untyped]
    except ImportError:
        logger.debug("yfinance not installed")
        return None

    syms = [s.strip().upper() for s in symbols[:max_tickers] if s and str(s).strip()]
    if not syms:
        return None

    period_days = int(min(max(lookback_days + 20, 30), 730))

    import pandas as pd

    cols = []
    kept: list[str] = []
    for sym in syms:
        try:
            h = yf.Ticker(sym).history(period=f"{period_days}d", auto_adjust=True, actions=False)
        except Exception as e:
            logger.debug("yfinance history failed for %s: %s", sym, e)
            continue
        if h is None or h.empty or "Close" not in h.columns:
            continue
        s = h["Close"].astype(float).dropna()
        if len(s) < min_rows:
            continue
        cols.append(s.rename(sym))
        kept.append(sym)

    if len(cols) < 1:
        return None

    merged = pd.concat(cols, axis=1, join="inner").dropna(how="any")
    if merged.empty or len(merged) < min_rows:
        return None

    merged = merged.iloc[-lookback_days:]
    if len(merged) < min_rows:
        return None

    return merged.values.astype(np.float64), kept

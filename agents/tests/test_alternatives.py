"""
Unit tests for alternatives_agent pure logic functions.
Tests do NOT call CoinGecko or Finnhub -- all external I/O is excluded.
"""
import pandas as pd
import pytest

from agents.alternatives_agent import compute_cross_correlations, trend_signal


class TestTrendSignal:
    def test_bullish_above_threshold(self):
        assert trend_signal(5.2) == "bullish"

    def test_bullish_at_boundary(self):
        assert trend_signal(3.1) == "bullish"

    def test_bearish_below_threshold(self):
        assert trend_signal(-4.1) == "bearish"

    def test_bearish_at_boundary(self):
        assert trend_signal(-3.1) == "bearish"

    def test_neutral_positive(self):
        assert trend_signal(1.5) == "neutral"

    def test_neutral_negative(self):
        assert trend_signal(-1.5) == "neutral"

    def test_neutral_zero(self):
        assert trend_signal(0.0) == "neutral"

    def test_neutral_at_upper_boundary(self):
        # Exactly 3.0 is NOT bullish (must be > 3.0)
        assert trend_signal(3.0) == "neutral"

    def test_neutral_at_lower_boundary(self):
        # Exactly -3.0 is NOT bearish (must be < -3.0)
        assert trend_signal(-3.0) == "neutral"


class TestComputeCrossCorrelations:
    def _make_returns(self, values: list) -> pd.Series:
        return pd.Series(values)

    def test_returns_dict(self):
        alt_prices = {
            "BTC": [100, 102, 105, 103, 107],
            "ETH": [50, 51, 52, 51, 53],
        }
        equity = self._make_returns([0.01, 0.02, -0.01, 0.015, 0.02])
        result = compute_cross_correlations(alt_prices, equity)
        assert isinstance(result, dict)

    def test_correlation_values_in_range(self):
        alt_prices = {
            "BTC": [100, 102, 105, 103, 107, 109, 108, 110, 112, 115],
            "ETH": [50, 51, 52, 51, 53, 54, 53, 55, 56, 58],
        }
        equity = self._make_returns([0.01, 0.02, -0.01, 0.015, 0.02, 0.01, -0.005, 0.03, 0.01, 0.025])
        result = compute_cross_correlations(alt_prices, equity)
        for key, val in result.items():
            assert -1.0 <= val <= 1.0, f"{key} correlation {val} out of range"

    def test_correlation_rounded_to_4_decimals(self):
        alt_prices = {
            "BTC": [100, 102, 105, 103, 107, 109, 108, 110, 112, 115],
        }
        equity = self._make_returns([0.01, 0.02, -0.01, 0.015, 0.02, 0.01, -0.005, 0.03, 0.01, 0.025])
        result = compute_cross_correlations(alt_prices, equity)
        for val in result.values():
            # Round-trip check: round to 4 places should not change value
            assert round(val, 4) == val

    def test_handles_empty_alt_prices(self):
        equity = self._make_returns([0.01, 0.02, -0.01])
        result = compute_cross_correlations({}, equity)
        assert result == {}

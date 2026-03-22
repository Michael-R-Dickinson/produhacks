"""Unit tests: chart edge cases + determinism (via registry)."""

import pytest

from agents.modeling_charts import run_registered_charts
from .helpers import assert_valid_png_base64


def _one(key: str, holdings: list[str], lookback: int, *, mock: bool = True):
    charts = run_registered_charts(holdings, [key], lookback, mock=mock)
    assert len(charts) == 1
    return charts[0]


@pytest.mark.parametrize("lookback", [0, 1, 2, 30, 365, 400])
def test_regression_handles_lookback_edges(lookback: int):
    c = _one("regression", ["A"], lookback, mock=True)
    assert c.chart_type == "regression"
    assert_valid_png_base64(c.image_base64)


@pytest.mark.parametrize("lookback", [0, 1, 5, 180, 500])
def test_volatility_cone_handles_lookback_edges(lookback: int):
    c = _one("volatility_cone", [], lookback, mock=True)
    assert c.chart_type == "volatility_cone"
    assert_valid_png_base64(c.image_base64)


@pytest.mark.parametrize("lookback", [0, 1, 2, 50])
def test_price_history_handles_lookback_edges(lookback: int):
    c = _one("price_history", ["X"], lookback, mock=True)
    assert c.chart_type == "price_history"
    assert_valid_png_base64(c.image_base64)


@pytest.mark.parametrize("holdings", [[], ["ONLY"], ["A", "B", "C", "D", "E", "F", "G"]])
def test_price_history_holdings_empty_or_many(holdings: list[str]):
    c = _one("price_history", holdings, 100, mock=True)
    assert "Overlay" in c.summary


def test_correlation_matrix_single_holding_uses_padding_labels():
    c = _one("correlation_matrix", ["SOLO"], 365, mock=True)
    assert "2" in c.summary and "correlation" in c.summary.lower()


def test_sector_performance_deterministic_for_same_holdings():
    a = _one("sector_performance", ["AAPL", "MSFT"], 365, mock=True)
    b = _one("sector_performance", ["AAPL", "MSFT"], 365, mock=True)
    assert a.image_base64 == b.image_base64
    assert a.summary == b.summary


def test_regression_mock_mode_is_deterministic():
    a = _one("regression", ["X", "Y"], 100, mock=True)
    b = _one("regression", ["X", "Y"], 100, mock=True)
    assert a.image_base64 == b.image_base64


def test_regression_non_mock_differs_from_mock_rng():
    a = _one("regression", ["X", "Y"], 100, mock=True)
    b = _one("regression", ["X", "Y"], 100, mock=False)
    assert a.image_base64 != b.image_base64

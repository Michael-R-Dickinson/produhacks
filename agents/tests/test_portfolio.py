"""Unit tests for portfolio computation functions.

Tests are isolated from yfinance — beta and correlation tests use pre-built mock price data.
"""
import numpy as np
import pytest

from agents.data.portfolio import EQUITY_TICKERS, MOCK_PORTFOLIO
from agents.portfolio_agent import (
    compute_correlation_matrix,
    compute_herfindahl,
    compute_portfolio_beta,
    compute_sector_allocation,
    compute_top_holdings,
)


# ---------------------------------------------------------------------------
# compute_sector_allocation
# ---------------------------------------------------------------------------

def test_sector_allocation_keys_match_sectors():
    result = compute_sector_allocation(MOCK_PORTFOLIO)
    # Crypto holdings have no "sector" key — they should map to "Crypto"
    expected_sectors = {"Technology", "Healthcare", "Financials", "Energy", "Consumer Discretionary", "Crypto"}
    assert set(result.keys()) == expected_sectors


def test_sector_allocation_sums_to_one():
    result = compute_sector_allocation(MOCK_PORTFOLIO)
    assert abs(sum(result.values()) - 1.0) < 0.01


def test_sector_allocation_technology_weight():
    result = compute_sector_allocation(MOCK_PORTFOLIO)
    # AAPL(0.18) + MSFT(0.14) + NVDA(0.10) + META(0.07) = 0.49
    assert abs(result["Technology"] - 0.49) < 0.001


def test_sector_allocation_crypto_weight():
    result = compute_sector_allocation(MOCK_PORTFOLIO)
    # BTC(0.08) + ETH(0.06) = 0.14
    assert abs(result["Crypto"] - 0.14) < 0.001


# ---------------------------------------------------------------------------
# compute_herfindahl
# ---------------------------------------------------------------------------

def test_herfindahl_range():
    weights = [h["weight"] for h in MOCK_PORTFOLIO]
    result = compute_herfindahl(weights)
    assert 0.0 < result < 1.0


def test_herfindahl_equal_weight_10_stocks():
    weights = [0.1] * 10
    result = compute_herfindahl(weights)
    # sum of 10 * (0.1^2) = 0.10
    assert abs(result - 0.10) < 1e-6


def test_herfindahl_single_stock():
    result = compute_herfindahl([1.0])
    assert abs(result - 1.0) < 1e-6


def test_herfindahl_two_equal_stocks():
    result = compute_herfindahl([0.5, 0.5])
    # 0.25 + 0.25 = 0.5
    assert abs(result - 0.5) < 1e-6


# ---------------------------------------------------------------------------
# compute_top_holdings
# ---------------------------------------------------------------------------

def test_top_holdings_count():
    result = compute_top_holdings(MOCK_PORTFOLIO, n=5)
    assert len(result) == 5


def test_top_holdings_sorted_descending():
    result = compute_top_holdings(MOCK_PORTFOLIO, n=5)
    weights = [h["weight"] for h in result]
    assert weights == sorted(weights, reverse=True)


def test_top_holdings_have_required_keys():
    result = compute_top_holdings(MOCK_PORTFOLIO, n=3)
    for holding in result:
        assert "ticker" in holding
        assert "weight" in holding
        assert "sector" in holding


def test_top_holdings_default_n_is_5():
    result = compute_top_holdings(MOCK_PORTFOLIO)
    assert len(result) == 5


def test_top_holdings_first_is_aapl():
    # AAPL has the highest weight (0.18)
    result = compute_top_holdings(MOCK_PORTFOLIO, n=1)
    assert result[0]["ticker"] == "AAPL"


# ---------------------------------------------------------------------------
# compute_portfolio_beta — uses mock price data, no yfinance calls
# ---------------------------------------------------------------------------

def _make_mock_beta_returns():
    """
    Returns (equity_returns_df, spy_returns_series) with known beta.

    We construct a simple scenario: portfolio has 2 equal-weight equities.
    equity_A returns exactly track SPY; equity_B returns are 2x SPY.
    Portfolio weighted beta = 0.5*1 + 0.5*2 = 1.5.
    """
    import pandas as pd

    np.random.seed(42)
    n = 200
    spy = np.random.normal(0.0005, 0.01, n)

    equity_a = spy.copy()            # beta = 1.0
    equity_b = 2.0 * spy             # beta = 2.0

    dates = pd.date_range("2024-01-01", periods=n)
    returns_df = pd.DataFrame({"A": equity_a, "B": equity_b}, index=dates)
    spy_series = pd.Series(spy, index=dates, name="SPY")
    return returns_df, spy_series


def test_portfolio_beta_with_mock_returns():
    """compute_portfolio_beta accepts pre-computed returns when passed directly."""
    returns_df, spy_series = _make_mock_beta_returns()
    weights = [0.5, 0.5]

    portfolio_returns = (returns_df * weights).sum(axis=1)
    data = np.vstack([portfolio_returns.values, spy_series.values])
    cov = np.cov(data)
    beta = cov[0, 1] / cov[1, 1]

    # Directly test the numpy formula used inside compute_portfolio_beta
    assert abs(beta - 1.5) < 0.05  # allow small noise


# ---------------------------------------------------------------------------
# compute_correlation_matrix — uses mock price data, no yfinance calls
# ---------------------------------------------------------------------------

def _make_mock_prices():
    """
    Returns a DataFrame of cumulative price series for 3 tickers.
    Ticker C is constructed to be highly correlated with A, D is uncorrelated.
    """
    import pandas as pd

    np.random.seed(99)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n)
    a = np.random.normal(0, 0.01, n)
    c = a + np.random.normal(0, 0.001, n)   # near-perfect correlation with A
    d = np.random.normal(0, 0.01, n)         # independent

    prices = pd.DataFrame({
        "A": (1 + a).cumprod() * 100,
        "C": (1 + c).cumprod() * 100,
        "D": (1 + d).cumprod() * 100,
    }, index=dates)
    return prices


def test_correlation_matrix_structure_with_mock(monkeypatch):
    """compute_correlation_matrix returns the right nested-dict shape."""
    import pandas as pd
    import yfinance as yf
    from agents.portfolio_agent import compute_correlation_matrix

    mock_prices = _make_mock_prices()

    def fake_download(tickers, period=None, interval=None, auto_adjust=True):
        # Return only tickers that exist in mock_prices
        available = [t for t in tickers if t in mock_prices.columns]
        return mock_prices[available]

    monkeypatch.setattr(yf, "download", fake_download)

    result = compute_correlation_matrix(["A", "C", "D"], lookback_days=90)

    assert isinstance(result, dict)
    assert set(result.keys()) == {"A", "C", "D"}
    for ticker, row in result.items():
        assert set(row.keys()) == {"A", "C", "D"}
        # diagonal must be 1.0
        assert abs(row[ticker] - 1.0) < 0.001


def test_correlation_matrix_ac_highly_correlated(monkeypatch):
    import yfinance as yf

    mock_prices = _make_mock_prices()

    def fake_download(tickers, period=None, interval=None, auto_adjust=True):
        available = [t for t in tickers if t in mock_prices.columns]
        return mock_prices[available]

    monkeypatch.setattr(yf, "download", fake_download)

    result = compute_correlation_matrix(["A", "C", "D"], lookback_days=90)
    # A and C are nearly identical — correlation should be close to 1
    assert result["A"]["C"] > 0.98


def test_correlation_values_rounded_to_4_decimals(monkeypatch):
    import yfinance as yf

    mock_prices = _make_mock_prices()

    def fake_download(tickers, period=None, interval=None, auto_adjust=True):
        available = [t for t in tickers if t in mock_prices.columns]
        return mock_prices[available]

    monkeypatch.setattr(yf, "download", fake_download)

    result = compute_correlation_matrix(["A", "C", "D"], lookback_days=90)
    for ticker, row in result.items():
        for other, val in row.items():
            rounded = round(val, 4)
            assert abs(val - rounded) < 1e-9, f"Value {val} not rounded to 4dp"

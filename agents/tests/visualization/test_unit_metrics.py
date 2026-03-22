"""Unit tests: placeholder risk metrics."""

import pytest

from agents.modeling_charts import estimate_metrics


@pytest.mark.parametrize("mock", [True, False])
def test_estimate_metrics_returns_finite_floats(mock: bool):
    sharpe, vol, slope, metrics = estimate_metrics(["A", "B"], 365, mock=mock)
    assert sharpe == pytest.approx(sharpe) and sharpe > 0
    assert vol == pytest.approx(vol) and 0 < vol < 1
    assert slope == pytest.approx(slope)
    assert "r_squared" in metrics
    assert "max_drawdown" in metrics
    assert "beta" in metrics
    assert metrics["max_drawdown"] < 0


def test_estimate_metrics_mock_vs_live_r_squared_differs():
    _, _, _, m_mock = estimate_metrics(["X"], 30, mock=True)
    _, _, _, m_live = estimate_metrics(["X"], 30, mock=False)
    assert m_mock["r_squared"] == 0.74
    assert m_live["r_squared"] == 0.71


def test_estimate_metrics_holdings_count_affects_sharpe_and_beta():
    s0, _, _, met0 = estimate_metrics([], 100, mock=False)
    s5, _, _, met5 = estimate_metrics([f"T{i}" for i in range(10)], 100, mock=False)
    assert s5 >= s0
    assert met5["beta"] >= met0["beta"]


def test_estimate_metrics_ignores_lookback_for_now_but_accepts_extremes():
    a = estimate_metrics(["A"], 1, mock=True)
    b = estimate_metrics(["A"], 99999, mock=True)
    assert a[0] == b[0] and a[1] == b[1]

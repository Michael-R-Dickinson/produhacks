"""Integration tests: RunModel -> build_model_response (full chart pipeline)."""

import pytest

from agents.models.requests import RunModel
from agents.modeling_charts import CHART_KEYS, build_model_response
from .helpers import assert_valid_png_base64, json_dumps_model


def test_default_analyses_is_regression_only():
    msg = RunModel(holdings=["NVDA"], mock=True)
    assert msg.analyses == ["regression"]
    resp = build_model_response(msg, use_mock=True)
    assert len(resp.charts) == 1
    assert resp.charts[0].chart_type == "regression"


def test_full_registry_single_request(sample_holdings):
    msg = RunModel(
        holdings=sample_holdings,
        analyses=sorted(CHART_KEYS),
        lookback_days=365,
        mock=True,
    )
    resp = build_model_response(msg, use_mock=True)
    assert resp.holdings_analyzed == sample_holdings
    assert {c.chart_type for c in resp.charts} == CHART_KEYS
    for c in resp.charts:
        assert_valid_png_base64(c.image_base64)


def test_holdings_echoed_even_when_empty():
    msg = RunModel(holdings=[], analyses=["regression"], lookback_days=10, mock=True)
    resp = build_model_response(msg, use_mock=True)
    assert resp.holdings_analyzed == []
    assert len(resp.charts) == 1


def test_msg_mock_flag_does_not_change_use_mock_parameter(monkeypatch):
    monkeypatch.setattr("agents.modeling_charts.load_adjusted_close_matrix", lambda *a, **k: None)
    msg = RunModel(holdings=["A"], analyses=["regression"], mock=False)
    mock_on = build_model_response(msg, use_mock=True)
    mock_off = build_model_response(msg, use_mock=False)
    assert mock_on.metrics["r_squared"] == 0.74
    assert mock_off.metrics["r_squared"] == 0.71


def test_chart_payload_size_reasonable_for_sse():
    msg = RunModel(holdings=["AAPL", "MSFT"], analyses=list(CHART_KEYS), lookback_days=365, mock=True)
    resp = build_model_response(msg, use_mock=True)
    for c in resp.charts:
        assert len(c.image_base64) < 2_500_000


def test_model_response_json_encodable(sample_holdings):
    msg = RunModel(holdings=sample_holdings, analyses=list(CHART_KEYS), mock=True)
    resp = build_model_response(msg, use_mock=True)
    s = json_dumps_model(resp)
    assert len(s) > 5000
    assert "charts" in s
    assert "image_base64" in s


@pytest.mark.parametrize("use_mock", [True, False])
def test_metrics_always_include_expected_keys(use_mock: bool):
    msg = RunModel(holdings=["X"], analyses=[], lookback_days=1, mock=True)
    resp = build_model_response(msg, use_mock=use_mock)
    assert set(resp.metrics.keys()) >= {"r_squared", "max_drawdown", "beta"}

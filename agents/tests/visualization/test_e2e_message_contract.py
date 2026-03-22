"""End-to-end style tests: contracts the orchestrator/bridge rely on (no live HTTP)."""

import json

import pytest

from agents.mocks.modeling import mock_model_response
from agents.models.requests import RunModel
from agents.models.responses import ChartOutput, ModelResponse
from agents.modeling_charts import build_model_response


def test_mock_model_response_matches_five_chart_contract():
    r = mock_model_response()
    assert isinstance(r, ModelResponse)
    assert len(r.charts) == 5
    types = {c.chart_type for c in r.charts}
    assert types == {
        "regression",
        "correlation_matrix",
        "sector_performance",
        "volatility_cone",
        "price_history",
    }


def test_roundtrip_model_response_through_json():
    r = mock_model_response()
    blob = r.model_dump()
    s = json.dumps(blob)
    back = json.loads(s)
    restored = ModelResponse.model_validate(back)
    assert restored.sharpe_ratio == r.sharpe_ratio
    assert len(restored.charts) == len(r.charts)
    assert restored.charts[0].image_base64 == r.charts[0].image_base64


def test_chart_output_fields_non_empty():
    r = mock_model_response()
    for c in r.charts:
        assert isinstance(c, ChartOutput)
        assert c.chart_type
        assert c.title
        assert c.summary
        assert len(c.image_base64) > 500


def test_run_model_default_pipeline_matches_orchestrator_expectations(monkeypatch):
    monkeypatch.setattr("agents.modeling_charts.load_adjusted_close_matrix", lambda *a, **k: None)
    msg = RunModel(
        holdings=["SPY", "QQQ", "IWM"],
        lookback_days=365,
        mock=False,
    )
    resp = build_model_response(msg, use_mock=False)
    assert resp.holdings_analyzed == msg.holdings
    assert len(resp.charts) == 1
    assert resp.charts[0].chart_type == "regression"
    assert isinstance(resp.metrics, dict)
    assert "beta" in resp.metrics

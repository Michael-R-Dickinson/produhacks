"""Unit tests: chart registry."""

import pytest

from agents.modeling_charts import CHART_KEYS, run_registered_charts
from .helpers import assert_valid_png_base64


@pytest.mark.parametrize("key", sorted(CHART_KEYS))
def test_each_registered_chart_renders_valid_png(key: str):
    charts = run_registered_charts(["ZZZ"], [key], 90, mock=True)
    assert len(charts) == 1
    assert charts[0].chart_type == key
    assert charts[0].title
    assert charts[0].summary
    assert_valid_png_base64(charts[0].image_base64)


def test_registry_preserves_request_order():
    order = ["price_history", "regression", "volatility_cone"]
    charts = run_registered_charts(["A", "B"], order, 120, mock=True)
    assert [c.chart_type for c in charts] == order


def test_registry_skips_unknown_keys_silently():
    charts = run_registered_charts([], ["nope", "regression", ""], 60, mock=True)
    assert len(charts) == 1
    assert charts[0].chart_type == "regression"


def test_registry_duplicate_keys_produce_duplicate_charts():
    charts = run_registered_charts(["MSFT"], ["regression", "regression"], 80, mock=True)
    assert len(charts) == 2
    assert all(c.chart_type == "regression" for c in charts)


@pytest.mark.parametrize("mock", [True, False])
def test_mock_flag_does_not_break_render(mock: bool):
    charts = run_registered_charts(["AAPL"], list(CHART_KEYS), 200, mock=mock)
    assert len(charts) == len(CHART_KEYS)
    for c in charts:
        assert_valid_png_base64(c.image_base64)

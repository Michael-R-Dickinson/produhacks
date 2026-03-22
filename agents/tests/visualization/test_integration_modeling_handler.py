"""Integration tests: modeling uAgent handler uses modeling_charts pipeline."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.models.requests import RunModel
from agents.modeling_agent import handle_run_model


@pytest.mark.asyncio
async def test_run_model_handler_sends_built_response(monkeypatch):
    monkeypatch.setattr("agents.modeling_agent.mock_data_env", lambda: True)
    ctx = MagicMock()
    ctx.agent.address = "modeling-addr-test"
    ctx.send = AsyncMock()
    msg = RunModel(
        holdings=["AAPL", "GOOGL"],
        analyses=["regression", "correlation_matrix"],
        lookback_days=180,
        mock=True,
    )
    await handle_run_model(ctx, "orchestrator-addr", msg)
    ctx.send.assert_awaited_once()
    sender, payload = ctx.send.call_args[0]
    assert sender == "orchestrator-addr"
    assert payload.holdings_analyzed == ["AAPL", "GOOGL"]
    assert len(payload.charts) == 2
    assert {c.chart_type for c in payload.charts} == {"regression", "correlation_matrix"}
    assert payload.sharpe_ratio > 0


@pytest.mark.asyncio
async def test_run_model_handler_respects_msg_mock_without_env(monkeypatch):
    monkeypatch.setattr("agents.modeling_agent.mock_data_env", lambda: False)
    ctx = MagicMock()
    ctx.agent.address = "addr"
    ctx.send = AsyncMock()
    msg = RunModel(holdings=["X"], analyses=["regression"], mock=True)
    await handle_run_model(ctx, "s", msg)
    payload = ctx.send.call_args[0][1]
    assert payload.metrics["r_squared"] == 0.74


@pytest.mark.asyncio
async def test_run_model_handler_live_branch_metrics(monkeypatch):
    monkeypatch.setattr("agents.modeling_agent.mock_data_env", lambda: False)
    monkeypatch.setattr("agents.modeling_charts.load_adjusted_close_matrix", lambda *a, **k: None)
    ctx = MagicMock()
    ctx.agent.address = "addr"
    ctx.send = AsyncMock()
    msg = RunModel(holdings=["X"], analyses=["regression"], mock=False)
    await handle_run_model(ctx, "s", msg)
    payload = ctx.send.call_args[0][1]
    assert payload.metrics["r_squared"] == 0.71

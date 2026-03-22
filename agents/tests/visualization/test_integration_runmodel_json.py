"""Integration: RunModel survives JSON encode/decode (orchestrator payloads)."""

import json

import pytest

from agents.models.requests import RunModel


def test_run_model_roundtrip_json():
    msg = RunModel(
        holdings=["BRK.B", "BRK-A"],
        analyses=["regression", "volatility_cone"],
        lookback_days=730,
        mock=False,
    )
    data = msg.model_dump()
    s = json.dumps(data)
    back = json.loads(s)
    restored = RunModel.model_validate(back)
    assert restored.holdings == msg.holdings
    assert restored.analyses == msg.analyses
    assert restored.lookback_days == 730
    assert restored.mock is False


def test_run_model_default_analyses_json_roundtrip():
    msg = RunModel(holdings=["X"], mock=True)
    restored = RunModel.model_validate(json.loads(json.dumps(msg.model_dump())))
    assert restored.analyses == ["regression"]

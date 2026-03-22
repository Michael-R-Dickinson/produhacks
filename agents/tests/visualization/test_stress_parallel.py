"""Stress / concurrency: chart pipeline under parallel load."""

import asyncio

import pytest

from agents.models.requests import RunModel
from agents.modeling_charts import build_model_response


@pytest.mark.asyncio
async def test_parallel_build_model_response_isolated_results():
    async def one(idx: int):
        msg = RunModel(
            holdings=[f"T{i}" for i in range(idx, idx + 3)],
            analyses=["regression", "price_history"],
            lookback_days=100 + idx,
            mock=True,
        )
        return build_model_response(msg, use_mock=True)

    results = await asyncio.gather(*(one(i) for i in range(8)))
    assert len(results) == 8
    first_charts = {r.charts[0].image_base64 for r in results}
    assert len(first_charts) >= 4

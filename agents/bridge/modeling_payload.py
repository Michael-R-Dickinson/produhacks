"""Serialize Modeling agent output for the Vite UI SSE contract (``ModelingData``)."""

from __future__ import annotations

from agents.models.responses import ModelResponse


def modeling_ui_payload(resp: ModelResponse) -> dict:
    """Build the ``data`` object for a modeling ``report_section`` SSE event.

    Matches ``ModelingData`` in ``frontend/src/schemas/events.ts`` (charts + optional legacy
    ``chart_base64`` for the first PNG).
    """
    charts = [c.model_dump() for c in resp.charts]
    out: dict = {
        "sharpe_ratio": float(resp.sharpe_ratio),
        "volatility": float(resp.volatility),
        "trend_slope": float(resp.trend_slope),
        "metrics": {k: float(v) for k, v in resp.metrics.items()},
        "charts": charts,
    }
    out["chart_base64"] = charts[0]["image_base64"] if charts else None
    return out

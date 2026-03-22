from agents.models.responses import ModelResponse


def mock_model_response() -> ModelResponse:
    return ModelResponse(
        sharpe_ratio=1.34,
        volatility=0.187,
        trend_slope=0.0023,
        chart_base64=None,  # Phase 2 will generate real charts
    )

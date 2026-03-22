from agents.models.responses import ChartOutput, ModelResponse


def mock_model_response() -> ModelResponse:
    return ModelResponse(
        holdings_analyzed=["AAPL", "MSFT", "NVDA", "UNH", "JPM"],
        sharpe_ratio=1.34,
        volatility=0.187,
        trend_slope=0.0023,
        charts=[
            ChartOutput(
                chart_type="regression",
                title="Portfolio Linear Regression (1Y)",
                image_base64="",  # Phase 2 will generate real chart images
                summary="Portfolio shows positive trend with R-squared 0.74 over 12 months",
            ),
        ],
        metrics={"r_squared": 0.74, "max_drawdown": -0.12, "beta": 1.12},
    )

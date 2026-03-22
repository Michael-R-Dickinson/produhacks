from agents.models.requests import RunModel
from agents.models.responses import ModelResponse
from agents.modeling_charts import build_model_response


def mock_model_response(holdings: list[str] | None = None) -> ModelResponse:
    h = holdings if holdings is not None else ["AAPL", "MSFT", "NVDA", "UNH", "JPM"]
    msg = RunModel(
        holdings=h,
        mock=True,
        analyses=[
            "regression",
            "correlation_matrix",
            "sector_performance",
            "volatility_cone",
            "price_history",
        ],
    )
    return build_model_response(msg, use_mock=True)

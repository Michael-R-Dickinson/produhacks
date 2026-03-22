from uagents import Model


class RunModel(Model):
    """Orchestrator -> Modeling Agent"""
    holdings: list[str]
    analyses: list[str] = ["regression"]
    lookback_days: int = 365
    mock: bool = False


class ChartOutput(Model):
    """Single chart produced by the modeling agent (PNG in markdown report)."""
    chart_type: str
    title: str
    image_base64: str
    summary: str


class ModelResponse(Model):
    """Modeling Agent -> Orchestrator"""
    holdings_analyzed: list[str]
    sharpe_ratio: float
    volatility: float
    trend_slope: float
    charts: list[ChartOutput]
    metrics: dict[str, float]

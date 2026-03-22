from uagents import Model


class PortfolioResponse(Model):
    """Portfolio Agent -> Orchestrator"""
    sector_allocation: dict[str, float]
    top_holdings: list[dict]
    herfindahl_index: float
    portfolio_beta: float


class NewsResponse(Model):
    """News Agent -> Orchestrator"""
    headlines: list[dict]
    aggregate_sentiment: dict[str, float]
    overall_sentiment: float


class ChartOutput(Model):
    """Single chart produced by the modeling agent"""
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


class AlternativesResponse(Model):
    """Alternatives Agent -> Orchestrator"""
    crypto_prices: dict[str, float]
    cross_correlations: dict[str, float]

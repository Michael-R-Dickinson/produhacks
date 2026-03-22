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


class ModelResponse(Model):
    """Modeling Agent -> Orchestrator"""
    sharpe_ratio: float
    volatility: float
    trend_slope: float
    chart_base64: str | None = None


class AlternativesResponse(Model):
    """Alternatives Agent -> Orchestrator"""
    crypto_prices: dict[str, float]
    cross_correlations: dict[str, float]

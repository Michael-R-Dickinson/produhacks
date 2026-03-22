from uagents import Model


class AnalyzePortfolio(Model):
    """Orchestrator -> Portfolio Agent"""
    holdings: list[str]
    mock: bool = False


class PortfolioResponse(Model):
    """Portfolio Agent -> Orchestrator"""
    sector_allocation: dict[str, float]
    top_holdings: list[dict]
    herfindahl_index: float
    portfolio_beta: float
    correlation_matrix: dict[str, dict[str, float]]

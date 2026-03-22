from uagents import Model


class AnalyzeAlternatives(Model):
    """Orchestrator -> Alternatives Agent"""
    mock: bool = False


class AlternativesResponse(Model):
    """Alternatives Agent -> Orchestrator"""
    crypto_prices: dict[str, float]
    cross_correlations: dict[str, float]

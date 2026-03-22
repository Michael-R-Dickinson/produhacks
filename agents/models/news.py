from uagents import Model


class FetchNews(Model):
    """Orchestrator -> News Agent"""
    tickers: list[str]
    mock: bool = False


class NewsResponse(Model):
    """News Agent -> Orchestrator"""
    headlines: list[dict]
    aggregate_sentiment: dict[str, float]
    overall_sentiment: float

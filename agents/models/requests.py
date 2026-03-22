from uagents import Model


class AnalyzePortfolio(Model):
    """Orchestrator -> Portfolio Agent"""
    holdings: list[str]
    mock: bool = False


class FetchNews(Model):
    """Orchestrator -> News Agent"""
    tickers: list[str]
    mock: bool = False


class RunModel(Model):
    """Orchestrator -> Modeling Agent"""
    holdings: list[str]
    mock: bool = False


class AnalyzeAlternatives(Model):
    """Orchestrator -> Alternatives Agent"""
    mock: bool = False

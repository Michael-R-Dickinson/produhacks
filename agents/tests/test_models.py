from agents.models.requests import AnalyzeAlternatives, AnalyzePortfolio, FetchNews, RunModel
from agents.models.responses import (
    AlternativesResponse,
    ChartOutput,
    ModelResponse,
    NewsResponse,
    PortfolioResponse,
)


def test_all_request_models_importable():
    assert AnalyzePortfolio is not None
    assert FetchNews is not None
    assert RunModel is not None
    assert AnalyzeAlternatives is not None


def test_all_response_models_importable():
    assert PortfolioResponse is not None
    assert NewsResponse is not None
    assert ChartOutput is not None
    assert ModelResponse is not None
    assert AlternativesResponse is not None


def test_request_roundtrip_serialization():
    portfolio = AnalyzePortfolio(holdings=["AAPL", "MSFT"], mock=True)
    data = portfolio.model_dump()
    reconstructed = AnalyzePortfolio(**data)
    assert reconstructed.holdings == ["AAPL", "MSFT"]
    assert reconstructed.mock is True

    news = FetchNews(tickers=["AAPL"], mock=False)
    data = news.model_dump()
    reconstructed = FetchNews(**data)
    assert reconstructed.tickers == ["AAPL"]
    assert reconstructed.mock is False

    model = RunModel(holdings=["NVDA"], mock=True, analyses=["regression"], lookback_days=180)
    data = model.model_dump()
    reconstructed = RunModel(**data)
    assert reconstructed.holdings == ["NVDA"]
    assert reconstructed.mock is True
    assert reconstructed.analyses == ["regression"]
    assert reconstructed.lookback_days == 180

    alternatives = AnalyzeAlternatives(mock=False)
    data = alternatives.model_dump()
    reconstructed = AnalyzeAlternatives(**data)
    assert reconstructed.mock is False


def test_response_roundtrip_serialization():
    portfolio_resp = PortfolioResponse(
        sector_allocation={"Technology": 0.42, "Healthcare": 0.18},
        top_holdings=[{"ticker": "AAPL", "weight": 0.18}],
        herfindahl_index=0.087,
        portfolio_beta=1.12,
    )
    data = portfolio_resp.model_dump()
    reconstructed = PortfolioResponse(**data)
    assert reconstructed.sector_allocation["Technology"] == 0.42
    assert reconstructed.herfindahl_index == 0.087

    news_resp = NewsResponse(
        headlines=[{"title": "Test", "sentiment": 0.5, "ticker": "AAPL"}],
        aggregate_sentiment={"AAPL": 0.5},
        overall_sentiment=0.5,
    )
    data = news_resp.model_dump()
    reconstructed = NewsResponse(**data)
    assert reconstructed.overall_sentiment == 0.5

    chart = ChartOutput(
        chart_type="regression",
        title="Test",
        image_base64="AAA",
        summary="Stub",
    )
    model_resp = ModelResponse(
        holdings_analyzed=["NVDA"],
        sharpe_ratio=1.34,
        volatility=0.187,
        trend_slope=0.0023,
        charts=[chart],
        metrics={"r_squared": 0.5},
    )
    data = model_resp.model_dump()
    reconstructed = ModelResponse(**data)
    assert reconstructed.sharpe_ratio == 1.34
    assert len(reconstructed.charts) == 1
    assert reconstructed.charts[0].chart_type == "regression"
    assert reconstructed.metrics["r_squared"] == 0.5

    alt_resp = AlternativesResponse(
        crypto_prices={"BTC": 67450.0},
        cross_correlations={"BTC": 0.12},
    )
    data = alt_resp.model_dump()
    reconstructed = AlternativesResponse(**data)
    assert reconstructed.crypto_prices["BTC"] == 67450.0


def test_domain_model_modules_importable():
    from agents.models.portfolio import AnalyzePortfolio, PortfolioResponse
    from agents.models.news import FetchNews, NewsResponse
    from agents.models.modeling import RunModel, ChartOutput, ModelResponse
    from agents.models.alternatives import AnalyzeAlternatives, AlternativesResponse

    assert AnalyzePortfolio is not None
    assert PortfolioResponse is not None


def test_models_reexported_from_init():
    from agents.models import (
        AnalyzeAlternatives,
        AnalyzePortfolio,
        AlternativesResponse,
        ChartOutput,
        FetchNews,
        ModelResponse,
        NewsResponse,
        PortfolioResponse,
        RunModel,
    )
    assert AnalyzePortfolio is not None
    assert FetchNews is not None
    assert RunModel is not None
    assert AnalyzeAlternatives is not None
    assert PortfolioResponse is not None
    assert NewsResponse is not None
    assert ModelResponse is not None
    assert ChartOutput is not None
    assert AlternativesResponse is not None

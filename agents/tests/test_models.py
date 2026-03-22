from agents.models.requests import AnalyzePortfolio, FetchNews, RunModel, AnalyzeAlternatives, ReportRequest
from agents.models.responses import PortfolioResponse, NewsResponse, ChartOutput, ModelResponse, AlternativesResponse


def test_all_request_models_importable():
    assert AnalyzePortfolio is not None
    assert FetchNews is not None
    assert RunModel is not None
    assert AnalyzeAlternatives is not None
    assert ReportRequest is not None


def test_all_response_models_importable():
    assert PortfolioResponse is not None
    assert NewsResponse is not None
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

    model = RunModel(holdings=["NVDA"], mock=True)
    data = model.model_dump()
    reconstructed = RunModel(**data)
    assert reconstructed.holdings == ["NVDA"]
    assert reconstructed.mock is True

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
        correlation_matrix={"AAPL": {"MSFT": 0.82}},
    )
    data = portfolio_resp.model_dump()
    reconstructed = PortfolioResponse(**data)
    assert reconstructed.sector_allocation["Technology"] == 0.42
    assert reconstructed.herfindahl_index == 0.087
    assert reconstructed.correlation_matrix["AAPL"]["MSFT"] == 0.82

    news_resp = NewsResponse(
        headlines=[{"title": "Test", "sentiment": 0.5, "ticker": "AAPL"}],
        aggregate_sentiment={"AAPL": 0.5},
        overall_sentiment=0.5,
    )
    data = news_resp.model_dump()
    reconstructed = NewsResponse(**data)
    assert reconstructed.overall_sentiment == 0.5

    model_resp = ModelResponse(
        holdings_analyzed=["AAPL", "MSFT"],
        sharpe_ratio=1.34,
        volatility=0.187,
        trend_slope=0.0023,
        charts=[ChartOutput(chart_type="regression", title="Test", image_base64="", summary="Test summary")],
        metrics={"r_squared": 0.74},
    )
    data = model_resp.model_dump()
    reconstructed = ModelResponse(**data)
    assert reconstructed.sharpe_ratio == 1.34
    assert len(reconstructed.charts) == 1
    assert reconstructed.charts[0].chart_type == "regression"

    alt_resp = AlternativesResponse(
        crypto_prices={"BTC": 67450.0},
        cross_correlations={"BTC": 0.12},
        trend_signals={"BTC": "bullish"},
        btc_dominance=52.3,
        commodities={"GOLD": 2340.50, "OIL": 78.25},
    )
    data = alt_resp.model_dump()
    reconstructed = AlternativesResponse(**data)
    assert reconstructed.crypto_prices["BTC"] == 67450.0
    assert reconstructed.btc_dominance == 52.3
    assert reconstructed.trend_signals["BTC"] == "bullish"
    assert reconstructed.commodities["GOLD"] == 2340.50


def test_report_request_model():
    req = ReportRequest(holdings=["AAPL", "MSFT"], mock=True)
    data = req.model_dump()
    reconstructed = ReportRequest(**data)
    assert reconstructed.holdings == ["AAPL", "MSFT"]
    assert reconstructed.mock is True

    req_default = ReportRequest(holdings=["NVDA"])
    assert req_default.mock is False


def test_models_reexported_from_init():
    from agents.models import (
        AnalyzePortfolio,
        FetchNews,
        RunModel,
        AnalyzeAlternatives,
        ReportRequest,
        PortfolioResponse,
        NewsResponse,
        ModelResponse,
        AlternativesResponse,
    )
    assert AnalyzePortfolio is not None
    assert FetchNews is not None
    assert RunModel is not None
    assert AnalyzeAlternatives is not None
    assert ReportRequest is not None
    assert PortfolioResponse is not None
    assert NewsResponse is not None
    assert ModelResponse is not None
    assert AlternativesResponse is not None

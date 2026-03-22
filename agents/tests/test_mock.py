from agents.mocks.portfolio import mock_portfolio_response
from agents.mocks.news import mock_news_response
from agents.mocks.modeling import mock_model_response
from agents.mocks.alternatives import mock_alternatives_response
from agents.models.responses import PortfolioResponse, NewsResponse, ModelResponse, AlternativesResponse


def test_mock_portfolio_returns_portfolio_response():
    result = mock_portfolio_response()
    assert isinstance(result, PortfolioResponse)
    assert len(result.sector_allocation) >= 3
    assert result.herfindahl_index > 0


def test_mock_news_returns_news_response():
    result = mock_news_response()
    assert isinstance(result, NewsResponse)
    assert len(result.headlines) >= 3
    assert -1.0 <= result.overall_sentiment <= 1.0


def test_mock_model_returns_model_response():
    result = mock_model_response()
    assert isinstance(result, ModelResponse)
    assert result.sharpe_ratio > 0
    assert result.volatility > 0


def test_mock_alternatives_returns_alternatives_response():
    result = mock_alternatives_response()
    assert isinstance(result, AlternativesResponse)
    assert "BTC" in result.crypto_prices


def test_all_mocks_importable_from_init():
    from agents.mocks import (
        mock_portfolio_response,
        mock_news_response,
        mock_model_response,
        mock_alternatives_response,
    )
    assert mock_portfolio_response() is not None
    assert mock_news_response() is not None
    assert mock_model_response() is not None
    assert mock_alternatives_response() is not None

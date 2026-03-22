"""Tests for orchestrator pure logic functions.

Tests do NOT call Gemini API -- only contradiction detection and prompt building tested.
"""

import pytest

from agents.models.responses import (
    AlternativesResponse,
    ModelResponse,
    NewsResponse,
    PortfolioResponse,
)


def make_portfolio(top_holdings=None, sector_allocation=None) -> PortfolioResponse:
    return PortfolioResponse(
        sector_allocation=sector_allocation or {"Technology": 0.49, "Healthcare": 0.14},
        top_holdings=top_holdings or [
            {"ticker": "AAPL", "weight": 0.18, "sector": "Technology"},
            {"ticker": "MSFT", "weight": 0.14, "sector": "Technology"},
            {"ticker": "NVDA", "weight": 0.10, "sector": "Technology"},
        ],
        herfindahl_index=0.087,
        portfolio_beta=1.12,
        correlation_matrix={"AAPL": {"AAPL": 1.0}},
    )


def make_news(aggregate_sentiment=None, overall_sentiment=0.29) -> NewsResponse:
    return NewsResponse(
        headlines=[{"title": "Test headline", "sentiment": 0.5, "ticker": "AAPL"}],
        aggregate_sentiment=aggregate_sentiment or {"AAPL": 0.82},
        overall_sentiment=overall_sentiment,
    )


def make_modeling(trend_slope=0.5) -> ModelResponse:
    return ModelResponse(
        holdings_analyzed=["AAPL", "MSFT"],
        sharpe_ratio=1.25,
        volatility=0.18,
        trend_slope=trend_slope,
        charts=[],
        metrics={"beta": 1.12},
    )


def make_alternatives() -> AlternativesResponse:
    return AlternativesResponse(
        crypto_prices={"BTC": 67450.0, "ETH": 3520.0},
        cross_correlations={"BTC": 0.12, "ETH": 0.18},
        trend_signals={"BTC": "bullish", "ETH": "bullish"},
        btc_dominance=52.3,
        commodities={"GOLD": 2340.50, "OIL": 78.25},
    )


class TestSafeResult:
    def test_safe_result_returns_fallback_on_exception(self):
        from agents.orchestrator import safe_result

        fallback = object()
        result = safe_result(Exception("timeout"), fallback)
        assert result is fallback

    def test_safe_result_returns_valid_response(self):
        from agents.orchestrator import safe_result

        valid = object()
        fallback = object()
        result = safe_result(valid, fallback)
        assert result is valid

    def test_safe_result_returns_fallback_on_base_exception(self):
        from agents.orchestrator import safe_result

        fallback = "fallback"
        result = safe_result(ValueError("bad value"), fallback)
        assert result == fallback


class TestDetectContradictions:
    def test_bearish_news_with_top_holding_flags_contradiction(self):
        from agents.orchestrator import detect_contradictions

        portfolio = make_portfolio(
            top_holdings=[{"ticker": "MSFT", "weight": 0.14, "sector": "Technology"}]
        )
        news = make_news(aggregate_sentiment={"MSFT": -0.45})
        modeling = make_modeling(trend_slope=0.5)

        contradictions = detect_contradictions(portfolio, news, modeling)

        assert len(contradictions) == 1
        assert "MSFT" in contradictions[0]
        assert "bearish" in contradictions[0].lower()

    def test_all_positive_news_returns_empty_list(self):
        from agents.orchestrator import detect_contradictions

        portfolio = make_portfolio()
        news = make_news(aggregate_sentiment={"AAPL": 0.82, "MSFT": 0.55, "NVDA": 0.91})
        modeling = make_modeling(trend_slope=0.5)

        contradictions = detect_contradictions(portfolio, news, modeling)

        assert contradictions == []

    def test_bullish_news_with_negative_momentum_flags_contradiction(self):
        from agents.orchestrator import detect_contradictions

        portfolio = make_portfolio()
        news = make_news(aggregate_sentiment={"AAPL": 0.75})
        modeling = make_modeling(trend_slope=-0.5)

        contradictions = detect_contradictions(portfolio, news, modeling)

        assert len(contradictions) == 1
        assert "AAPL" in contradictions[0]
        assert "bullish" in contradictions[0].lower()

    def test_neutral_sentiment_does_not_flag_contradiction(self):
        from agents.orchestrator import detect_contradictions

        portfolio = make_portfolio(
            top_holdings=[{"ticker": "AAPL", "weight": 0.18, "sector": "Technology"}]
        )
        news = make_news(aggregate_sentiment={"AAPL": -0.15})  # between -0.3 and 0
        modeling = make_modeling(trend_slope=0.5)

        contradictions = detect_contradictions(portfolio, news, modeling)

        assert contradictions == []

    def test_low_weight_holding_bearish_news_does_not_flag(self):
        """Bearish news on a small holding (weight <= 0.05) should not flag."""
        from agents.orchestrator import detect_contradictions

        portfolio = make_portfolio(
            top_holdings=[{"ticker": "XOM", "weight": 0.04, "sector": "Energy"}]
        )
        news = make_news(aggregate_sentiment={"XOM": -0.5})
        modeling = make_modeling(trend_slope=0.5)

        contradictions = detect_contradictions(portfolio, news, modeling)

        assert contradictions == []

    def test_multiple_contradictions_detected(self):
        from agents.orchestrator import detect_contradictions

        portfolio = make_portfolio(
            top_holdings=[
                {"ticker": "MSFT", "weight": 0.14, "sector": "Technology"},
                {"ticker": "JPM", "weight": 0.07, "sector": "Financials"},
            ]
        )
        news = make_news(aggregate_sentiment={"MSFT": -0.5, "JPM": -0.6})
        modeling = make_modeling(trend_slope=0.5)

        contradictions = detect_contradictions(portfolio, news, modeling)

        assert len(contradictions) == 2


class TestBuildSynthesisPrompt:
    def test_prompt_contains_professional_financial_analyst(self):
        from agents.orchestrator import build_synthesis_prompt

        portfolio = make_portfolio()
        news = make_news()
        modeling = make_modeling()
        alt = make_alternatives()

        prompt = build_synthesis_prompt(portfolio, news, modeling, alt, [], [])

        assert "professional financial analyst" in prompt

    def test_prompt_contains_thematic_sections(self):
        from agents.orchestrator import build_synthesis_prompt

        portfolio = make_portfolio()
        news = make_news()
        modeling = make_modeling()
        alt = make_alternatives()

        prompt = build_synthesis_prompt(portfolio, news, modeling, alt, [], [])

        assert "thematic" in prompt.lower()

    def test_prompt_contains_agent_data(self):
        from agents.orchestrator import build_synthesis_prompt

        portfolio = make_portfolio()
        news = make_news()
        modeling = make_modeling()
        alt = make_alternatives()

        prompt = build_synthesis_prompt(portfolio, news, modeling, alt, [], [])

        # Should contain serialized data from each agent
        assert "sector_allocation" in prompt or "Technology" in prompt
        assert "aggregate_sentiment" in prompt or "AAPL" in prompt
        assert "sharpe_ratio" in prompt or "1.25" in prompt

    def test_prompt_contains_contradictions_when_present(self):
        from agents.orchestrator import build_synthesis_prompt

        portfolio = make_portfolio()
        news = make_news()
        modeling = make_modeling()
        alt = make_alternatives()
        contradictions = ["MSFT: News sentiment is bearish but it is a top holding"]

        prompt = build_synthesis_prompt(portfolio, news, modeling, alt, contradictions, [])

        assert "MSFT" in prompt

    def test_prompt_contains_chart_embeds(self):
        from agents.orchestrator import build_synthesis_prompt

        portfolio = make_portfolio()
        news = make_news()
        modeling = make_modeling()
        alt = make_alternatives()
        chart_embeds = ["![Portfolio Chart](data:image/png;base64,abc123)"]

        prompt = build_synthesis_prompt(portfolio, news, modeling, alt, [], chart_embeds)

        assert "abc123" in prompt

    def test_prompt_has_word_limit_guidance(self):
        from agents.orchestrator import build_synthesis_prompt

        portfolio = make_portfolio()
        news = make_news()
        modeling = make_modeling()
        alt = make_alternatives()

        prompt = build_synthesis_prompt(portfolio, news, modeling, alt, [], [])

        assert "600" in prompt or "800" in prompt or "words" in prompt.lower()

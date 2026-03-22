"""
Unit tests for news_agent pure logic functions.
Tests do NOT load FinBERT or call Finnhub — uses pre-scored mock headline data.
"""
import pytest

from agents.news_agent import (
    aggregate_sentiment_by_ticker,
    compute_overall_sentiment,
    filter_headlines_for_tickers,
)


# -- Fixtures --

SAMPLE_HEADLINES = [
    {
        "headline": "Apple reports record iPhone 16 sales this quarter",
        "source": "Reuters",
        "related": "AAPL",
        "datetime": 1700000000,
        "url": "https://example.com/1",
    },
    {
        "headline": "Microsoft Azure growth slows as enterprise spending tightens",
        "source": "Bloomberg",
        "related": "MSFT",
        "datetime": 1700000001,
        "url": "https://example.com/2",
    },
    {
        "headline": "NVIDIA unveils next-gen Blackwell Ultra AI chips for data centers",
        "source": "TechCrunch",
        "related": "NVDA",
        "datetime": 1700000002,
        "url": "https://example.com/3",
    },
    {
        "headline": "General market update: Fed holds rates steady amid inflation data",
        "source": "WSJ",
        "related": "",
        "datetime": 1700000003,
        "url": "https://example.com/4",
    },
    {
        "headline": "AAPL and MSFT both hit 52-week highs in broad tech rally",
        "source": "CNBC",
        "related": "AAPL,MSFT",
        "datetime": 1700000004,
        "url": "https://example.com/5",
    },
]

SCORED_HEADLINES = [
    {"headline": "Apple crushes Q1 expectations", "matched_tickers": ["AAPL"], "sentiment": 0.82},
    {"headline": "Apple faces antitrust scrutiny in EU", "matched_tickers": ["AAPL"], "sentiment": -0.45},
    {"headline": "Microsoft Azure growth disappoints", "matched_tickers": ["MSFT"], "sentiment": -0.35},
    {"headline": "NVIDIA data center revenue doubles", "matched_tickers": ["NVDA"], "sentiment": 0.91},
]


# -- filter_headlines_for_tickers tests --

def test_filter_keeps_ticker_in_headline_text():
    result = filter_headlines_for_tickers(SAMPLE_HEADLINES, ["AAPL", "MSFT"])
    headlines_text = [h["headline"] for h in result]
    # "Apple..." matches AAPL via related field; "Microsoft..." matches MSFT via related
    assert any("Apple" in h for h in headlines_text) or any("AAPL" in h for h in headlines_text)


def test_filter_keeps_ticker_in_related_field():
    result = filter_headlines_for_tickers(SAMPLE_HEADLINES, ["NVDA"])
    assert len(result) >= 1
    assert any("NVIDIA" in h["headline"] for h in result)


def test_filter_discards_unrelated_headlines():
    result = filter_headlines_for_tickers(SAMPLE_HEADLINES, ["JPM"])
    # No JPM in any headline or related
    assert len(result) == 0


def test_filter_tags_matched_tickers():
    result = filter_headlines_for_tickers(SAMPLE_HEADLINES, ["AAPL", "MSFT"])
    for h in result:
        assert "matched_tickers" in h
        assert isinstance(h["matched_tickers"], list)
        assert len(h["matched_tickers"]) >= 1


def test_filter_headline_matches_multiple_tickers():
    # "AAPL and MSFT both hit 52-week highs..." matches both
    result = filter_headlines_for_tickers(SAMPLE_HEADLINES, ["AAPL", "MSFT"])
    multi = [h for h in result if len(h["matched_tickers"]) > 1]
    assert len(multi) >= 1


def test_filter_caps_at_five_headlines_per_ticker():
    # Create 8 headlines all related to AAPL
    many = [
        {
            "headline": f"Apple story number {i}",
            "source": "Reuters",
            "related": "AAPL",
            "datetime": 1700000000 + i,
            "url": f"https://example.com/{i}",
        }
        for i in range(8)
    ]
    result = filter_headlines_for_tickers(many, ["AAPL"])
    aapl_count = sum(1 for h in result if "AAPL" in h["matched_tickers"])
    assert aapl_count <= 5


def test_filter_case_insensitive_ticker_match():
    headlines = [
        {
            "headline": "aapl stock surges on strong earnings beat",
            "source": "Reuters",
            "related": "",
            "datetime": 1700000000,
            "url": "https://example.com/1",
        }
    ]
    result = filter_headlines_for_tickers(headlines, ["AAPL"])
    assert len(result) == 1


# -- aggregate_sentiment_by_ticker tests --

def test_aggregate_returns_mean_per_ticker():
    result = aggregate_sentiment_by_ticker(SCORED_HEADLINES)
    assert "AAPL" in result
    assert "MSFT" in result
    assert "NVDA" in result
    # AAPL mean = (0.82 + -0.45) / 2 = 0.185
    assert abs(result["AAPL"] - 0.185) < 0.001


def test_aggregate_single_headline_ticker():
    result = aggregate_sentiment_by_ticker(SCORED_HEADLINES)
    # MSFT has one headline: -0.35
    assert abs(result["MSFT"] - (-0.35)) < 0.001


def test_aggregate_empty_returns_empty_dict():
    result = aggregate_sentiment_by_ticker([])
    assert result == {}


def test_aggregate_only_includes_tickers_present():
    result = aggregate_sentiment_by_ticker(SCORED_HEADLINES)
    assert "JPM" not in result


# -- compute_overall_sentiment tests --

def test_compute_overall_sentiment_mean():
    aggregate = {"AAPL": 0.82, "MSFT": -0.35, "NVDA": 0.91}
    result = compute_overall_sentiment(aggregate)
    expected = (0.82 + (-0.35) + 0.91) / 3
    assert abs(result - expected) < 0.001


def test_compute_overall_sentiment_single():
    result = compute_overall_sentiment({"AAPL": 0.5})
    assert abs(result - 0.5) < 0.001


def test_compute_overall_sentiment_empty():
    result = compute_overall_sentiment({})
    assert result == 0.0


# -- score_headlines near-neutral filter test --
# We test the filtering behavior without calling FinBERT by using
# a stub that we inject via monkeypatching.

def test_score_headlines_discards_near_neutral(monkeypatch):
    from agents import news_agent

    def fake_score(text: str) -> float:
        # Map specific texts to controlled scores
        scores = {
            "strong buy signal": 0.8,
            "mildly ok news": 0.05,  # near-neutral, should be discarded
            "company goes bankrupt": -0.9,
        }
        return scores.get(text, 0.0)

    monkeypatch.setattr(news_agent, "score_sentiment", fake_score)

    headlines = [
        {"headline": "strong buy signal", "matched_tickers": ["AAPL"]},
        {"headline": "mildly ok news", "matched_tickers": ["MSFT"]},
        {"headline": "company goes bankrupt", "matched_tickers": ["JPM"]},
    ]
    from agents.news_agent import score_headlines
    result = score_headlines(headlines)
    result_texts = [h["headline"] for h in result]
    assert "strong buy signal" in result_texts
    assert "company goes bankrupt" in result_texts
    assert "mildly ok news" not in result_texts


# -- mock mode test --

def test_mock_mode_returns_news_response():
    from agents.mocks.news import mock_news_response
    from agents.models.responses import NewsResponse
    resp = mock_news_response()
    assert isinstance(resp, NewsResponse)
    assert len(resp.headlines) > 0
    assert isinstance(resp.aggregate_sentiment, dict)
    assert isinstance(resp.overall_sentiment, float)

from agents.models.responses import NewsResponse


def mock_news_response() -> NewsResponse:
    return NewsResponse(
        headlines=[
            {"title": "Apple reports record Q1 revenue driven by iPhone 16 demand", "sentiment": 0.82, "ticker": "AAPL"},
            {"title": "Microsoft Azure growth slows amid enterprise spending pullback", "sentiment": -0.35, "ticker": "MSFT"},
            {"title": "NVIDIA announces next-gen Blackwell Ultra chips for AI data centers", "sentiment": 0.91, "ticker": "NVDA"},
            {"title": "JPMorgan warns of commercial real estate risks in Q2 outlook", "sentiment": -0.48, "ticker": "JPM"},
            {"title": "UnitedHealth Group expands Medicare Advantage network coverage", "sentiment": 0.55, "ticker": "UNH"},
        ],
        aggregate_sentiment={"AAPL": 0.82, "MSFT": -0.35, "NVDA": 0.91, "JPM": -0.48, "UNH": 0.55},
        overall_sentiment=0.29,
    )

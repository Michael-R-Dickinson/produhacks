from agents.models.responses import PortfolioResponse


def mock_portfolio_response() -> PortfolioResponse:
    return PortfolioResponse(
        sector_allocation={
            "Technology": 0.42,
            "Healthcare": 0.18,
            "Financials": 0.15,
            "Consumer Discretionary": 0.12,
            "Energy": 0.08,
            "Other": 0.05,
        },
        top_holdings=[
            {"ticker": "AAPL", "weight": 0.18, "sector": "Technology"},
            {"ticker": "MSFT", "weight": 0.15, "sector": "Technology"},
            {"ticker": "NVDA", "weight": 0.09, "sector": "Technology"},
            {"ticker": "UNH", "weight": 0.08, "sector": "Healthcare"},
            {"ticker": "JPM", "weight": 0.07, "sector": "Financials"},
        ],
        herfindahl_index=0.087,
        portfolio_beta=1.12,
    )

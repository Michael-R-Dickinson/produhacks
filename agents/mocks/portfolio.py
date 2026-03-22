from agents.data.portfolio import MOCK_PORTFOLIO, EQUITY_TICKERS
from agents.models.responses import PortfolioResponse

# Within-sector correlations are high, cross-sector are lower
_CORRELATION_MATRIX: dict[str, dict[str, float]] = {
    "AAPL": {"AAPL": 1.0,  "MSFT": 0.82, "NVDA": 0.75, "META": 0.71, "UNH": 0.23, "JNJ": 0.18, "JPM": 0.31, "GS": 0.28, "XOM": 0.14, "TSLA": 0.45},
    "MSFT": {"AAPL": 0.82, "MSFT": 1.0,  "NVDA": 0.79, "META": 0.68, "UNH": 0.21, "JNJ": 0.16, "JPM": 0.34, "GS": 0.30, "XOM": 0.12, "TSLA": 0.41},
    "NVDA": {"AAPL": 0.75, "MSFT": 0.79, "NVDA": 1.0,  "META": 0.62, "UNH": 0.19, "JNJ": 0.14, "JPM": 0.27, "GS": 0.24, "XOM": 0.11, "TSLA": 0.52},
    "META": {"AAPL": 0.71, "MSFT": 0.68, "NVDA": 0.62, "META": 1.0,  "UNH": 0.17, "JNJ": 0.13, "JPM": 0.25, "GS": 0.22, "XOM": 0.09, "TSLA": 0.48},
    "UNH":  {"AAPL": 0.23, "MSFT": 0.21, "NVDA": 0.19, "META": 0.17, "UNH": 1.0,  "JNJ": 0.74, "JPM": 0.29, "GS": 0.26, "XOM": 0.18, "TSLA": 0.15},
    "JNJ":  {"AAPL": 0.18, "MSFT": 0.16, "NVDA": 0.14, "META": 0.13, "UNH": 0.74, "JNJ": 1.0,  "JPM": 0.22, "GS": 0.19, "XOM": 0.15, "TSLA": 0.11},
    "JPM":  {"AAPL": 0.31, "MSFT": 0.34, "NVDA": 0.27, "META": 0.25, "UNH": 0.29, "JNJ": 0.22, "JPM": 1.0,  "GS": 0.88, "XOM": 0.35, "TSLA": 0.28},
    "GS":   {"AAPL": 0.28, "MSFT": 0.30, "NVDA": 0.24, "META": 0.22, "UNH": 0.26, "JNJ": 0.19, "JPM": 0.88, "GS": 1.0,  "XOM": 0.32, "TSLA": 0.25},
    "XOM":  {"AAPL": 0.14, "MSFT": 0.12, "NVDA": 0.11, "META": 0.09, "UNH": 0.18, "JNJ": 0.15, "JPM": 0.35, "GS": 0.32, "XOM": 1.0,  "TSLA": 0.21},
    "TSLA": {"AAPL": 0.45, "MSFT": 0.41, "NVDA": 0.52, "META": 0.48, "UNH": 0.15, "JNJ": 0.11, "JPM": 0.28, "GS": 0.25, "XOM": 0.21, "TSLA": 1.0},
}


def mock_portfolio_response() -> PortfolioResponse:
    sector_allocation: dict[str, float] = {}
    for holding in MOCK_PORTFOLIO:
        if holding.get("type") == "crypto":
            continue
        sector = holding["sector"]
        sector_allocation[sector] = sector_allocation.get(sector, 0.0) + holding["weight"]

    top_holdings = [
        {"ticker": h["ticker"], "weight": h["weight"], "sector": h.get("sector", h.get("type", ""))}
        for h in MOCK_PORTFOLIO
        if h.get("type") != "crypto"
    ]

    return PortfolioResponse(
        sector_allocation=sector_allocation,
        top_holdings=top_holdings,
        herfindahl_index=0.087,
        portfolio_beta=1.12,
        correlation_matrix=_CORRELATION_MATRIX,
    )

MOCK_PORTFOLIO = [
    {"ticker": "AAPL", "weight": 0.18, "sector": "Technology", "shares": 150},
    {"ticker": "MSFT", "weight": 0.14, "sector": "Technology", "shares": 80},
    {"ticker": "NVDA", "weight": 0.10, "sector": "Technology", "shares": 200},
    {"ticker": "META", "weight": 0.07, "sector": "Technology", "shares": 120},
    {"ticker": "UNH",  "weight": 0.09, "sector": "Healthcare", "shares": 45},
    {"ticker": "JNJ",  "weight": 0.05, "sector": "Healthcare", "shares": 80},
    {"ticker": "JPM",  "weight": 0.07, "sector": "Financials", "shares": 90},
    {"ticker": "GS",   "weight": 0.04, "sector": "Financials", "shares": 30},
    {"ticker": "XOM",  "weight": 0.06, "sector": "Energy", "shares": 110},
    {"ticker": "TSLA", "weight": 0.06, "sector": "Consumer Discretionary", "shares": 95},
    {"ticker": "BTC",  "weight": 0.08, "type": "crypto"},
    {"ticker": "ETH",  "weight": 0.06, "type": "crypto"},
]

EQUITY_TICKERS = [h["ticker"] for h in MOCK_PORTFOLIO if h.get("type") != "crypto"]
CRYPTO_TICKERS = [h["ticker"] for h in MOCK_PORTFOLIO if h.get("type") == "crypto"]
ALL_TICKERS = [h["ticker"] for h in MOCK_PORTFOLIO]

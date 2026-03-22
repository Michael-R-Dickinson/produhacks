import os

import httpx
import pandas as pd
from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.mocks.alternatives import mock_alternatives_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
from agents.models.requests import AnalyzeAlternatives
from agents.models.responses import AlternativesResponse
from agents.ports import ALTERNATIVES_PORT

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "AVAX": "avalanche-2",
}

alternatives_agent = Agent(
    name="alternatives",
    seed="alternatives-agent-seed-investiswarm",
    port=ALTERNATIVES_PORT,
)


async def fetch_crypto_prices(coins: list[str]) -> tuple[dict[str, float], dict[str, float]]:
    """Fetch current prices and 7d changes from CoinGecko.

    Returns (prices_dict, change_7d_dict): ({ticker: usd_price}, {ticker: 7d_percent_change}).
    Always includes BTC and ETH.
    """
    tickers = list({*coins, "BTC", "ETH"})
    ids = [COINGECKO_IDS[t] for t in tickers if t in COINGECKO_IDS]
    ids_param = ",".join(ids)

    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids_param}&vs_currencies=usd&include_24hr_change=true&include_7d_change=true"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    id_to_ticker = {v: k for k, v in COINGECKO_IDS.items()}
    prices: dict[str, float] = {}
    change_7d: dict[str, float] = {}

    for cg_id, values in data.items():
        ticker = id_to_ticker.get(cg_id)
        if ticker:
            prices[ticker] = float(values.get("usd", 0.0))
            change_7d[ticker] = float(values.get("usd_7d_change", 0.0))

    return prices, change_7d


async def fetch_btc_dominance() -> float:
    """Fetch BTC market cap dominance percentage from CoinGecko global endpoint."""
    url = "https://api.coingecko.com/api/v3/global"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    return float(data["data"]["market_cap_percentage"]["btc"])


async def fetch_commodity_prices(api_key: str) -> dict[str, float]:
    """Fetch gold (GC1!) and oil (CL1!) prices from Finnhub."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        gold_resp = await client.get(
            f"https://finnhub.io/api/v1/quote?symbol=GC1!&token={api_key}"
        )
        gold_resp.raise_for_status()
        gold_data = gold_resp.json()

        oil_resp = await client.get(
            f"https://finnhub.io/api/v1/quote?symbol=CL1!&token={api_key}"
        )
        oil_resp.raise_for_status()
        oil_data = oil_resp.json()

    return {
        "GOLD": float(gold_data["c"]),
        "OIL": float(oil_data["c"]),
    }


def trend_signal(price_change_7d: float) -> str:
    """Compute trend signal from 7-day price change percentage.

    > 3.0  -> bullish
    < -3.0 -> bearish
    else   -> neutral
    """
    if price_change_7d > 3.0:
        return "bullish"
    if price_change_7d < -3.0:
        return "bearish"
    return "neutral"


def compute_cross_correlations(
    alt_prices_history: dict[str, list[float]],
    equity_returns: pd.Series,
) -> dict[str, float]:
    """Compute Pearson correlation between each alt asset's returns and equity portfolio returns.

    alt_prices_history: {asset_ticker: [price_t0, price_t1, ...]}
    equity_returns: pd.Series of daily equity portfolio returns

    Returns {asset_ticker: correlation_coefficient} rounded to 4 decimal places.
    """
    if not alt_prices_history:
        return {}

    result: dict[str, float] = {}
    for ticker, prices in alt_prices_history.items():
        if len(prices) < 2:
            continue
        price_series = pd.Series(prices)
        asset_returns = price_series.pct_change().dropna()

        min_len = min(len(asset_returns), len(equity_returns))
        if min_len < 2:
            continue

        corr = asset_returns.iloc[-min_len:].corr(equity_returns.iloc[-min_len:])
        if pd.isna(corr):
            continue
        result[ticker] = round(float(corr), 4)

    return result


@alternatives_agent.on_message(model=AnalyzeAlternatives, replies={AlternativesResponse})
async def handle_analyze_alternatives(ctx: Context, sender: str, msg: AnalyzeAlternatives) -> None:
    import asyncio

    agent_id = "alternatives"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="AnalyzeAlternatives", description="Fetch crypto/commodity data",
        direction=MessageDirection.REQUEST,
    ))

    if MOCK_DATA or msg.mock:
        response = mock_alternatives_response()
    else:
        finnhub_api_key = os.environ["FINNHUB_API_KEY"]
        from agents.data.portfolio import CRYPTO_TICKERS, EQUITY_TICKERS

        push_sse_event(SSEEvent.agent_thought(agent_id, "Pulling crypto prices from CoinGecko..."))

        crypto_prices, change_7d = await asyncio.gather(
            fetch_crypto_prices(CRYPTO_TICKERS),
            return_exceptions=False,
        )
        # asyncio.gather with a single coroutine that returns a tuple
        prices, changes = crypto_prices

        btc_dominance, commodities = await asyncio.gather(
            fetch_btc_dominance(),
            fetch_commodity_prices(finnhub_api_key),
        )

        btc_price = prices.get("BTC", 0.0)
        btc_7d = changes.get("BTC", 0.0)
        btc_signal = trend_signal(btc_7d)
        push_sse_event(SSEEvent.agent_thought(
            agent_id,
            f"BTC at ${btc_price:,.0f} ({btc_7d:+.1f}% 7d) -- {btc_signal} signal",
        ))

        push_sse_event(SSEEvent.agent_thought(
            agent_id,
            f"BTC dominance: {btc_dominance:.1f}% -- altcoin rotation risk moderate",
        ))

        gold = commodities.get("GOLD", 0.0)
        oil = commodities.get("OIL", 0.0)
        push_sse_event(SSEEvent.agent_thought(
            agent_id,
            f"Gold ${gold:,.0f}, Oil ${oil:.0f} -- checking portfolio correlations...",
        ))

        import yfinance as yf

        equity_history = yf.download(
            EQUITY_TICKERS, period="3mo", progress=False, auto_adjust=True
        )["Close"]
        equity_returns_series = equity_history.mean(axis=1).pct_change().dropna()

        crypto_history_raw = yf.download(
            ["BTC-USD", "ETH-USD"], period="3mo", progress=False, auto_adjust=True
        )["Close"]

        alt_prices_history: dict[str, list[float]] = {}
        for cg_ticker, yf_symbol in [("BTC", "BTC-USD"), ("ETH", "ETH-USD")]:
            if yf_symbol in crypto_history_raw.columns:
                alt_prices_history[cg_ticker] = crypto_history_raw[yf_symbol].dropna().tolist()

        for etf_ticker, etf_symbol in [("GOLD", "GLD"), ("OIL", "USO")]:
            etf_hist = yf.download(etf_symbol, period="3mo", progress=False, auto_adjust=True)["Close"]
            alt_prices_history[etf_ticker] = etf_hist.dropna().tolist()

        cross_correlations = compute_cross_correlations(alt_prices_history, equity_returns_series)

        push_sse_event(SSEEvent.agent_thought(
            agent_id,
            f"Cross-asset correlations computed: BTC-portfolio {cross_correlations.get('BTC', 0.0):.2f}, "
            f"Gold-portfolio {cross_correlations.get('GOLD', 0.0):.2f}",
        ))

        trend_signals = {ticker: trend_signal(chg) for ticker, chg in changes.items()}

        response = AlternativesResponse(
            crypto_prices=prices,
            cross_correlations=cross_correlations,
            trend_signals=trend_signals,
            btc_dominance=btc_dominance,
            commodities=commodities,
        )

    push_sse_event(SSEEvent.agent_thought(agent_id, "Analysis complete."))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="AlternativesResponse", direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)

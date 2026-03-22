import os

import numpy as np
import yfinance as yf
from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.data.portfolio import EQUITY_TICKERS, MOCK_PORTFOLIO
from agents.mocks.portfolio import mock_portfolio_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
from agents.models.requests import AnalyzePortfolio
from agents.models.responses import PortfolioResponse
from agents.ports import PORTFOLIO_PORT

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

portfolio_agent = Agent(
    name="portfolio",
    seed="portfolio-agent-seed-investiswarm",
    port=PORTFOLIO_PORT,
)


def compute_sector_allocation(portfolio: list[dict]) -> dict[str, float]:
    """Group holdings by sector and sum weights. Crypto holdings map to 'Crypto'."""
    allocation: dict[str, float] = {}
    for holding in portfolio:
        if holding.get("type") == "crypto":
            sector = "Crypto"
        else:
            sector = holding["sector"]
        allocation[sector] = allocation.get(sector, 0.0) + holding["weight"]
    return allocation


def compute_herfindahl(weights: list[float]) -> float:
    """Herfindahl-Hirschman Index: sum of squared weights."""
    return float(np.sum(np.square(weights)))


def compute_top_holdings(portfolio: list[dict], n: int = 5) -> list[dict]:
    """Return the top n holdings sorted by weight descending."""
    sorted_holdings = sorted(portfolio, key=lambda h: h["weight"], reverse=True)
    return [
        {
            "ticker": h["ticker"],
            "weight": h["weight"],
            "sector": h.get("sector", h.get("type", "")),
        }
        for h in sorted_holdings[:n]
    ]


def compute_portfolio_beta(
    equity_tickers: list[str],
    weights: list[float],
    lookback_days: int = 365,
) -> float:
    """Compute portfolio beta vs SPY using historical close prices from yfinance."""
    period = f"{lookback_days}d"
    all_tickers = equity_tickers + ["SPY"]
    prices = yf.download(all_tickers, period=period, interval="1d", auto_adjust=True)

    # yfinance returns multi-level columns when multiple tickers requested
    if isinstance(prices.columns, tuple.__class__) or hasattr(prices.columns, "levels"):
        prices = prices["Close"]

    returns = prices.pct_change().dropna()

    equity_returns = returns[equity_tickers]
    spy_returns = returns["SPY"]

    portfolio_returns = (equity_returns * weights).sum(axis=1)

    data = np.vstack([portfolio_returns.values, spy_returns.values])
    cov = np.cov(data)
    beta = float(cov[0, 1] / cov[1, 1])
    return round(beta, 4)


def compute_correlation_matrix(
    equity_tickers: list[str],
    lookback_days: int = 90,
) -> dict[str, dict[str, float]]:
    """Compute pairwise return correlation across equities. Returns nested dict rounded to 4dp."""
    period = f"{lookback_days}d"
    prices = yf.download(equity_tickers, period=period, interval="1d", auto_adjust=True)

    if isinstance(prices.columns, tuple.__class__) or hasattr(prices.columns, "levels"):
        prices = prices["Close"]

    returns = prices.pct_change().dropna()
    corr_df = returns.corr()

    result: dict[str, dict[str, float]] = {}
    for ticker in equity_tickers:
        if ticker not in corr_df.columns:
            continue
        result[ticker] = {
            other: round(float(corr_df.loc[ticker, other]), 4)
            for other in equity_tickers
            if other in corr_df.columns
        }
    return result


@portfolio_agent.on_message(model=AnalyzePortfolio, replies={PortfolioResponse})
async def handle_analyze_portfolio(ctx: Context, sender: str, msg: AnalyzePortfolio) -> None:
    agent_id = "portfolio"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="AnalyzePortfolio", description=f"Analyze {len(msg.holdings)} holdings",
        direction=MessageDirection.REQUEST,
    ))

    if MOCK_DATA or msg.mock:
        response = mock_portfolio_response()
    else:
        push_sse_event(SSEEvent.agent_thought(
            agent_id, f"Loading portfolio: {len(MOCK_PORTFOLIO)} holdings across 6 sectors..."
        ))

        sector_allocation = compute_sector_allocation(MOCK_PORTFOLIO)
        sector_summary = ", ".join(
            f"{int(v * 100)}% {k}" for k, v in sorted(sector_allocation.items(), key=lambda x: -x[1])
        )
        push_sse_event(SSEEvent.agent_thought(
            agent_id, f"Sector allocation: {sector_summary}"
        ))

        equity_weights = [h["weight"] for h in MOCK_PORTFOLIO if h.get("type") != "crypto"]
        all_weights = [h["weight"] for h in MOCK_PORTFOLIO]
        hhi = compute_herfindahl(all_weights)
        concentration = "moderate concentration" if hhi < 0.18 else "high concentration"
        push_sse_event(SSEEvent.agent_thought(
            agent_id, f"Herfindahl index: {hhi:.3f} -- {concentration}"
        ))

        push_sse_event(SSEEvent.agent_thought(
            agent_id, "Computing 90-day correlation matrix across 10 equities..."
        ))

        correlation_matrix = compute_correlation_matrix(EQUITY_TICKERS, lookback_days=90)
        portfolio_beta = compute_portfolio_beta(EQUITY_TICKERS, equity_weights, lookback_days=365)

        push_sse_event(SSEEvent.agent_thought(
            agent_id, f"Portfolio beta: {portfolio_beta:.2f} vs SPY benchmark"
        ))

        top_holdings = compute_top_holdings(MOCK_PORTFOLIO, n=5)

        response = PortfolioResponse(
            sector_allocation=sector_allocation,
            top_holdings=top_holdings,
            herfindahl_index=hhi,
            portfolio_beta=portfolio_beta,
            correlation_matrix=correlation_matrix,
        )

    top_sector = max(sector_allocation, key=sector_allocation.get)
    top_pct = sector_allocation[top_sector]
    desc = (
        f"Beta {response.portfolio_beta:.2f}; "
        f"HHI {response.herfindahl_index:.3f}; "
        f"top sector {top_sector} ({top_pct:.0%}); "
        f"{len(response.top_holdings)} top holdings"
    )

    push_sse_event(SSEEvent.agent_thought(agent_id, "Analysis complete."))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="PortfolioResponse", description=desc,
        direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)

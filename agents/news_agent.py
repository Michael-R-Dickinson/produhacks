import os
from datetime import date, timedelta

import httpx
from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.mocks.news import mock_news_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
from agents.models.requests import FetchNews
from agents.models.responses import NewsResponse

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

news_agent = Agent(
    name="news",
    seed="news-agent-seed-investiswarm",
    port=8002,
)

# -- FinBERT lazy loader --

_finbert = None


def get_finbert():
    global _finbert
    if _finbert is None:
        from transformers import pipeline as hf_pipeline
        _finbert = hf_pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            return_all_scores=True,
        )
    return _finbert


# -- Live data functions --

async def fetch_finnhub_headlines(tickers: list[str], api_key: str) -> list[dict]:
    """Fetch market news and per-ticker company news from Finnhub, deduplicated."""
    today = date.today()
    week_ago = today - timedelta(days=7)
    seen_headlines: set[str] = set()
    combined: list[dict] = []

    def _normalise(item: dict) -> dict:
        return {
            "headline": item.get("headline", ""),
            "source": item.get("source", ""),
            "related": item.get("related", ""),
            "datetime": item.get("datetime", 0),
            "url": item.get("url", ""),
        }

    async with httpx.AsyncClient(timeout=10.0) as client:
        # General market news
        resp = await client.get(
            "https://finnhub.io/api/v1/news",
            params={"category": "general", "token": api_key},
        )
        if resp.status_code == 200:
            for item in resp.json():
                headline_text = item.get("headline", "")
                if headline_text and headline_text not in seen_headlines:
                    seen_headlines.add(headline_text)
                    combined.append(_normalise(item))

        # Per-ticker company news
        for ticker in tickers:
            resp = await client.get(
                "https://finnhub.io/api/v1/company-news",
                params={
                    "symbol": ticker,
                    "from": week_ago.isoformat(),
                    "to": today.isoformat(),
                    "token": api_key,
                },
            )
            if resp.status_code == 200:
                for item in resp.json():
                    headline_text = item.get("headline", "")
                    if headline_text and headline_text not in seen_headlines:
                        seen_headlines.add(headline_text)
                        combined.append(_normalise(item))

    return combined


def filter_headlines_for_tickers(headlines: list[dict], tickers: list[str]) -> list[dict]:
    """
    Keep headlines where any ticker appears in headline text or related field.
    Tags each kept headline with matched_tickers. Caps at 5 headlines per ticker.
    """
    ticker_counts: dict[str, int] = {t: 0 for t in tickers}
    result: list[dict] = []

    for raw_headline in headlines:
        text = raw_headline.get("headline", "")
        related = raw_headline.get("related", "")
        matched = []

        for ticker in tickers:
            if ticker.lower() in text.lower() or ticker.upper() in related.upper().split(","):
                matched.append(ticker)

        if not matched:
            continue

        # Apply per-ticker cap — only include headline if at least one ticker is under cap
        eligible_tickers = [t for t in matched if ticker_counts[t] < 5]
        if not eligible_tickers:
            continue

        headline = dict(raw_headline)
        headline["matched_tickers"] = eligible_tickers
        result.append(headline)

        for t in eligible_tickers:
            ticker_counts[t] += 1

    return result


def score_sentiment(text: str) -> float:
    """Run FinBERT on text, return positive - negative score in [-1, 1]."""
    results = get_finbert()(text[:512])[0]
    scores = {r["label"]: r["score"] for r in results}
    return scores.get("positive", 0.0) - scores.get("negative", 0.0)


def score_headlines(headlines: list[dict]) -> list[dict]:
    """Score each headline with FinBERT sentiment. Discard near-neutral (abs < 0.1)."""
    scored = []
    for h in headlines:
        sentiment = score_sentiment(h["headline"])
        if abs(sentiment) < 0.1:
            continue
        item = dict(h)
        item["sentiment"] = sentiment
        scored.append(item)
    return scored


def aggregate_sentiment_by_ticker(scored_headlines: list[dict]) -> dict[str, float]:
    """Group by matched_tickers and compute mean sentiment per ticker."""
    ticker_scores: dict[str, list[float]] = {}
    for h in scored_headlines:
        sentiment = h.get("sentiment", 0.0)
        for ticker in h.get("matched_tickers", []):
            ticker_scores.setdefault(ticker, []).append(sentiment)

    return {
        ticker: sum(scores) / len(scores)
        for ticker, scores in ticker_scores.items()
    }


def compute_overall_sentiment(aggregate: dict[str, float]) -> float:
    """Return mean of all per-ticker sentiment scores."""
    if not aggregate:
        return 0.0
    values = list(aggregate.values())
    return sum(values) / len(values)


@news_agent.on_message(model=FetchNews, replies={NewsResponse})
async def handle_fetch_news(ctx: Context, sender: str, msg: FetchNews) -> None:
    agent_id = "news"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="FetchNews", description=f"Fetch news for {msg.tickers}",
        direction=MessageDirection.REQUEST,
    ))

    if MOCK_DATA or msg.mock:
        push_sse_event(SSEEvent.agent_thought(agent_id, f"Fetching news for {msg.tickers}..."))
        response = mock_news_response()
    else:
        api_key = os.environ["FINNHUB_API_KEY"]
        tickers = msg.tickers

        push_sse_event(SSEEvent.agent_thought(agent_id, f"Scanning Finnhub for {len(tickers)} tickers..."))

        raw = await fetch_finnhub_headlines(tickers, api_key)
        filtered = filter_headlines_for_tickers(raw, tickers)

        push_sse_event(SSEEvent.agent_thought(
            agent_id,
            f"Found {len(filtered)} relevant headlines across {len(tickers)} holdings",
        ))

        scored = score_headlines(filtered)
        aggregate = aggregate_sentiment_by_ticker(scored)
        overall = compute_overall_sentiment(aggregate)

        # Punchy FinBERT teaser
        top_items = sorted(aggregate.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        teaser_parts = ", ".join(
            f"{t} sentiment {'+' if v >= 0 else ''}{v:.2f}" for t, v in top_items
        )
        push_sse_event(SSEEvent.agent_thought(agent_id, f"FinBERT scoring: {teaser_parts}"))

        sentiment_label = "bullish" if overall > 0 else "bearish"
        push_sse_event(SSEEvent.agent_thought(
            agent_id,
            f"Overall market sentiment: {'+' if overall >= 0 else ''}{overall:.2f} (mildly {sentiment_label})",
        ))

        # Normalise headlines for response
        headlines_out = [
            {
                "title": h["headline"],
                "sentiment": h["sentiment"],
                "ticker": h["matched_tickers"][0] if h["matched_tickers"] else "",
            }
            for h in scored
        ]

        response = NewsResponse(
            headlines=headlines_out,
            aggregate_sentiment=aggregate,
            overall_sentiment=overall,
        )

    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="NewsResponse", direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)

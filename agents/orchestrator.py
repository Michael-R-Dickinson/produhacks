import asyncio
import json
import logging

from google import genai
from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.models.events import AgentStatus, SSEEvent
from uagents import Model as UAgentModel

from agents.models.requests import (
    AnalyzeAlternatives,
    AnalyzePortfolio,
    FetchNews,
    ReportRequest,
    RunModel,
)
from agents.ports import ORCHESTRATOR_PORT


class ReportResponse(UAgentModel):
    status: str


from agents.models.responses import (
    AlternativesResponse,
    ModelResponse,
    NewsResponse,
    PortfolioResponse,
)
from agents.mocks.alternatives import mock_alternatives_response
from agents.mocks.modeling import mock_model_response
from agents.mocks.news import mock_news_response
from agents.mocks.portfolio import mock_portfolio_response

logger = logging.getLogger(__name__)

orchestrator = Agent(
    name="orchestrator",
    seed="orchestrator-agent-seed-investiswarm",
    port=ORCHESTRATOR_PORT,
)

from agents.portfolio_agent import portfolio_agent
from agents.news_agent import news_agent
from agents.modeling_agent import modeling_agent
from agents.alternatives_agent import alternatives_agent

PORTFOLIO_ADDR = portfolio_agent.address
NEWS_ADDR = news_agent.address
MODELING_ADDR = modeling_agent.address
ALT_ADDR = alternatives_agent.address

_gemini: genai.Client | None = None


def get_gemini() -> genai.Client:
    """Lazy-initialize the Gemini client so module import doesn't fail without the key."""
    global _gemini
    if _gemini is None:
        _gemini = genai.Client()  # reads GEMINI_API_KEY from env
    return _gemini


def safe_result(result, fallback):
    """Return fallback if result is an Exception, otherwise return result."""
    if isinstance(result, Exception):
        logger.warning("Agent call failed: %s — using fallback", result)
        return fallback
    return result


def detect_contradictions(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    modeling: ModelResponse,
) -> list[str]:
    """Detect cross-agent contradictions between news sentiment and portfolio/modeling data."""
    contradictions = []

    # Build ticker -> weight lookup from top_holdings
    ticker_weights = {
        h["ticker"]: h.get("weight", 0.0) for h in portfolio.top_holdings
    }

    for ticker, sentiment in news.aggregate_sentiment.items():
        weight = ticker_weights.get(ticker, 0.0)

        # Bearish news on a significant holding
        if sentiment < -0.3 and weight > 0.05:
            contradictions.append(
                f"{ticker}: News sentiment is bearish ({sentiment:.2f}) but it is a top holding"
                f" ({weight * 100:.0f}% of portfolio)"
            )

        # Bullish news but negative portfolio momentum
        elif sentiment > 0.5 and modeling.trend_slope < 0:
            contradictions.append(
                f"{ticker}: News sentiment is bullish ({sentiment:.2f}) but portfolio momentum"
                f" is declining"
            )

    return contradictions


def build_synthesis_prompt(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    modeling: ModelResponse,
    alt: AlternativesResponse,
    contradictions: list[str],
    chart_embeds: list[str],
) -> str:
    """Build the LLM synthesis prompt from all agent data."""
    system_msg = (
        "You are a professional financial analyst writing a morning brief for a portfolio manager."
    )

    instructions = """Organize the report into thematic sections by investment theme (NOT by data source agent). Required sections:
1. Executive Summary (3-4 sentences, key actionable insights)
2. 2-3 thematic sections (e.g., "Tech Sector Outlook", "Risk Assessment", "Market Sentiment & Momentum")
3. Alternative Assets & Market Context
4. Notable Contradictions (if any detected)

Do not section by data source. Weave all data into a unified narrative. Use a professional analyst tone.
Keep the report to 600-800 words for 2-3 screens of content."""

    modeling_data = modeling.model_dump()
    modeling_data.pop("charts", None)  # charts are embedded separately via chart_embeds
    data_block = json.dumps(
        {
            "portfolio": portfolio.model_dump(),
            "news": news.model_dump(),
            "modeling": modeling_data,
            "alternatives": alt.model_dump(),
            "contradictions": contradictions,
        },
        indent=2,
    )

    prompt_parts = [
        system_msg,
        "",
        instructions,
        "",
        "## Agent Data",
        data_block,
    ]

    if chart_embeds:
        prompt_parts += [
            "",
            "## Chart Embeds",
            "Include these chart embeds at appropriate locations in the report:",
            *chart_embeds,
        ]

    if contradictions:
        prompt_parts += [
            "",
            "## Detected Contradictions",
            *contradictions,
        ]

    return "\n".join(prompt_parts)


async def synthesize_report(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    modeling: ModelResponse,
    alt: AlternativesResponse,
    contradictions: list[str],
    charts,
) -> str:
    """Call Gemini to synthesize a unified thematic narrative."""
    chart_embeds = [
        f"![{c.title}](data:image/png;base64,{c.image_base64})"
        for c in charts
        if c.image_base64
    ]

    prompt = build_synthesis_prompt(portfolio, news, modeling, alt, contradictions, chart_embeds)

    response = await get_gemini().aio.models.generate_content(
        model="gemini-flash-3.1-lite",
        system_instruction="You are a professional financial analyst writing a morning brief for a portfolio manager.",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            max_output_tokens=2000,
            temperature=0.4,
        ),
    )

    return response.text


@orchestrator.on_rest_post("/report", ReportRequest, ReportResponse)
async def handle_report(ctx: Context, req: ReportRequest) -> ReportResponse:
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Dispatching to 4 domain agents concurrently..."))

    # Fan-out to all domain agents concurrently
    results = await asyncio.gather(
        ctx.send_and_receive(PORTFOLIO_ADDR, AnalyzePortfolio(holdings=req.holdings, mock=req.mock), timeout=30),
        ctx.send_and_receive(NEWS_ADDR, FetchNews(tickers=req.holdings, mock=req.mock), timeout=30),
        ctx.send_and_receive(MODELING_ADDR, RunModel(holdings=req.holdings, mock=req.mock), timeout=30),
        ctx.send_and_receive(ALT_ADDR, AnalyzeAlternatives(mock=req.mock), timeout=30),
        return_exceptions=True,
    )

    # ctx.send_and_receive returns (message, sender) tuple in uAgents 0.24.0
    # Extract message from tuple if not an exception
    def extract_msg(result):
        if isinstance(result, Exception):
            return result
        if isinstance(result, tuple):
            return result[0]
        return result

    portfolio_data = safe_result(extract_msg(results[0]), mock_portfolio_response())
    news_data = safe_result(extract_msg(results[1]), mock_news_response())
    modeling_data = safe_result(extract_msg(results[2]), mock_model_response())
    alt_data = safe_result(extract_msg(results[3]), mock_alternatives_response())

    push_sse_event(SSEEvent.agent_thought(
        "orchestrator",
        f"All agents responded. Analyzing {len(news_data.headlines)} headlines, {len(portfolio_data.sector_allocation)} sectors...",
    ))

    # Contradiction detection
    contradictions = detect_contradictions(portfolio_data, news_data, modeling_data)
    if contradictions:
        push_sse_event(SSEEvent.agent_thought(
            "orchestrator",
            f"Flagging {len(contradictions)} cross-agent contradictions",
        ))

    # LLM synthesis
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Synthesizing unified narrative with Gemini..."))
    report_markdown = await synthesize_report(
        portfolio_data, news_data, modeling_data, alt_data,
        contradictions, modeling_data.charts,
    )

    push_sse_event(SSEEvent.agent_thought("orchestrator", "Report complete. Delivering to client."))

    # Push completed report via SSE
    push_sse_event(SSEEvent.report_complete(
        markdown=report_markdown,
        charts=[c.model_dump() for c in modeling_data.charts],
    ))
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.DONE))

    return ReportResponse(status="complete")

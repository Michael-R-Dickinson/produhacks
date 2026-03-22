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
    seed="orchestrator-agent-seed-Wealth Council",
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
        import os

        _gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _gemini


def safe_result(result, fallback):
    """Return fallback if result is an Exception or None, otherwise return result."""
    if result is None or isinstance(result, Exception):
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
    ticker_weights = {h["ticker"]: h.get("weight", 0.0) for h in portfolio.top_holdings}

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


AVAILABLE_CHARTS: dict[str, str] = {
    "regression": "Linear regression of portfolio value over time with OLS trend line. Shows momentum direction and R-squared fit.",
    "correlation_matrix": "Heatmap of pairwise correlations between holdings. Reveals concentration risk and diversification gaps.",
    "sector_performance": "Bar chart comparing returns across holdings/sectors. Highlights winners, losers, and relative performance.",
    "volatility_cone": "Historical realized-volatility percentiles by tenor. Shows whether current vol is elevated vs. history.",
    "price_history": "Normalized price paths for individual holdings overlaid. Shows relative performance and divergence.",
}


async def plan_chart_selection(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    alt: AlternativesResponse,
) -> list[str]:
    """Ask Gemini which charts are most relevant given the data from the non-modeling agents."""
    chart_descriptions = "\n".join(
        f"- `{key}`: {desc}" for key, desc in AVAILABLE_CHARTS.items()
    )

    data_summary = json.dumps(
        {
            "portfolio": portfolio.model_dump(),
            "news": news.model_dump(),
            "alternatives": alt.model_dump(),
        },
        indent=2,
    )

    prompt = f"""You are helping an orchestrator agent decide which financial charts to generate for a portfolio report.

Given the data below from three domain agents (portfolio analysis, news sentiment, and alternative assets), select which charts would be most valuable for the final report.

## Available Chart Types
{chart_descriptions}

## Agent Data
{data_summary}

## Instructions
- Select 3-5 chart types that are most relevant to the data and would tell the most compelling visual story.
- If correlations between holdings are notable (many holdings, or concentrated sectors), include `correlation_matrix`.
- If there are clear winners/losers in the portfolio, include `sector_performance`.
- If news sentiment is mixed or contradictory, include `price_history` to show recent divergence.
- Always include `regression` as a baseline trend view.
- If volatility or risk is a theme in the news or portfolio data, include `volatility_cone`.

Respond with ONLY a JSON array of chart type strings, nothing else. Example: ["regression", "correlation_matrix", "sector_performance"]"""

    response = await get_gemini().aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            max_output_tokens=200,
            temperature=0.1,
        ),
    )

    raw = response.text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    try:
        selected = json.loads(raw)
        # Validate against known chart types
        return [s for s in selected if s in AVAILABLE_CHARTS]
    except (json.JSONDecodeError, TypeError):
        logger.warning(
            "Chart planning LLM returned unparseable response: %s — using all charts",
            raw,
        )
        return list(AVAILABLE_CHARTS.keys())


KNOWLEDGE_LEVEL_INSTRUCTIONS: dict[int, str] = {
    1: (
        "CRITICAL: You are writing for someone with ZERO financial background — treat them like a smart 12-year-old."
        "\n\nYOU MUST:\n"
        "- Use plain, everyday English ONLY. No jargon whatsoever.\n"
        "- Define EVERY financial term immediately in plain language (e.g., 'beta — basically, how wild the stock rides compared to the market').\n"
        "- Replace all metrics with relatable analogies (e.g., instead of 'Sharpe ratio 1.4', say 'you earn 1.40 of return for every 1.00 of risk — a good deal').\n"
        "- Use short sentences (max 20 words each).\n"
        "- Spell out what every number MEANS for the reader's money in plain terms.\n"
        "\nYOU MUST NOT:\n"
        "- Use any unexplained acronyms (P/E, HHI, OLS, YTD, etc.)\n"
        "- Assume the reader knows what a hedge, beta, correlation, or Sharpe ratio is.\n"
        "- Use dense data-heavy sentences."
    ),
    2: (
        "You are writing for someone who knows what stocks and bonds are, and has heard of diversification, but is not a finance professional."
        "\n\nYOU MUST:\n"
        "- Use plain language as the default, with light jargon only where it saves space.\n"
        "- Briefly define technical terms the FIRST time you use them (e.g., 'beta (market sensitivity)').\n"
        "- Focus on what this means for the reader's portfolio in practical terms, not just the raw numbers.\n"
        "- Keep explanations accessible — avoid assuming knowledge beyond basic investing.\n"
        "\nYOU MUST NOT:\n"
        "- Drop advanced metrics (Sharpe, HHI, OLS) without a brief explanation.\n"
        "- Use jargon-heavy sentences that require re-reading to understand."
    ),
    3: (
        "You are writing for an informed investor who is comfortable with standard financial concepts: P/E ratios, diversification, beta, sentiment, and basic portfolio theory."
        "\n\nYOU MUST:\n"
        "- Use standard analyst language and financial terminology freely.\n"
        "- Be direct and data-driven, citing metrics where they add clarity.\n"
        "- Weave analysis and implications together naturally.\n"
        "\nYOU MUST NOT:\n"
        "- Over-explain well-known concepts like beta or correlation.\n"
        "- Use institutional/quant jargon without brief context."
    ),
    4: (
        "You are writing for a finance professional who is deeply familiar with advanced metrics and portfolio management."
        "\n\nYOU MUST:\n"
        "- Use dense, precise analyst language. Be concise and data-driven.\n"
        "- Freely reference Sharpe ratios, Herfindahl index, correlation matrices, factor exposure, momentum, drawdowns, and vol surfaces.\n"
        "- Prioritize information density over hand-holding.\n"
        "- Frame insights as actionable signals, not educational explanations.\n"
        "\nYOU MUST NOT:\n"
        "- Waste words explaining standard metrics.\n"
        "- Soften technical language for accessibility."
    ),
    5: (
        "You are writing for a quantitative/institutional audience — portfolio managers, quants, and risk analysts with deep expertise."
        "\n\nYOU MUST:\n"
        "- Use the densest, most precise financial and statistical language possible.\n"
        "- Use Greek letters (α, β, σ, ρ), factor decomposition, regime terminology (fat tails, convexity, mean reversion), and institutional framing.\n"
        "- Maximize information per sentence. No hand-holding.\n"
        "- Frame everything in terms of risk-adjusted return, factor exposure, and portfolio construction implications.\n"
        "\nYOU MUST NOT:\n"
        "- Define any standard financial concept.\n"
        "- Use conversational or softened language."
    ),
}


def build_synthesis_prompt(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    modeling: ModelResponse,
    alt: AlternativesResponse,
    contradictions: list[str],
    chart_refs: list[dict[str, str]],
    knowledge_level: int,
) -> str:
    """Build the LLM synthesis prompt from all agent data."""
    system_msg = "You are a professional financial analyst writing a morning brief for a portfolio manager."

    audience_instruction = KNOWLEDGE_LEVEL_INSTRUCTIONS.get(
        knowledge_level, KNOWLEDGE_LEVEL_INSTRUCTIONS[3]
    )

    instructions = f"""## Audience & Tone
{audience_instruction}

Organize the report into thematic sections by investment theme (NOT by data source agent). Required sections:
1. Executive Summary (3-4 sentences, key actionable insights)
2. 2-3 thematic sections (e.g., "Tech Sector Outlook", "Risk Assessment", "Market Sentiment & Momentum")
3. Alternative Assets & Market Context
4. Notable Contradictions (if any detected)

Do not section by data source. Weave all data into a unified narrative.
Keep the report to 600-800 words for 2-3 screens of content.

## Formatting Requirements
Make the report visually rich and scannable. Use markdown formatting generously:
- Use **bold** for key metrics, ticker symbols, and critical data points (e.g., **AAPL +3.2%**, **Sharpe ratio: 1.4**)
- Use *italics* for analyst commentary, caveats, and qualitative assessments (e.g., *sentiment has shifted bearish since Q3*)
- Use `inline code` for exact figures, prices, and percentages when they appear mid-sentence (e.g., the portfolio returned `12.4%`)
- Use > blockquotes for key takeaways or notable contradictions that deserve emphasis
- Use horizontal rules (---) between major thematic sections for clear visual separation
- Use bullet lists and numbered lists liberally to break up dense information
- Where data naturally forms comparisons, use markdown tables (e.g., sector weights, top/bottom performers, before/after metrics)
- Use ### subheadings within sections to create hierarchy and aid scanning
- Highlight risks or warnings with **bold** and frame them clearly (e.g., **Risk:** *correlation between top holdings exceeds 0.8*)"""

    modeling_data = modeling.model_dump()
    modeling_data.pop("charts", None)  # charts sent separately as references
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

    if chart_refs:
        chart_lines = [
            f'- [chart:{r["chart_id"]}] "{r["title"]}": {r["summary"]}'
            for r in chart_refs
        ]
        prompt_parts += [
            "",
            "## Available Charts",
            "You MUST embed every available chart in the report — do not skip any.",
            "Place each chart reference at the most contextually relevant location in the report.",
            "Use the exact syntax [chart:<id>] on its own line to embed each chart.",
            "Charts should appear immediately after the paragraph that discusses their data, never clustered at the end.",
            *chart_lines,
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
    knowledge_level: int = 2,
) -> str:
    """Call Gemini to synthesize a unified thematic narrative."""
    chart_refs = [
        {"chart_id": c.chart_id, "title": c.title, "summary": c.summary}
        for c in charts
        if c.image_base64
    ]

    prompt = build_synthesis_prompt(
        portfolio, news, modeling, alt, contradictions, chart_refs, knowledge_level
    )

    response = await get_gemini().aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction="You are a professional financial analyst writing a morning brief for a portfolio manager.",
            max_output_tokens=8000,
            temperature=0.4,
        ),
    )

    return response.text


@orchestrator.on_rest_post("/report", ReportRequest, ReportResponse)
async def handle_report(ctx: Context, req: ReportRequest) -> ReportResponse:
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.WORKING))
    push_sse_event(
        SSEEvent.agent_thought(
            "orchestrator", "Dispatching to portfolio, news, and alternatives agents..."
        )
    )

    # --- Phase 1: Fan-out to non-modeling agents concurrently ---
    phase1_results = await asyncio.gather(
        ctx.send_and_receive(
            PORTFOLIO_ADDR,
            AnalyzePortfolio(holdings=req.holdings, mock=req.mock),
            response_type=PortfolioResponse,
            timeout=30,
        ),
        ctx.send_and_receive(
            NEWS_ADDR,
            FetchNews(tickers=req.holdings, mock=req.mock),
            response_type=NewsResponse,
            timeout=30,
        ),
        ctx.send_and_receive(
            ALT_ADDR,
            AnalyzeAlternatives(mock=req.mock),
            response_type=AlternativesResponse,
            timeout=30,
        ),
        return_exceptions=True,
    )

    def extract_msg(result):
        if isinstance(result, Exception):
            return result
        if isinstance(result, tuple):
            return result[0]
        return result

    portfolio_data = safe_result(
        extract_msg(phase1_results[0]), mock_portfolio_response()
    )
    news_data = safe_result(extract_msg(phase1_results[1]), mock_news_response())
    alt_data = safe_result(extract_msg(phase1_results[2]), mock_alternatives_response())

    push_sse_event(
        SSEEvent.agent_thought(
            "orchestrator",
            f"3 agents responded. Analyzing {len(news_data.headlines)} headlines, {len(portfolio_data.sector_allocation)} sectors...",
        )
    )

    # --- Phase 2: Ask Gemini which charts to generate ---
    push_sse_event(
        SSEEvent.agent_thought(
            "orchestrator",
            "Consulting Gemini to plan chart selection based on agent data...",
        )
    )
    selected_charts = await plan_chart_selection(portfolio_data, news_data, alt_data)
    push_sse_event(
        SSEEvent.agent_thought(
            "orchestrator",
            f"Chart plan decided: {', '.join(selected_charts)}. Dispatching to modeling agent...",
        )
    )

    # --- Phase 3: Send targeted request to modeling agent ---
    modeling_result = await ctx.send_and_receive(
        MODELING_ADDR,
        RunModel(holdings=req.holdings, analyses=selected_charts, mock=req.mock),
        response_type=ModelResponse,
        timeout=30,
    )
    modeling_data = safe_result(extract_msg(modeling_result), mock_model_response())

    push_sse_event(
        SSEEvent.agent_thought(
            "orchestrator",
            f"Modeling agent returned {len(modeling_data.charts)} charts. Preparing final synthesis...",
        )
    )

    # Contradiction detection
    contradictions = detect_contradictions(portfolio_data, news_data, modeling_data)
    if contradictions:
        push_sse_event(
            SSEEvent.agent_thought(
                "orchestrator",
                f"Flagging {len(contradictions)} cross-agent contradictions",
            )
        )

    # --- Phase 4: LLM synthesis with all data + targeted charts ---
    push_sse_event(
        SSEEvent.agent_thought(
            "orchestrator", "Synthesizing unified narrative with Gemini..."
        )
    )
    report_markdown = await synthesize_report(
        portfolio_data,
        news_data,
        modeling_data,
        alt_data,
        contradictions,
        modeling_data.charts,
        req.knowledge_level,
    )

    push_sse_event(
        SSEEvent.agent_thought("orchestrator", "Report complete. Delivering to client.")
    )
    logger.info(
        "Sending report.complete — markdown length: %d, charts: %d",
        len(report_markdown),
        len(modeling_data.charts),
    )

    # Push completed report via SSE
    push_sse_event(
        SSEEvent.report_complete(
            markdown=report_markdown,
            charts=[c.model_dump() for c in modeling_data.charts],
        )
    )
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.DONE))

    return ReportResponse(status="complete")

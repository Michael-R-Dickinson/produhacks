⏺ Looking at the current contract, RunModel is pretty bare:

  class RunModel(Model):
      holdings: list[str]  # e.g. ["AAPL", "MSFT", "NVDA"]
      mock: bool = False

  That's it. It just gets a list of ticker symbols and a mock flag. The agent then decides internally what to do -- fetch historical prices via yfinance, run regression, compute
  Sharpe/volatility, generate a chart.

  There's no way to say "run a Monte Carlo" vs "run a backtest" vs "just give me the regression." It's a single hardcoded pipeline: tickers in, ModelResponse out.

  Is that the right call? For a 24h hackathon, probably yes -- one preset analysis path keeps it simple. But if you're thinking about it, here's what the alternative looks like:

  # Option A: Current (implicit single pipeline)
  class RunModel(Model):
      holdings: list[str]
      mock: bool = False

  # Option B: Explicit model selection
  class RunModel(Model):
      holdings: list[str]
      analysis: str = "regression"  # "regression" | "backtest" | "correlation"
      lookback_days: int = 365
      mock: bool = False

  Option B would let the orchestrator (or chat queries) ask for specific analyses, and it maps better to ORCH-01 ("dispatches to appropriate domain agents based on report request or
  chat query"). But it also means the modeling agent needs to branch internally, and the response shape might vary per analysis type.

  The response is also flat right now:

  class ModelResponse(Model):
      sharpe_ratio: float
      volatility: float
      trend_slope: float
      chart_base64: str | None = None

  No room for multiple charts, no labels on what the chart shows, no per-holding breakdown. If someone asks "how is AAPL trending vs NVDA?" in chat, this response can't express that.

  The question for your team: Is the modeling agent a black box that always runs the same analysis, or should it accept parameters that let the orchestrator/chat route specific
  questions to it? That decision changes the contract before Phase 1 executes.

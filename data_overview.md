# Modeling Agent -- Data Contract

## Request: `RunModel`

The orchestrator (which has the LLM) decides which analyses to request. The modeling agent executes them -- no LLM involved.

```python
class RunModel(Model):
    holdings: list[str]            # Ticker symbols, e.g. ["AAPL", "MSFT", "NVDA"]
    analyses: list[str] = ["regression"]  # Which chart/analysis types to run
    lookback_days: int = 365       # Historical window for price data
    mock: bool = False             # Return mock fixtures instead of live data
```

### Available Analysis Types (Chart Registry)

| Key | What It Does | Data Source |
|-----|-------------|-------------|
| `regression` | Linear regression + trend line on portfolio value | yfinance historical prices |
| `correlation_matrix` | Heatmap of inter-holding correlations | yfinance historical prices |
| `sector_performance` | Bar chart comparing sector returns | yfinance + sector mapping |
| `volatility_cone` | Forward-looking volatility bands | yfinance historical prices |
| `price_history` | Overlay line chart of holding price histories | yfinance historical prices |

New chart types are added by writing one function and registering it -- teammates can add these independently.

## Response: `ModelResponse`

```python
class ChartOutput(Model):
    chart_type: str       # Matches the analysis key that produced it (e.g. "regression")
    title: str            # Human-readable title (e.g. "Portfolio Linear Regression (1Y)")
    image_base64: str     # PNG encoded as base64 string
    summary: str          # One-line description for the orchestrator to weave into the narrative

class ModelResponse(Model):
    holdings_analyzed: list[str]     # Echo back which tickers were analyzed
    sharpe_ratio: float              # Portfolio Sharpe ratio
    volatility: float                # Annualized portfolio volatility
    trend_slope: float               # Regression slope coefficient
    charts: list[ChartOutput]        # One per requested analysis type
    metrics: dict[str, float]        # Extensible key-value for additional metrics
```

### `metrics` Dict -- Known Keys

| Key | Description |
|-----|-------------|
| `r_squared` | Regression fit quality |
| `max_drawdown` | Largest peak-to-trough decline |
| `beta` | Portfolio beta vs benchmark |

This dict is intentionally open-ended -- new metrics can be added without changing the model schema.

## Data Flow

```
Orchestrator                    Modeling Agent
    |                               |
    |-- RunModel ------------------->|
    |   holdings: ["AAPL", "MSFT"]  |
    |   analyses: ["regression",    |
    |     "correlation_matrix"]     |
    |   lookback_days: 365          |
    |                               |-- yfinance fetch
    |                               |-- run regression
    |                               |-- generate charts
    |                               |-- compute metrics
    |<-- ModelResponse -------------|
    |   sharpe_ratio: 1.34          |
    |   volatility: 0.187           |
    |   charts: [                   |
    |     ChartOutput(regression),  |
    |     ChartOutput(corr_matrix)  |
    |   ]                           |
    |   metrics: {r_squared: 0.74}  |
```

## Key Design Decisions

- **No LLM in the modeling agent.** The orchestrator's LLM picks which analyses to request. The modeling agent is pure computation.
- **`ChartOutput.summary` exists so the orchestrator can describe charts in the narrative** without needing to "see" the image.
- **`metrics` is a dict, not named fields,** so new computed values don't require schema changes.
- **`analyses` is a list** -- the orchestrator can request multiple chart types in a single call rather than making separate requests.

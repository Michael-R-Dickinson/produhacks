"""Deterministic charting and risk metrics for the Modeling uAgent.

Uses **yfinance** for live paths when ``use_mock=False`` and data loads successfully;
otherwise falls back to synthetic series (same as explicit mock mode).

Architecture: see ``.planning/research/ARCHITECTURE.md`` — Modeling agent charting;
orchestrator LLM chooses ``RunModel.analyses``. No LLM in this module.
"""

from __future__ import annotations

import base64
import io
from collections.abc import Callable, Sequence
from typing import NamedTuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from agents.modeling_data import load_adjusted_close_matrix
from agents.models.requests import RunModel
from agents.models.responses import ChartOutput, ModelResponse

# ---------------------------------------------------------------------------
# PNG helpers
# ---------------------------------------------------------------------------


def fig_to_base64_png(fig: matplotlib.figure.Figure, *, dpi: int = 120) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return base64.standard_b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# Chart input bundle (optional yfinance OHLCV-derived levels)
# ---------------------------------------------------------------------------


class PricePanel(NamedTuple):
    """Aligned adjusted closes: shape (T, K), columns match ``symbols``."""

    levels: np.ndarray
    symbols: list[str]


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _placeholder_metrics(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
) -> tuple[float, float, float, dict[str, float]]:
    _ = lookback_days
    base = 1.34 + (0.01 if not mock else 0) * min(len(holdings), 5)
    vol = 0.187 - (0.002 if not mock else 0) * min(len(holdings), 5)
    slope = 0.0023
    metrics: dict[str, float] = {
        "r_squared": 0.74 if mock else 0.71,
        "max_drawdown": -0.12,
        "beta": 1.05 + 0.01 * min(len(holdings), 3),
    }
    return float(base), float(vol), float(slope), metrics


def estimate_metrics(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None = None,
) -> tuple[float, float, float, dict[str, float]]:
    if mock or panel is None or panel.levels.shape[0] < 3 or panel.levels.shape[1] < 1:
        return _placeholder_metrics(holdings, lookback_days, mock=mock)

    prices = np.clip(panel.levels, 1e-9, None)
    log_ret = np.diff(np.log(prices), axis=0)
    if log_ret.size == 0:
        return _placeholder_metrics(holdings, lookback_days, mock=mock)

    port = log_ret.mean(axis=1)
    mu = float(np.mean(port))
    sd = float(np.std(port) + 1e-12)
    sharpe = mu / sd * np.sqrt(252.0)
    vol_ann = sd * np.sqrt(252.0)

    ew = (prices / prices[0]).mean(axis=1)
    days = np.arange(len(ew), dtype=float)
    coef = np.polyfit(days, ew, 1)
    trend = np.poly1d(coef)(days)
    slope = float(coef[0])
    r2 = float(np.corrcoef(ew, trend)[0, 1] ** 2) if len(ew) > 2 else 0.0
    peak = np.maximum.accumulate(ew)
    max_dd = float(np.min(ew / peak - 1.0))

    metrics = {
        "r_squared": r2,
        "max_drawdown": max_dd,
        "beta": 1.0,
    }
    return float(sharpe), float(vol_ann), slope, metrics


# ---------------------------------------------------------------------------
# Chart renderers
# ---------------------------------------------------------------------------


def _render_regression(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None,
) -> ChartOutput:
    n_points = max(2, lookback_days)
    if panel is not None and panel.levels.shape[0] >= 3:
        ew = (panel.levels / panel.levels[0]).mean(axis=1)
        days = np.arange(len(ew))
        coef = np.polyfit(days, ew, 1)
        trend = np.poly1d(coef)(days)
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(days, ew, color="#2563eb", linewidth=1.2, label="Equal-weight (yfinance)")
        ax.plot(days, trend, "--", color="#dc2626", linewidth=1.5, label="OLS trend")
        ax.set_xlabel("Trading days")
        ax.set_ylabel("Normalized index")
        ax.set_title(f"Linear regression — {len(panel.symbols)} holdings, {len(ew)}d (yfinance)")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.25)
        b64 = fig_to_base64_png(fig)
        r2 = float(np.corrcoef(ew, trend)[0, 1] ** 2)
        return ChartOutput(
            chart_type="regression",
            title=f"Portfolio linear regression ({len(ew)}d)",
            image_base64=b64,
            summary=f"Equal-weight portfolio from yfinance; OLS trend R²≈{r2:.2f}.",
        )

    rng = np.random.default_rng(42 if mock else 7)
    days = np.arange(n_points)
    noise = rng.normal(0, 0.008, size=n_points)
    walk = 100 * np.exp(np.cumsum(0.0003 + noise))
    coef = np.polyfit(days, walk, 1)
    trend = np.poly1d(coef)(days)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(days, walk, color="#2563eb", linewidth=1.2, label="Portfolio (synthetic)")
    ax.plot(days, trend, "--", color="#dc2626", linewidth=1.5, label="OLS trend")
    ax.set_xlabel("Trading days")
    ax.set_ylabel("Synthetic value")
    suffix = " (mock)" if mock else ""
    ax.set_title(f"Linear regression — {len(holdings)} holdings, {n_points}d{suffix}")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.25)
    b64 = fig_to_base64_png(fig)
    r2 = float(np.corrcoef(walk, trend)[0, 1] ** 2)
    return ChartOutput(
        chart_type="regression",
        title=f"Portfolio linear regression ({n_points}d)",
        image_base64=b64,
        summary=f"Synthetic path with OLS trend; approximate R² {r2:.2f}.",
    )


def _render_correlation_matrix(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None,
) -> ChartOutput:
    _ = lookback_days
    if panel is not None and panel.levels.shape[1] >= 2 and panel.levels.shape[0] >= 5:
        rets = np.diff(np.log(np.clip(panel.levels, 1e-9, None)), axis=0)
        corr = np.corrcoef(rets.T)
        labels = panel.symbols
        n = len(labels)
        fig, ax = plt.subplots(figsize=(5, 4.5))
        im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_title("Correlation matrix (daily log returns, yfinance)")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        b64 = fig_to_base64_png(fig)
        return ChartOutput(
            chart_type="correlation_matrix",
            title="Holding correlations (yfinance returns)",
            image_base64=b64,
            summary=f"{n}×n correlation from yfinance daily returns.",
        )

    n = max(len(holdings), 2)
    rng = np.random.default_rng(99 if mock else 3)
    raw = rng.standard_normal((n, 60))
    corr = np.corrcoef(raw)
    labels = [holdings[i] if i < len(holdings) else f"H{i}" for i in range(n)]
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    suffix = " (mock)" if mock else ""
    ax.set_title(f"Correlation matrix ({n}×{n}){suffix}")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    b64 = fig_to_base64_png(fig)
    return ChartOutput(
        chart_type="correlation_matrix",
        title="Holding correlations (synthetic series)",
        image_base64=b64,
        summary=f"{n}×n correlation heatmap from synthetic returns (stub).",
    )


def _stub_sectors(holdings: list[str]) -> tuple[list[str], list[float]]:
    base = ["Technology", "Healthcare", "Financials", "Consumer", "Energy", "Industrials"]
    rng = np.random.default_rng(hash(tuple(holdings)) % (2**32))
    k = min(len(base), 5)
    sectors = base[:k]
    returns = (rng.random(k) - 0.45) * 0.24
    return sectors, [float(x) for x in returns]


def _render_sector_performance(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None,
) -> ChartOutput:
    _ = lookback_days
    if panel is not None and panel.levels.shape[0] >= 2:
        p0 = panel.levels[0]
        p1 = panel.levels[-1]
        rets_pct = (p1 / p0 - 1.0) * 100.0
        labels = panel.symbols
        colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))
        fig, ax = plt.subplots(figsize=(6, 3.8))
        bars = ax.bar(labels, rets_pct, color=colors, edgecolor="#333", linewidth=0.4)
        ax.axhline(0, color="#666", linewidth=0.8)
        ax.set_ylabel("Total return (%)")
        ax.set_title("Holding period return (yfinance)")
        ax.tick_params(axis="x", rotation=25)
        ax.grid(True, axis="y", alpha=0.25)
        for b, r in zip(bars, rets_pct, strict=True):
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + 0.3 * np.sign(r or 1),
                f"{r:.1f}%",
                ha="center",
                va="bottom",
                fontsize=7,
            )
        fig.tight_layout()
        b64 = fig_to_base64_png(fig)
        best_i = int(np.argmax(rets_pct))
        return ChartOutput(
            chart_type="sector_performance",
            title="Holding returns over window (yfinance)",
            image_base64=b64,
            summary=f"Largest move: {labels[best_i]} ({rets_pct[best_i]:.1f}%).",
        )

    sectors, rets = _stub_sectors(holdings)
    colors = plt.cm.Set2(np.linspace(0, 1, len(sectors)))
    fig, ax = plt.subplots(figsize=(6, 3.8))
    bars = ax.bar(sectors, [r * 100 for r in rets], color=colors, edgecolor="#333", linewidth=0.4)
    ax.axhline(0, color="#666", linewidth=0.8)
    ax.set_ylabel("Return (%, synthetic)")
    suffix = " (mock)" if mock else ""
    ax.set_title(f"Sector performance (stub){suffix}")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(True, axis="y", alpha=0.25)
    for b, r in zip(bars, rets, strict=True):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 0.01 * np.sign(r or 1),
            f"{r*100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=7,
        )
    fig.tight_layout()
    b64 = fig_to_base64_png(fig)
    best = sectors[int(np.argmax(rets))]
    return ChartOutput(
        chart_type="sector_performance",
        title="Sector return comparison (synthetic)",
        image_base64=b64,
        summary=f"Largest synthetic sector move: {best} ({max(rets)*100:.1f}%).",
    )


def _render_volatility_cone(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None,
) -> ChartOutput:
    horizon = max(1, min(lookback_days, 180))
    days_fwd = np.arange(1, horizon + 1)

    if panel is not None and panel.levels.shape[0] >= 5:
        prices = np.clip(panel.levels, 1e-9, None)
        log_ret = np.diff(np.log(prices), axis=0).mean(axis=1)
        sigma_daily = float(np.std(log_ret) + 1e-12)
        width = sigma_daily * np.sqrt(days_fwd.astype(float)) * 100
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.fill_between(days_fwd, -width, width, alpha=0.35, color="#7c3aed", label="±1σ cone (realized vol)")
        ax.plot(days_fwd, width, color="#5b21b6", linewidth=1)
        ax.plot(days_fwd, -width, color="#5b21b6", linewidth=1)
        ax.axhline(0, color="#444", linewidth=0.8)
        ax.set_xlabel("Forward days")
        ax.set_ylabel("Band width (% of notional)")
        ax.set_title("Volatility cone (from yfinance realized vol)")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.25)
        fig.tight_layout()
        b64 = fig_to_base64_png(fig)
        return ChartOutput(
            chart_type="volatility_cone",
            title="Forward volatility cone (illustrative)",
            image_base64=b64,
            summary=f"σ≈{sigma_daily * np.sqrt(252) * 100:.1f}% annualized from EW portfolio.",
        )

    rng = np.random.default_rng(11 if mock else 22)
    sigma = 0.015 + 0.002 * len(holdings)
    width = sigma * np.sqrt(days_fwd) * 100
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.fill_between(days_fwd, -width, width, alpha=0.35, color="#7c3aed", label="±1σ cone (synthetic)")
    ax.plot(days_fwd, width, color="#5b21b6", linewidth=1)
    ax.plot(days_fwd, -width, color="#5b21b6", linewidth=1)
    ax.axhline(0, color="#444", linewidth=0.8)
    ax.set_xlabel("Forward days")
    ax.set_ylabel("Band width (% of notional)")
    suffix = " (mock)" if mock else ""
    ax.set_title(f"Volatility cone (sqrt-time scaling){suffix}")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    b64 = fig_to_base64_png(fig)
    return ChartOutput(
        chart_type="volatility_cone",
        title="Forward volatility cone (illustrative)",
        image_base64=b64,
        summary=f"Illustrative ±1σ band; base σ≈{sigma*100:.1f}%/√day (stub).",
    )


def _render_price_history(
    holdings: list[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None,
) -> ChartOutput:
    if panel is not None and panel.levels.shape[0] >= 2:
        prices = panel.levels[:, :6]
        syms = panel.symbols[:6]
        norm = prices / prices[0:1, :]
        days = np.arange(norm.shape[0])
        fig, ax = plt.subplots(figsize=(7, 4))
        cmap = plt.cm.tab10(np.linspace(0, 1, len(syms)))
        for i, t in enumerate(syms):
            ax.plot(days, norm[:, i] * 100, label=t, color=cmap[i], linewidth=1.1)
        ax.set_xlabel("Days")
        ax.set_ylabel("Index (start = 100)")
        ax.set_title("Price history (yfinance, normalized)")
        ax.legend(loc="upper left", fontsize=7, ncol=2)
        ax.grid(True, alpha=0.25)
        fig.tight_layout()
        b64 = fig_to_base64_png(fig)
        return ChartOutput(
            chart_type="price_history",
            title="Holding price paths (yfinance)",
            image_base64=b64,
            summary=f"Normalized adjusted close for {len(syms)} names over {len(days)} days.",
        )

    tickers = holdings[:6] if holdings else ["SYM1", "SYM2"]
    n_days = max(2, min(lookback_days, 200))
    days = np.arange(n_days)
    rng = np.random.default_rng(55 if mock else 66)
    fig, ax = plt.subplots(figsize=(7, 4))
    cmap = plt.cm.tab10(np.linspace(0, 1, len(tickers)))
    for i, t in enumerate(tickers):
        noise = rng.normal(0, 0.012, size=n_days)
        series = 100 * np.exp(np.cumsum(0.0002 * (i + 1) + noise))
        ax.plot(days, series, label=t, color=cmap[i], linewidth=1.1)
    ax.set_xlabel("Days")
    ax.set_ylabel("Synthetic price")
    suffix = " (mock)" if mock else ""
    ax.set_title(f"Price history overlay — {len(tickers)} names{suffix}")
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    b64 = fig_to_base64_png(fig)
    return ChartOutput(
        chart_type="price_history",
        title="Holding price paths (synthetic)",
        image_base64=b64,
        summary=f"Overlay of {len(tickers)} synthetic series over {n_days} days.",
    )


CHART_RENDERERS: dict[str, Callable[..., ChartOutput]] = {
    "regression": _render_regression,
    "correlation_matrix": _render_correlation_matrix,
    "sector_performance": _render_sector_performance,
    "volatility_cone": _render_volatility_cone,
    "price_history": _render_price_history,
}

CHART_KEYS: frozenset[str] = frozenset(CHART_RENDERERS.keys())


def run_registered_charts(
    holdings: list[str],
    analyses: Sequence[str],
    lookback_days: int,
    *,
    mock: bool,
    panel: PricePanel | None = None,
) -> list[ChartOutput]:
    charts: list[ChartOutput] = []
    for key in analyses:
        renderer = CHART_RENDERERS.get(key)
        if renderer is None:
            continue
        charts.append(renderer(holdings, lookback_days, mock=mock, panel=panel))
    return charts


def build_model_response(msg: RunModel, *, use_mock: bool) -> ModelResponse:
    panel: PricePanel | None = None
    if not use_mock and msg.holdings:
        loaded = load_adjusted_close_matrix(msg.holdings, msg.lookback_days)
        if loaded:
            panel = PricePanel(levels=loaded[0], symbols=loaded[1])

    analyses = list(msg.analyses)
    if analyses:
        allowed = [a for a in analyses if a in CHART_KEYS]
        charts = run_registered_charts(
            msg.holdings,
            allowed,
            msg.lookback_days,
            mock=use_mock,
            panel=panel,
        )
    else:
        charts = []

    sharpe, vol, slope, metrics = estimate_metrics(
        msg.holdings,
        msg.lookback_days,
        mock=use_mock,
        panel=panel,
    )

    return ModelResponse(
        holdings_analyzed=list(msg.holdings),
        sharpe_ratio=sharpe,
        volatility=vol,
        trend_slope=slope,
        charts=charts,
        metrics=metrics,
    )

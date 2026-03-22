"""
Generate a realistic portfolio performance chart as a base64 PNG.
Outputs MOCK_CHART_BASE64 to stdout, which is captured and stored in agents/mocks/modeling.py.
"""

import base64
import io
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate_portfolio_chart() -> str:
    random.seed(42)
    np.random.seed(42)

    days = 252  # 1 trading year
    x = np.arange(days)

    # Upward trend with noise
    trend = 100 * (1 + 0.0002 * x)
    noise = np.cumsum(np.random.randn(days) * 0.8)
    portfolio_values = trend + noise

    # Benchmark (S&P 500 proxy) — slightly lower return
    bench_trend = 100 * (1 + 0.00015 * x)
    bench_noise = np.cumsum(np.random.randn(days) * 0.7)
    benchmark_values = bench_trend + bench_noise

    fig, ax = plt.subplots(figsize=(8, 4), dpi=72)
    ax.plot(x, portfolio_values, color="#2563eb", linewidth=1.5, label="Portfolio")
    ax.plot(x, benchmark_values, color="#9ca3af", linewidth=1.0, linestyle="--", label="S&P 500")
    ax.fill_between(x, portfolio_values, benchmark_values,
                    where=(portfolio_values >= benchmark_values),
                    alpha=0.12, color="#2563eb")

    ax.set_title("Portfolio Performance vs S&P 500 (1 Year)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Trading Days", fontsize=9)
    ax.set_ylabel("Normalized Value (base 100)", fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, linestyle=":")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)

    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


if __name__ == "__main__":
    chart_b64 = generate_portfolio_chart()
    print(f"Generated chart: {len(chart_b64)} base64 chars")
    print(chart_b64[:80] + "...")

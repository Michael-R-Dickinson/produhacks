#!/usr/bin/env python3
"""Write sample PNGs for the modeling chart registry.

Run from repository root::

    PYTHONPATH=. python agents/chart_examples/generate.py
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.modeling_charts import CHART_KEYS, run_registered_charts


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    holdings = ["AAPL", "MSFT", "NVDA", "GOOGL", "META"]
    charts = run_registered_charts(
        holdings,
        sorted(CHART_KEYS),
        lookback_days=365,
        mock=True,
    )
    for chart in charts:
        path = out_dir / f"{chart.chart_type}.png"
        path.write_bytes(base64.standard_b64decode(chart.image_base64))
        print(f"Wrote {path} ({chart.title})")


if __name__ == "__main__":
    main()

Chart preview PNGs in this folder are produced only by running the generator
(do not commit hand-drawn or web-copied images).

From the repository root (parent of the `agents` package):

  PYTHONPATH=. python agents/chart_examples/generate.py

This uses the same `run_registered_charts` code path as the modeling agent
with mock/synthetic data (no live yfinance calls).

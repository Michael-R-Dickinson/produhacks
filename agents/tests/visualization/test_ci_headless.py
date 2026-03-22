"""CI constraints: headless matplotlib (no GUI backend required)."""

import matplotlib

import agents.modeling_charts  # noqa: F401 — module import configures Agg


def test_matplotlib_uses_agg_after_modeling_charts_import():
    assert matplotlib.get_backend() == "Agg"

"""Contract tests: registry keys stay aligned with implementations."""

from agents.modeling_charts import CHART_KEYS, CHART_RENDERERS


def test_chart_keys_matches_registry():
    assert CHART_KEYS == frozenset(CHART_RENDERERS.keys())


def test_registry_renderers_are_callable():
    for key, fn in CHART_RENDERERS.items():
        assert callable(fn)
        assert key == key.lower()

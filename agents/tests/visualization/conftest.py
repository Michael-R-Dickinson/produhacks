"""Fixtures for visualization tests."""

import pytest


@pytest.fixture
def sample_holdings() -> list[str]:
    return ["AAPL", "MSFT", "NVDA"]

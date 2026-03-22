from agents.models.responses import AlternativesResponse


def mock_alternatives_response() -> AlternativesResponse:
    return AlternativesResponse(
        crypto_prices={"BTC": 67450.0, "ETH": 3520.0, "SOL": 142.0, "FET": 2.35},
        cross_correlations={"BTC": 0.12, "ETH": 0.18, "GOLD": -0.05, "OIL": 0.08},
    )

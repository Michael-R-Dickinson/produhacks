from typing import List, Dict
from uagents import Model

class NewsQuery(Model):
    """Input message to request news and sentiment analysis for a list of tickers."""
    tickers: List[str]
    k: int = 5  # Number of top headlines to fetch and score

class SentimentResponse(Model):
    """Output message containing the aggregated sentiment scores and fetched headlines."""
    sentiment_scores: Dict[str, float]
    # Each ticker maps to a list of dicts containing the 'headline' text and its 'url'
    headlines: Dict[str, List[Dict[str, str]]]

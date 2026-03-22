import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

from uagents import Agent, Context, Model
import finnhub
from transformers import pipeline

# --- Pydantic Models for Communication ---
from messages import NewsQuery, SentimentResponse

# --- Agent Initialization ---
news_agent = Agent(
    name="news_and_sentiment_agent",
    seed="news_and_sentiment_agent_secret_seed",
    port=8014,
    endpoint=["http://127.0.0.1:8014/submit"],
)

# --- External API & Model Setup ---
# Set up Finnhub Client (NEWS-01)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# Set up the finbert Sentiment Analysis Pipeline (NEWS-03)
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# --- Helper Functions ---
def fetch_recent_news(ticker: str, days_back: int = 7) -> List[Dict[str, Any]]:
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        news = finnhub_client.company_news(
            ticker.upper(),
            _from=start_date.strftime("%Y-%m-%d"),
            to=end_date.strftime("%Y-%m-%d")
        )
        return news
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []

def aggregate_sentiment(headlines: List[str]) -> float:
    if not headlines:
        return 0.0
    try:
        results = sentiment_pipeline(headlines, truncation=True)
        total_score = 0.0
        for result in results:
            label = result['label'].lower()
            score = result['score']
            if label == 'positive':
                total_score += score
            elif label == 'negative':
                total_score -= score
        return total_score / len(headlines)
    except Exception as e:
        print(f"Error analyzing sentiment for headlines: {e}")
        return 0.0

# --- Agent Message Handlers ---
@news_agent.on_message(model=NewsQuery, replies=SentimentResponse)
async def handle_news_query(ctx: Context, sender: str, msg: NewsQuery):
    ctx.logger.info(f"Received NewsQuery from {sender} for tickers: {msg.tickers} (k={msg.k})")
    
    sentiment_scores: Dict[str, float] = {}
    headlines_dict: Dict[str, List[Dict[str, str]]] = {}
    
    for ticker in msg.tickers:
        ticker = ticker.upper()
        ctx.logger.info(f"Processing ticker: {ticker}")
        
        raw_news = fetch_recent_news(ticker)
        
        top_news = raw_news[:msg.k]
        ticker_headlines_text = [item.get('headline', '') for item in top_news if item.get('headline')]
        
        ticker_payload = []
        for item in top_news:
            if item.get('headline'):
                ticker_payload.append({
                    "headline": item.get('headline', ''),
                    "url": item.get('url', '')
                })
        
        if not ticker_payload:
            ctx.logger.warning(f"No headlines found for {ticker}")
            sentiment_scores[ticker] = 0.0
            headlines_dict[ticker] = []
            continue
            
        ctx.logger.info(f"Analyzing sentiment for {len(ticker_headlines_text)} headlines...")
        agg_score = aggregate_sentiment(ticker_headlines_text)
        
        sentiment_scores[ticker] = round(agg_score, 4)
        headlines_dict[ticker] = ticker_payload
        
        ctx.logger.info(f"Ticker {ticker} aggregation complete. Score: {agg_score:.4f}")

    response = SentimentResponse(
        sentiment_scores=sentiment_scores,
        headlines=headlines_dict
    )
    
    ctx.logger.info(f"Sending SentimentResponse to {sender}")
    await ctx.send(sender, response)

if __name__ == "__main__":
    news_agent.run()

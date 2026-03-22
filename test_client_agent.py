from uagents import Agent, Context
from messages import NewsQuery, SentimentResponse

client_agent = Agent(
    name="investor_client",
    seed="investor_client_seed_123",
    port=8015,
    endpoint=["http://127.0.0.1:8015/submit"],
)

NEWS_AGENT_ADDRESS = "agent1qt7uj3xgm0xgjt7jfyhs463fpwcp4g7aqvppxel6alwmr7wq83l7zpqjfw2"

@client_agent.on_event("startup")
async def request_news(ctx: Context):
    ctx.logger.info(f"Client Address: {client_agent.address}")
    
    query = NewsQuery(tickers=["AAPL", "TSLA"], k=3)
    ctx.logger.info(f"Asking News Agent for sentiment data on: {query.tickers}")
    
    await ctx.send(NEWS_AGENT_ADDRESS, query)

@client_agent.on_message(model=SentimentResponse)
async def handle_response(ctx: Context, sender: str, msg: SentimentResponse):
    ctx.logger.info(f"--- Received Sentiment Report from News Agent ---")
    for ticker in msg.sentiment_scores:
        score = msg.sentiment_scores[ticker]
        headline_count = len(msg.headlines[ticker])
        ctx.logger.info(f"Ticker: {ticker} | Score: {score:.2f} | Headlines processed: {headline_count}")
        
        if headline_count > 0:
            for i, data in enumerate(msg.headlines[ticker], 1):
                ctx.logger.info(f"   {i}. {data['headline']}\n      [Link]: {data['url']}")

if __name__ == "__main__":
    client_agent.run()

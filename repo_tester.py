from uagents import Agent, Context
from agents.models.requests import FetchNews
from agents.models.responses import NewsResponse

tester_agent = Agent(
    name="test_orchestrator",
    seed="test-orchestrator-seed",
    port=8031,
    endpoint=["http://127.0.0.1:8031/submit"]
)

# Put the address printed in the news_agent terminal here!
NEWS_AGENT_ADDRESS = "agent1q20xc3h8a6k0m53pmw3gteaql8t83yah2jw8xntjufqcjw2y6lvl7fpvc36"

@tester_agent.on_event("startup")
async def ping_news(ctx: Context):
    if "agent1q..." in NEWS_AGENT_ADDRESS:
        ctx.logger.error("⚠️ Please update the NEWS_AGENT_ADDRESS variable before running!")
        return
        
    ctx.logger.info("📡 Firing orchestrator `FetchNews` request (requesting top 3)...")
    payload = FetchNews(tickers=["AAPL", "TSLA"], mock=False, k=3)
    await ctx.send(NEWS_AGENT_ADDRESS, payload)

@tester_agent.on_message(model=NewsResponse)
async def verify_response(ctx: Context, sender: str, msg: NewsResponse):
    ctx.logger.info("✅ Received `NewsResponse` from Agent!")
    ctx.logger.info(f"Aggregate Polarity: {msg.overall_sentiment:.2f}")
    
    for h in msg.headlines:
        ctx.logger.info(f"[{h['ticker']}] Sentiment: {h['sentiment']:.2f} | {h['title']}")
        ctx.logger.info(f"   🔗 Link: {h['url']}")

if __name__ == "__main__":
    tester_agent.run()

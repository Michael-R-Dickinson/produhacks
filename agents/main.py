from dotenv import load_dotenv

load_dotenv()

import asyncio
import uvicorn
from agents.bridge.app import app, event_queue
from agents.bureau import launch_bureau
from agents.orchestrator import orchestrator
from agents.portfolio_agent import portfolio_agent
from agents.news_agent import news_agent
from agents.modeling_agent import modeling_agent
from agents.alternatives_agent import alternatives_agent


_all_agents = [orchestrator, portfolio_agent, news_agent, modeling_agent, alternatives_agent]


@app.on_event("startup")
async def start_bureau_thread() -> None:
    """Launch Bureau after uvicorn's event loop is running."""
    fastapi_loop = asyncio.get_running_loop()
    launch_bureau(_all_agents, fastapi_loop, event_queue)


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

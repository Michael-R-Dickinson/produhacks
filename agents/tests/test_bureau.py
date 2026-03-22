import os

from agents.orchestrator import orchestrator
from agents.portfolio_agent import portfolio_agent
from agents.news_agent import news_agent
from agents.modeling_agent import modeling_agent
from agents.alternatives_agent import alternatives_agent

_ALL_AGENTS = [orchestrator, portfolio_agent, news_agent, modeling_agent, alternatives_agent]


def test_all_agents_registered():
    for agent in _ALL_AGENTS:
        address = str(agent.address)
        assert address.startswith("agent1q"), (
            f"{agent.name} address does not start with 'agent1q': {address}"
        )

    addresses = [str(a.address) for a in _ALL_AGENTS]
    assert len(addresses) == len(set(addresses)), "Duplicate agent addresses detected (seed collision)"


def test_agent_addresses_stable_across_imports():
    from agents.orchestrator import orchestrator as orch2
    from agents.portfolio_agent import portfolio_agent as port2
    from agents.news_agent import news_agent as news2
    from agents.modeling_agent import modeling_agent as mod2
    from agents.alternatives_agent import alternatives_agent as alt2

    second_import = [orch2, port2, news2, mod2, alt2]

    for original, reimported in zip(_ALL_AGENTS, second_import):
        assert str(original.address) == str(reimported.address), (
            f"{original.name}: address changed between imports"
        )


def test_mock_mode_default_true():
    assert os.getenv("MOCK_DATA", "true").lower() == "true"

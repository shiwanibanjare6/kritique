from app.agents.static_agent import StaticAgent


def test_static_agent():
    agent = StaticAgent()
    result = agent.analyze("sample")
    assert result["message"] == "Static analysis placeholder"

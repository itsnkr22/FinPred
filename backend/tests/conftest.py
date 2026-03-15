import pytest


@pytest.fixture
def sample_scenario_data():
    return {
        "name": "Test Scenario",
        "description": "A test scenario",
        "seed_event": "BREAKING: Federal Reserve announces emergency rate cut",
        "environment_vars": {
            "market_volatility": "high",
            "sector_focus": "general",
            "election_year": False,
            "fed_stance": "dovish",
        },
        "duration_minutes": 30,
        "agent_count": 20,
    }

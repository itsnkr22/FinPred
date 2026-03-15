from app.engine.personas import PERSONA_CONFIGS, get_persona_config


def test_all_personas_defined():
    expected = {"retail_reddit", "hft_algo", "institutional", "macro_hedge", "finfluencer"}
    assert set(PERSONA_CONFIGS.keys()) == expected


def test_percentages_sum_to_one():
    total = sum(p.percentage for p in PERSONA_CONFIGS.values())
    assert abs(total - 1.0) < 0.01


def test_get_persona_config():
    config = get_persona_config("retail_reddit")
    assert config.persona_type == "retail_reddit"
    assert config.percentage == 0.35


def test_get_invalid_persona():
    try:
        get_persona_config("invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

from app.engine.metrics import calculate_p_impact, calculate_stance_ratios


def test_p_impact_calculation():
    agents = [
        {"sentiment": 0.5, "capital_weight": 0.1},
        {"sentiment": -0.3, "capital_weight": 0.2},
        {"sentiment": 0.8, "capital_weight": 0.05},
    ]
    result = calculate_p_impact(agents)
    expected = 0.5 * 0.1 + (-0.3) * 0.2 + 0.8 * 0.05
    assert abs(result - expected) < 0.001


def test_stance_ratios():
    stances = ["BUY", "BUY", "SELL", "HOLD", "BUY"]
    ratios = calculate_stance_ratios(stances)
    assert ratios["buy_ratio"] == 0.6
    assert ratios["sell_ratio"] == 0.2
    assert ratios["hold_ratio"] == 0.2


def test_empty_stances():
    ratios = calculate_stance_ratios([])
    assert ratios["buy_ratio"] == 0.0

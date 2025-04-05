from core.scoring import calculate_eie, calculate_roi

def test_calculate_eie():
    idea = {
        "time_required": 6,
        "resource_cost": 5,
        "dependency_complexity": 4
    }
    score, _ = calculate_eie(idea)
    assert score == round((6*0.4 + 5*0.4 + 4*0.2), 2)

def test_calculate_roi():
    idea = {
        "value_created": 9,
        "user_demand": 6,
        "business_impact": 7
    }
    score, _ = calculate_roi(idea)
    assert score == round((9*0.4 + 6*0.3 + 7*0.3), 2)

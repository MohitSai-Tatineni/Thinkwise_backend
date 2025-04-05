def calculate_eie(idea: dict) -> tuple:
    time = idea.get("time_required", 5)
    cost = idea.get("resource_cost", 5)
    dependencies = idea.get("dependency_complexity", 5)

    score = round((time * 0.4) + (cost * 0.4) + (dependencies * 0.2), 2)
    
    reasoning = [
        f"EIE Calculation: Time({time}) * 0.4 + Cost({cost}) * 0.4 + Dependencies({dependencies}) * 0.2",
        f"EIE Score = {score}"
    ]
    return score, reasoning

def calculate_roi(idea: dict) -> tuple:
    value = idea.get("value_created", 5)
    demand = idea.get("user_demand", 5)
    impact = idea.get("business_impact", 5)

    score = round((value * 0.4) + (demand * 0.3) + (impact * 0.3), 2)
    
    reasoning = [
        f"ROI Calculation: Value({value}) * 0.4 + Demand({demand}) * 0.3 + Impact({impact}) * 0.3",
        f"ROI Score = {score}"
    ]
    return score, reasoning

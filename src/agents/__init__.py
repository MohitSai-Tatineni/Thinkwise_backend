from core.scoring import calculate_eie, calculate_roi

def analyze_idea(idea: dict) -> dict:
    reasoning = []

    reasoning.append(f"Analyzing idea: {idea.get('title')}")
    
    roi, roi_reasoning = calculate_roi(idea)
    eie, eie_reasoning = calculate_eie(idea)
    
    reasoning.extend(roi_reasoning)
    reasoning.extend(eie_reasoning)

    # Final composite score (can be customized)
    final_score = roi - (eie * 0.5)
    reasoning.append(f"Final score = ROI ({roi}) - EIE x 0.5 ({eie * 0.5}) = {final_score:.2f}")

    return {
        "idea": idea,
        "roi": roi,
        "eie": eie,
        "score": round(final_score, 2),
        "reasoning": reasoning
    }

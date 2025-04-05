from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from agents import analyze_idea

app = FastAPI()

class Idea(BaseModel):
    title: str
    time_required: float
    resource_cost: float
    dependency_complexity: float
    value_created: float
    user_demand: float
    business_impact: float

@app.post("/evaluate")
def evaluate_ideas(ideas: List[Idea]):
    results = [analyze_idea(idea.dict()) for idea in ideas]
    top_3 = sorted(results, key=lambda x: x["score"], reverse=True)[:3]
    return {"top_ideas": top_3}

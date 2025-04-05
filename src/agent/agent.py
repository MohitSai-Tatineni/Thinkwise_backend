from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, BaseMessage
from langchain.agents import Tool
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import Dict, List, TypedDict, Sequence, Annotated
from langchain_core.runnables import RunnableConfig
import json
from langchain_google_vertexai import ChatVertexAI
import os
from dotenv import load_dotenv

# ----------------------------
# Environment Variables
# ----------------------------
# Load variables from .env file
load_dotenv()

# Now you can access the environment variables
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ----------------------------
# LLM Setup
# ----------------------------
llm = ChatVertexAI(model="gemini-2.0-flash-001", temperature=0.7)

# ----------------------------
# State Definition
# ----------------------------
class Assistant(BaseModel):
    ideas: Dict[str, Dict]
    EIE_score: Dict[str, float]
    ROI_score: Dict[str, float]
    Top_3: List[str]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

# ----------------------------
# Tool Input Schemas (For Gemini compatibility)
# ----------------------------
class IdeaInput(BaseModel):
    idea_id: str = Field(..., description="Unique identifier of the idea")
    description: str = Field(..., description="Detailed description of the idea")

# ----------------------------
# Tool Functions
# ----------------------------
@tool(args_schema=IdeaInput)
def eie_calc_tool(idea_id: str, description: str) -> Dict[str, float]:
    """Estimate implementation effort for a given idea."""
    prompt = f"""
    You are an efficient agent that assesses the Estimated Implementation Effort for a given idea.

    Analyze:
    - Time needed
    - Cost
    - Resources
    - Dependencies

    Return the response in JSON format:
    {{
        "eie_score": float,
        "time_needed": "string",
        "cost": "string",
        "resources": ["list of resources"],
        "dependencies": ["list of dependencies"]
    }}

    Here's the idea: {description}
    """
    res = llm.invoke(prompt)
    try:
        parsed = json.loads(res.content)
        return {idea_id: parsed["eie_score"]}
    except Exception as e:
        print(f"Failed to parse EIE for {idea_id}: {e}\n Content: {res.content}")
        return {idea_id: 1.0}

@tool(args_schema=IdeaInput)
def roi_calc_tool(idea_id: str, description: str) -> Dict[str, float]:
    """Estimate ROI for a given idea."""
    prompt = f"""
    You are an ROI assessment agent. Analyze the potential value and impact of the following idea.

    Return in JSON format:
    {{
        "roi_score": float,
        "tools_used": ["list"],
        "content_fetched": ["list"]
    }}

    Idea description: {description}
    """
    result = llm.invoke(prompt)
    try:
        parsed = json.loads(result.content)
        return {idea_id: parsed["roi_score"]}
    except Exception as e:
        print(f"Failed to parse ROI for {idea_id}: {e}\nContent: {result.content}")
        return {idea_id: 1.0}

# Bind tools and models
tools = [eie_calc_tool, roi_calc_tool]
model = llm.bind_tools(tools)
tools_by_name = {tool.name: tool for tool in tools}

# ----------------------------
# Tool Node
# ----------------------------
def tool_node(state: AgentState):
    print("\n[🔧 Tool Node Activated]")
    outputs = []
    last_message = state["messages"][-1]

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        print(f"🛠️ Calling tool: {tool_name} with args: {tool_args}")

        result = tools_by_name[tool_name].invoke(tool_args)
        print(f"✅ Result: {result}")

        outputs.append(
            ToolMessage(
                content=json.dumps(result),
                name=tool_name,
                tool_call_id=tool_call["id"]
            )
        )
    return {"messages": outputs}

# ----------------------------
# Model Node
# ----------------------------
def call_model(state: AgentState, config: RunnableConfig):
    print("\n[🧠 Model Node Activated]")
    system_prompt = SystemMessage(
        content="""
        You are a reasoning agent using these tools:
        - eie_calc_tool: for estimating implementation effort
        - roi_calc_tool: for estimating return on investment

        For each idea, use both tools before concluding.
        """
    )

    messages = [system_prompt] + state["messages"]
    for msg in messages:
        print(f"🔹 {msg.type if hasattr(msg, 'type') else 'System'}: {msg.content if hasattr(msg, 'content') else msg}")

    response = model.invoke(messages, config)
    print(f"\n📤 Model response: {response.content}")
    return {"messages": [response]}

# ----------------------------
# Conditional Edge
# ----------------------------
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

# ----------------------------
# Graph Build
# ----------------------------
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
graph.add_edge("tools", "agent")
workflow = graph.compile()

# # ----------------------------
# # Test Execution
# # ----------------------------
# if __name__ == "__main__":
#     idea_dict = {
#         "idea1": {"description": "Build a Chrome extension that summarizes YouTube videos in real-time."},
#         "idea2": {"description": "Create a SaaS tool that helps freelancers generate invoices automatically."},
#     }

#     initial_msg = HumanMessage(content=f"Analyze these ideas: {json.dumps(idea_dict)}")
#     final_state = workflow.invoke({"messages": [initial_msg]})

#     print("\n🎉 Final Output:")
#     for msg in final_state["messages"]:
#         print(f"📨 {msg.type if hasattr(msg, 'type') else 'Unknown'}: {msg.content}")

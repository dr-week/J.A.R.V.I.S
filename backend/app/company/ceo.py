import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

# Setup paths
ROOT_DIR = Path(__file__).resolve().parents[3]
AI_COMPANY_DIR = ROOT_DIR / "AI-COMPANY"
TASKS_PENDING_DIR = AI_COMPANY_DIR / "tasks" / "pending"

COMPANY_MD = AI_COMPANY_DIR / "COMPANY.md"
BUSINESS_STATE_MD = AI_COMPANY_DIR / "BUSINESS_STATE.md"


class TaskPacket(TypedDict):
    id: str
    target_module: Literal["MoneyMantra", "DANGERROBO", "DangerMarketDepo"]
    action: str
    priority: str
    details: dict[str, Any]


class CEOState(TypedDict):
    market_signal: str
    company_context: str
    business_state: str
    analysis: str
    decision: str
    tasks_to_dispatch: list[TaskPacket]


def load_context(state: CEOState) -> CEOState:
    """Reads the current corporate state and rules."""
    print("[CEO] Reading Corporate State...")
    company_ctx = COMPANY_MD.read_text(encoding="utf-8") if COMPANY_MD.exists() else "No company data."
    biz_state = BUSINESS_STATE_MD.read_text(encoding="utf-8") if BUSINESS_STATE_MD.exists() else "No business state."
    
    return {
        "company_context": company_ctx,
        "business_state": biz_state
    }


def analyze_opportunity(state: CEOState) -> CEOState:
    """Uses LLM to analyze the signal against the business state."""
    print(f"[CEO] Analyzing Signal: {state['market_signal']}")
    llm = ChatOpenAI(temperature=0)
    
    prompt = f"""
    You are the AI CEO of a Venture Studio.
    
    COMPANY CONTEXT:
    {state['company_context']}
    
    CURRENT BUSINESS STATE:
    {state['business_state']}
    
    MARKET SIGNAL:
    {state['market_signal']}
    
    Analyze the market signal. Does this align with our company goals? 
    Is there an immediate ROI? Provide a concise strategic analysis.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    analysis_text = str(response.content)
    
    print(f"[CEO] Analysis Complete: {analysis_text[:100]}...")
    return {"analysis": analysis_text}


def make_decision(state: CEOState) -> CEOState:
    """Uses LLM to decide on actions and generate task packets."""
    print("[CEO] Making Executive Decision...")
    llm = ChatOpenAI(temperature=0).bind(
        response_format={"type": "json_object"}
    )
    
    prompt = f"""
    You are the AI CEO. Based on your analysis, you must decide what to do next.
    
    ANALYSIS: {state['analysis']}
    
    You can delegate to three modules:
    - MoneyMantra: for budget allocation, ROI modeling, finance.
    - DANGERROBO: for building physical/digital prototypes, engineering.
    - DangerMarketDepo: for marketing, SEO, customer acquisition.
    
    Return a JSON object with this exact structure:
    {{
        "decision_summary": "Short explanation of the decision",
        "tasks": [
            {{
                "target_module": "MoneyMantra", # Or DANGERROBO, DangerMarketDepo
                "action": "Brief instruction",
                "priority": "P0" # P0, P1, P2
                "details": {{"key": "value"}} # Any extra structured data needed
            }}
        ]
    }}
    
    If the signal is bad, return an empty tasks list.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    decision_data = json.loads(str(response.content))
    
    tasks = decision_data.get("tasks", [])
    valid_tasks: list[TaskPacket] = []
    
    for t in tasks:
        valid_tasks.append({
            "id": f"TASK-{str(uuid.uuid4())[:8].upper()}",
            "target_module": t.get("target_module", "DANGERROBO"),
            "action": t.get("action", ""),
            "priority": t.get("priority", "P2"),
            "details": t.get("details", {})
        })
        
    return {
        "decision": decision_data.get("decision_summary", ""),
        "tasks_to_dispatch": valid_tasks
    }


def execute_tasks(state: CEOState) -> CEOState:
    """Writes the delegated tasks to the file system as JSON packets."""
    tasks = state.get("tasks_to_dispatch", [])
    if not tasks:
        print("[CEO] No tasks to dispatch. Opportunity discarded.")
        return {}
        
    TASKS_PENDING_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"[CEO] Dispatching {len(tasks)} tasks...")
    for task in tasks:
        task_id = task["id"]
        filepath = TASKS_PENDING_DIR / f"{task_id}.json"
        
        full_packet = {
            "metadata": {
                "created_at": datetime.now(UTC).isoformat(),
                "source": "Jarvis-CEO-Agent",
                "status": "pending"
            },
            "task": task
        }
        
        filepath.write_text(json.dumps(full_packet, indent=2), encoding="utf-8")
        print(f"  -> Dispatched {task_id} to {task['target_module']}")
        
    return {}


# Build the Graph
workflow = StateGraph(CEOState)

workflow.add_node("research", load_context)
workflow.add_node("analyze", analyze_opportunity)
workflow.add_node("decide", make_decision)
workflow.add_node("execute", execute_tasks)

workflow.add_edge(START, "research")
workflow.add_edge("research", "analyze")
workflow.add_edge("analyze", "decide")
workflow.add_edge("decide", "execute")
workflow.add_edge("execute", END)

ceo_app = workflow.compile()

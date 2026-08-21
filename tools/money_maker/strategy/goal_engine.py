"""Real-Time Assumption Tracker & Dynamic Goal Setting Engine for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Strategy / Goal Optimization
- Standard Risk Level: 'auto' (Read-only hypothesis management)
"""
from typing import Dict, Any, List
from datetime import datetime
from backend.app.hands.registry import register

# In-memory session store for active financial hypotheses
ACTIVE_ASSUMPTIONS: Dict[str, Dict[str, Any]] = {}
ACTIVE_GOALS: List[Dict[str, Any]] = []

def mm_set_financial_goal(
    goal_name: str,
    target_amount_inr: float,
    strategy_archetype: str,
    deadline_days: int = 30
) -> Dict[str, Any]:
    """Registers a financial target with specific strategy archetype and micro-milestones."""
    goal = {
        "goal_name": goal_name,
        "target_amount_inr": target_amount_inr,
        "strategy_archetype": strategy_archetype,
        "deadline_days": deadline_days,
        "created_at": datetime.now().isoformat(),
        "daily_target_inr": round(target_amount_inr / deadline_days, 2) if deadline_days > 0 else target_amount_inr,
        "status": "ACTIVE"
    }
    ACTIVE_GOALS.append(goal)
    
    return {
        "status": "success",
        "message": f"Goal '{goal_name}' registered successfully.",
        "goal_details": goal
    }

def mm_track_assumption(
    hypothesis_key: str,
    assumption_statement: str,
    confidence_score: float,
    invalidation_condition: str
) -> Dict[str, Any]:
    """Records a real-time market or business assumption to be dynamically monitored."""
    record = {
        "statement": assumption_statement,
        "confidence": confidence_score,
        "invalidation_condition": invalidation_condition,
        "updated_at": datetime.now().isoformat(),
        "is_valid": confidence_score >= 0.4
    }
    ACTIVE_ASSUMPTIONS[hypothesis_key] = record
    
    return {
        "status": "success",
        "hypothesis_key": hypothesis_key,
        "is_valid": record["is_valid"],
        "record": record
    }

register(
    {
        "name": "mm_set_financial_goal",
        "description": "Registers financial income targets, daily run-rates, and strategy archetypes.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_name": {"type": "string"},
                "target_amount_inr": {"type": "number"},
                "strategy_archetype": {"type": "string", "description": "e.g. 'Freelance Automation', 'Swing Arbitrage'"},
                "deadline_days": {"type": "integer", "default": 30}
            },
            "required": ["goal_name", "target_amount_inr", "strategy_archetype"]
        },
        "returns": {"type": "object"},
        "scopes": [],
        "tags": ["strategy", "goals", "money_maker"],
    },
    mm_set_financial_goal,
)

register(
    {
        "name": "mm_track_assumption",
        "description": "Records real-time market hypotheses with invalidation triggers to dynamically pivot strategies.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "hypothesis_key": {"type": "string"},
                "assumption_statement": {"type": "string"},
                "confidence_score": {"type": "number"},
                "invalidation_condition": {"type": "string"}
            },
            "required": ["hypothesis_key", "assumption_statement", "confidence_score", "invalidation_condition"]
        },
        "returns": {"type": "object"},
        "scopes": [],
        "tags": ["strategy", "hypothesis", "money_maker"],
    },
    mm_track_assumption,
)

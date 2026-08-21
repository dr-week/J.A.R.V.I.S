"""Cash Flow & Expense Tracking Engine for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Finance / Cash Flow
- Standard Risk Level: 'auto' (Read-only personal accounting)
"""
from typing import Dict, Any, List
from backend.app.hands.registry import register

def mm_track_expenses(
    transactions: List[Dict[str, Any]],
    monthly_budget_inr: float = 50000.0
) -> Dict[str, Any]:
    """Analyzes a list of transaction records, categorizes expenses, and checks budget limits."""
    category_totals: Dict[str, float] = {}
    total_spent = 0.0
    total_income = 0.0
    
    for tx in transactions:
        amount = float(tx.get("amount", 0.0))
        category = tx.get("category", "Uncategorized").title()
        
        if amount < 0:
            expense = abs(amount)
            total_spent += expense
            category_totals[category] = category_totals.get(category, 0.0) + expense
        else:
            total_income += amount
            
    budget_usage_pct = (total_spent / monthly_budget_inr * 100.0) if monthly_budget_inr > 0 else 0.0
    is_overbudget = total_spent > monthly_budget_inr
    
    return {
        "status": "success",
        "total_income": round(total_income, 2),
        "total_spent": round(total_spent, 2),
        "net_savings": round(total_income - total_spent, 2),
        "monthly_budget": monthly_budget_inr,
        "budget_usage_pct": round(budget_usage_pct, 1),
        "is_overbudget": is_overbudget,
        "category_breakdown": {k: round(v, 2) for k, v in category_totals.items()}
    }

register(
    {
        "name": "mm_track_expenses",
        "description": "Calculates category spending, net savings, and budget limit utilization.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "transactions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of {description, amount, category} objects (negative amount = expense)"
                },
                "monthly_budget_inr": {"type": "number", "default": 50000.0}
            },
            "required": ["transactions"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "total_spent": {"type": "number"},
                "budget_usage_pct": {"type": "number"},
                "is_overbudget": {"type": "boolean"}
            }
        },
        "scopes": [],
        "tags": ["finance", "budget", "money_maker"],
    },
    mm_track_expenses,
)

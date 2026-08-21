"""Probability & Expected Value (EV) Engine for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Probability / Quantitative Finance
- Standard Risk Level: 'auto' (Read-only mathematical calculation)
"""
import math
from typing import Dict, Any, List
from backend.app.hands.registry import register

def mm_calculate_expected_value(
    win_probability: float,
    potential_gain: float,
    loss_probability: float,
    potential_loss: float
) -> Dict[str, Any]:
    """Calculates the mathematical Expected Value (EV) of a financial trade or gig.
    
    Formula: EV = (P_win * Gain) - (P_loss * Loss)
    Rule: Only proceed if EV > 0 and Risk/Reward >= 1.5
    """
    if win_probability + loss_probability > 1.05:
        # Normalize if passed as percentages
        win_probability /= 100.0
        loss_probability /= 100.0
        
    ev = (win_probability * potential_gain) - (loss_probability * potential_loss)
    risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else float('inf')
    
    is_favorable = ev > 0 and risk_reward_ratio >= 1.5
    recommendation = "FAVORABLE: Mathematical edge detected." if is_favorable else "UNFAVORABLE: Negative or sub-optimal EV."
    
    return {
        "status": "success",
        "expected_value": round(ev, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 2) if risk_reward_ratio != float('inf') else "Infinite",
        "is_favorable": is_favorable,
        "recommendation": recommendation
    }

register(
    {
        "name": "mm_calculate_expected_value",
        "description": "Calculates Expected Value (EV) and Risk/Reward ratio for trades or business investments.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "win_probability": {"type": "number", "description": "Probability of win (0.0 to 1.0 or 0-100%)"},
                "potential_gain": {"type": "number", "description": "Potential payout in ₹ or $"},
                "loss_probability": {"type": "number", "description": "Probability of loss (0.0 to 1.0 or 0-100%)"},
                "potential_loss": {"type": "number", "description": "Potential capital at risk in ₹ or $"}
            },
            "required": ["win_probability", "potential_gain", "loss_probability", "potential_loss"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "expected_value": {"type": "number"},
                "is_favorable": {"type": "boolean"},
                "recommendation": {"type": "string"}
            }
        },
        "scopes": [],
        "tags": ["probability", "math", "money_maker"],
    },
    mm_calculate_expected_value,
)

"""Monte Carlo Simulation Engine for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Probability / Risk Simulation
- Standard Risk Level: 'auto' (Read-only mathematical simulation)
"""
import random
import math
from typing import Dict, Any, List
from backend.app.hands.registry import register

def mm_monte_carlo_sim(
    initial_capital: float,
    win_probability: float,
    win_payout_multiplier: float,
    loss_fraction: float = 1.0,
    num_simulations: int = 1000,
    trades_per_sim: int = 50
) -> Dict[str, Any]:
    """Runs Monte Carlo simulations to assess probability of profit vs drawdown."""
    if win_probability > 1.0:
        win_probability /= 100.0
        
    final_balances = []
    ruin_count = 0
    
    for _ in range(num_simulations):
        balance = initial_capital
        for _ in range(trades_per_sim):
            if balance <= initial_capital * 0.2:  # 80% drawdown = ruin
                ruin_count += 1
                break
            is_win = random.random() < win_probability
            if is_win:
                balance += balance * win_payout_multiplier * 0.05  # Standard 5% position sizing
            else:
                balance -= balance * loss_fraction * 0.05
        final_balances.append(balance)
        
    avg_final = sum(final_balances) / len(final_balances)
    profitable_sims = sum(1 for b in final_balances if b > initial_capital)
    profit_probability = (profitable_sims / num_simulations) * 100.0
    risk_of_ruin_pct = (ruin_count / num_simulations) * 100.0
    
    return {
        "status": "success",
        "initial_capital": initial_capital,
        "expected_final_capital": round(avg_final, 2),
        "profit_probability_pct": round(profit_probability, 1),
        "risk_of_ruin_pct": round(risk_of_ruin_pct, 2),
        "recommendation": "APPROVED" if profit_probability > 65 and risk_of_ruin_pct < 5 else "HIGH RISK"
    }

register(
    {
        "name": "mm_monte_carlo_sim",
        "description": "Runs 1,000+ Monte Carlo scenario simulations to project portfolio growth vs drawdown risk.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "initial_capital": {"type": "number"},
                "win_probability": {"type": "number"},
                "win_payout_multiplier": {"type": "number", "description": "e.g. 2.0 for 2:1 risk/reward"},
                "loss_fraction": {"type": "number", "default": 1.0},
                "num_simulations": {"type": "integer", "default": 1000}
            },
            "required": ["initial_capital", "win_probability", "win_payout_multiplier"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "expected_final_capital": {"type": "number"},
                "profit_probability_pct": {"type": "number"},
                "risk_of_ruin_pct": {"type": "number"}
            }
        },
        "scopes": [],
        "tags": ["probability", "simulation", "money_maker"],
    },
    mm_monte_carlo_sim,
)

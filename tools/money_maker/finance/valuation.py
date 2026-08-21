"""Asset Valuation & Fundamental Health Analyzer for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Finance / Valuation
- Standard Risk Level: 'auto' (Read-only financial analysis)
"""
from typing import Dict, Any
from backend.app.hands.registry import register

def mm_valuate_asset(
    ticker: str,
    current_price: float,
    earnings_per_share: float,
    book_value_per_share: float = 0.0,
    sector_average_pe: float = 20.0
) -> Dict[str, Any]:
    """Calculates fundamental valuation ratios (P/E, P/B) and scores asset health."""
    if earnings_per_share <= 0:
        pe_ratio = float('inf')
        valuation_status = "UNPROFITABLE: Negative or zero EPS"
    else:
        pe_ratio = current_price / earnings_per_share
        if pe_ratio < sector_average_pe * 0.75:
            valuation_status = "UNDERVALUED: Trading at discount to sector"
        elif pe_ratio > sector_average_pe * 1.5:
            valuation_status = "OVERVALUED: Premium pricing"
        else:
            valuation_status = "FAIRLY VALUED: In-line with sector"

    pb_ratio = (current_price / book_value_per_share) if book_value_per_share > 0 else "N/A"
    
    return {
        "status": "success",
        "ticker": ticker.upper(),
        "current_price": current_price,
        "pe_ratio": round(pe_ratio, 2) if pe_ratio != float('inf') else "Negative",
        "pb_ratio": round(pb_ratio, 2) if isinstance(pb_ratio, float) else pb_ratio,
        "sector_avg_pe": sector_average_pe,
        "valuation_status": valuation_status
    }

register(
    {
        "name": "mm_valuate_asset",
        "description": "Calculates P/E ratio, P/B, and fundamental valuation health against sector averages.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "current_price": {"type": "number"},
                "earnings_per_share": {"type": "number"},
                "book_value_per_share": {"type": "number", "default": 0.0},
                "sector_average_pe": {"type": "number", "default": 20.0}
            },
            "required": ["ticker", "current_price", "earnings_per_share"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "pe_ratio": {"type": "number"},
                "valuation_status": {"type": "string"}
            }
        },
        "scopes": [],
        "tags": ["finance", "valuation", "money_maker"],
    },
    mm_valuate_asset,
)

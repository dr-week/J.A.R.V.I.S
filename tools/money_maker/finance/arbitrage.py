"""Cross-Market Arbitrage & Spread Calculator for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Finance / Arbitrage
- Standard Risk Level: 'auto' (Read-only gap detection)
"""
from typing import Dict, Any, List
from backend.app.hands.registry import register

def mm_detect_arbitrage_spread(
    asset_name: str,
    price_exchange_a: float,
    exchange_a_name: str,
    price_exchange_b: float,
    exchange_b_name: str,
    fee_percentage: float = 0.2
) -> Dict[str, Any]:
    """Detects arbitrage price gaps between two markets after deducting round-trip exchange fees."""
    if price_exchange_a <= 0 or price_exchange_b <= 0:
        return {"status": "error", "message": "Prices must be positive numbers."}
        
    low_price = min(price_exchange_a, price_exchange_b)
    high_price = max(price_exchange_a, price_exchange_b)
    buy_from = exchange_a_name if price_exchange_a == low_price else exchange_b_name
    sell_to = exchange_b_name if price_exchange_a == low_price else exchange_a_name
    
    raw_spread = high_price - low_price
    spread_pct = (raw_spread / low_price) * 100.0
    
    # Calculate net profit after dual-exchange transaction fees
    total_fees = (low_price * (fee_percentage / 100.0)) + (high_price * (fee_percentage / 100.0))
    net_profit = raw_spread - total_fees
    net_profit_pct = (net_profit / low_price) * 100.0
    
    is_arbitrage_opportunity = net_profit > 0 and net_profit_pct >= 0.5
    
    return {
        "status": "success",
        "asset": asset_name,
        "buy_from": buy_from,
        "buy_price": low_price,
        "sell_to": sell_to,
        "sell_price": high_price,
        "gross_spread_pct": round(spread_pct, 3),
        "total_estimated_fees": round(total_fees, 2),
        "net_profit_per_unit": round(net_profit, 2),
        "net_profit_pct": round(net_profit_pct, 3),
        "is_opportunity": is_arbitrage_opportunity
    }

register(
    {
        "name": "mm_detect_arbitrage_spread",
        "description": "Calculates real net arbitrage opportunities across two exchanges/markets after fees.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "asset_name": {"type": "string", "description": "e.g. BTC, ETH, Gold, Nifty ETF"},
                "price_exchange_a": {"type": "number"},
                "exchange_a_name": {"type": "string"},
                "price_exchange_b": {"type": "number"},
                "exchange_b_name": {"type": "string"},
                "fee_percentage": {"type": "number", "default": 0.2}
            },
            "required": ["asset_name", "price_exchange_a", "exchange_a_name", "price_exchange_b", "exchange_b_name"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "net_profit_per_unit": {"type": "number"},
                "is_opportunity": {"type": "boolean"}
            }
        },
        "scopes": [],
        "tags": ["finance", "arbitrage", "money_maker"],
    },
    mm_detect_arbitrage_spread,
)

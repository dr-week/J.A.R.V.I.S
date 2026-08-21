from backend.app.hands.registry import register

try:
    import yfinance as yf
    import pandas as pd
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

def mm_scan_market(tickers: list[str]) -> dict:
    """Scans the market for a list of tickers and returns technical analysis alerts."""
    if not HAS_YFINANCE:
        return {
            "status": "partial",
            "message": "yfinance not installed in current environment. Install via: pip install yfinance",
            "tickers_received": tickers
        }
        
    alerts = []
    results = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if hist.empty:
                results[ticker] = {"error": "No data found"}
                continue
                
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            current_price = hist['Close'].iloc[-1]
            sma_50 = hist['SMA_50'].iloc[-1]
            
            results[ticker] = {
                "current_price": current_price,
                "sma_50": sma_50 if not pd.isna(sma_50) else None
            }
            
            if not pd.isna(sma_50) and current_price > sma_50:
                alerts.append(f"{ticker} is trending ABOVE its 50-day SMA.")
                
        except Exception as e:
            results[ticker] = {"error": str(e)}

    return {
        "status": "success",
        "alerts": alerts,
        "details": results
    }

# Register the tool with Jarvis's built-in registry
register(
    {
        "name": "mm_scan_market",
        "description": "Scans stock/crypto markets and calculates technical indicators (SMAs, etc.)",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",  # Read-only, safe
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols (e.g., ['AAPL', 'BTC-USD'])"
                }
            },
            "required": ["tickers"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "alerts": {"type": "array", "items": {"type": "string"}},
                "details": {"type": "object"}
            }
        },
        "scopes": [],
        "tags": ["finance", "money_maker"],
    },
    mm_scan_market,
)

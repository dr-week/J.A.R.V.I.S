"""Headline Sentiment & Contrarian Market Mood Analyzer for Jarvis Money Maker.

Standard Module Nomenclature:
- Domain: Marketing / Sentiment Analysis
- Standard Risk Level: 'auto' (Read-only sentiment scoring)
"""
from typing import Dict, Any, List
from backend.app.hands.registry import register

BULLISH_KEYWORDS = ["surge", "record high", "rally", "profit", "bullish", "growth", "breakout", "boom", "gain"]
BEARISH_KEYWORDS = ["crash", "drop", "plunge", "recession", "bearish", "loss", "ban", "fraud", "scam", "panic"]

def mm_analyze_sentiment(headlines: List[str]) -> Dict[str, Any]:
    """Analyzes a list of news headlines and produces a Fear & Greed sentiment index (0-100)."""
    if not headlines:
        return {"status": "error", "message": "Headlines list cannot be empty."}
        
    bull_count = 0
    bear_count = 0
    
    for h in headlines:
        hl = h.lower()
        if any(w in hl for w in BULLISH_KEYWORDS):
            bull_count += 1
        if any(w in hl for w in BEARISH_KEYWORDS):
            bear_count += 1
            
    total = bull_count + bear_count
    if total == 0:
        sentiment_score = 50.0  # Neutral
        sentiment_label = "NEUTRAL"
    else:
        sentiment_score = (bull_count / total) * 100.0
        if sentiment_score >= 70:
            sentiment_label = "EXTREME GREED (Caution / Take Profit)"
        elif sentiment_score <= 30:
            sentiment_label = "EXTREME FEAR (Contrarian Opportunity)"
        else:
            sentiment_label = "MODERATE / BALANCED"
            
    return {
        "status": "success",
        "headlines_analyzed": len(headlines),
        "sentiment_score": round(sentiment_score, 1),
        "sentiment_label": sentiment_label,
        "bullish_signals": bull_count,
        "bearish_signals": bear_count
    }

register(
    {
        "name": "mm_analyze_sentiment",
        "description": "Calculates market mood and Fear & Greed score from live financial headlines.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "headlines": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of news or social media headlines"
                }
            },
            "required": ["headlines"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "sentiment_score": {"type": "number"},
                "sentiment_label": {"type": "string"}
            }
        },
        "scopes": [],
        "tags": ["marketing", "sentiment", "money_maker"],
    },
    mm_analyze_sentiment,
)

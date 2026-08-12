# Money Maker Plugin for Jarvis

This is a native Jarvis plugin that integrates advanced financial, strategic, and probabilistic tools directly into the Jarvis brain.

## Architecture

This plugin follows the 6-pillar framework:
1. **Finance**: Market scanning, asset valuation, expense tracking.
2. **Intelligence**: News aggregation, opportunity scraping.
3. **Risk**: Risk evaluation before execution.
4. **Marketing**: Sentiment analysis, automated outreach.
5. **Probability**: Expected value (EV), Monte Carlo simulations.
6. **Strategy**: Real-time assumptions, dynamic goal setting.

## Integration

- All tools are registered via `backend.app.hands.registry`.
- Dangerous tools (e.g., executing trades, sending emails) are registered with `risk_level: "confirm_always"` to leverage Jarvis's built-in confirmation gate.
- Memory and logging utilize Jarvis's native systems.

## Prerequisites

```bash
pip install yfinance pandas-ta ccxt vaderSentiment scipy newsapi-python
```

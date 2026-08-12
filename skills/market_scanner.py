import yfinance as yf
import pandas as pd

def scan_market(tickers):
    """
    Scans a list of stock tickers, calculates moving averages, 
    and checks for simple technical alerts (e.g. price dropping significantly).
    """
    print("--- Jarvis Market Scanner Initializing ---\n")
    
    alerts = []
    
    for ticker in tickers:
        print(f"Analyzing {ticker}...")
        try:
            # Fetch last 3 months of daily data
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if hist.empty:
                print(f"No data found for {ticker}")
                continue
                
            # Calculate 50-day moving average
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            
            current_price = hist['Close'].iloc[-1]
            sma_50 = hist['SMA_50'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            
            # Simple daily change percentage
            daily_change = ((current_price - prev_close) / prev_close) * 100
            
            # Alert Logic 1: Big daily move
            if abs(daily_change) > 5.0:
                direction = "UP" if daily_change > 0 else "DOWN"
                alerts.append(f"ALERT: {ticker} moved {direction} by {abs(daily_change):.2f}% today (Current: ${current_price:.2f})")
                
            # Alert Logic 2: Price crossed moving average
            if not pd.isna(sma_50):
                if current_price > sma_50 and prev_close <= hist['SMA_50'].iloc[-2]:
                    alerts.append(f"SIGNAL: {ticker} just crossed ABOVE its 50-day moving average!")
                elif current_price < sma_50 and prev_close >= hist['SMA_50'].iloc[-2]:
                    alerts.append(f"SIGNAL: {ticker} just crossed BELOW its 50-day moving average!")

        except Exception as e:
            print(f"Error scanning {ticker}: {e}")

    print("\n--- Market Scanner Results ---")
    if not alerts:
        print("Market is quiet. No major alerts triggered for your watchlist.")
    else:
        for alert in alerts:
            print(alert)

if __name__ == "__main__":
    my_watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'BTC-USD']
    scan_market(my_watchlist)

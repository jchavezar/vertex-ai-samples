import random
import datetime
import yfinance as yf
from typing import List, Dict, Any

def generate_mock_price(ticker: str) -> float:
    """Fallback: Generates a consistent but realistic-looking current price for a ticker."""
    base = sum(ord(c) for c in ticker) % 200 + 50 
    drift = random.uniform(-5, 5)
    return round(base + drift, 2)

def generate_mock_history(ticker: str, days: int = 30) -> List[Dict[str, Any]]:
    """Fallback: Generates a random walk history."""
    base = sum(ord(c) for c in ticker) % 200 + 50
    history = []
    current = base
    start_date = datetime.date.today() - datetime.timedelta(days=days)
    for i in range(days + 1):
        dt = start_date + datetime.timedelta(days=i)
        if dt.weekday() >= 5: continue 
        change_pct = random.gauss(0.0005, 0.02)
        current = current * (1 + change_pct)
        history.append({
            "date": dt.strftime("%Y-%m-%d"),
            "close": round(current, 2)
        })
    return history

def get_mock_price_response(ticker: str) -> Dict[str, Any]:
    """Fetches REAL price from Yahoo Finance, falls back to mock if fails."""
    try:
        t = yf.Ticker(ticker)
        # fast_info is often faster/more reliable for current price than .info
        price = t.fast_info.last_price
        if price is None:
             # Try regular info
             price = t.info.get('currentPrice') or t.info.get('regularMarketPrice')
        
        if price:
            now = datetime.datetime.now()
            return {
                "ticker": ticker.upper(),
                "price": round(price, 2),
                "currency": "USD", # Simplified, usually USD for US stocks
                "time": f"""
    Current Time: {now.isoformat()}
    Today: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})
    Source: Yahoo Finance (Real-Time)
    """
            }
    except Exception as e:
        print(f"Error fetching real price for {ticker}: {e}")
    
    # Fallback
    price = generate_mock_price(ticker)
    now = datetime.datetime.now()
    return {
        "ticker": ticker.upper(),
        "price": price,
        "currency": "USD",
        "time": f"""
    Current Time: {now.isoformat()}
    Today: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})
    Source: Synthetic (Fallback)
    """
    }

def get_mock_history_response(ticker: str, start_date=None, end_date=None) -> Dict[str, Any]:
    """Fetches REAL history from Yahoo Finance."""
    try:
        t = yf.Ticker(ticker)
        # default to 3mo if not specified, or reasonable range
        # yfinance history handles strings like "1mo", "3mo", "1y"
        # but our interface might pass specific dates.
        # Let's just fetch "3mo" for now as a safe default for charts
        period = "6mo"
        hist_df = t.history(period=period)
        
        if not hist_df.empty:
            history = []
            for date, row in hist_df.iterrows():
                history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(row['Close'], 2)
                })
            return {
                "ticker": ticker.upper(),
                "history": history
            }
    except Exception as e:
        print(f"Error fetching real history for {ticker}: {e}")

    # Fallback
    hist = generate_mock_history(ticker, days=90)
    return {
        "ticker": ticker.upper(),
        "history": hist
    }

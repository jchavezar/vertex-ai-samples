import datetime
import yfinance as yf
from typing import List, Dict, Any, Optional

def get_real_price(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetches REAL price from Yahoo Finance. Returns None if fails."""
    try:
        # Sanitize ticker for yfinance (FactSet uses Ticker-US, yfinance uses Ticker)
        yf_ticker = ticker.replace("-US", "").replace("-USA", "")
        t = yf.Ticker(yf_ticker)
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
    
    return None

def get_real_history(ticker: str, period: str = "6mo") -> Optional[Dict[str, Any]]:
    """Fetches REAL history from Yahoo Finance. Returns None if fails."""
    try:
        # Sanitize ticker for yfinance
        yf_ticker = ticker.replace("-US", "").replace("-USA", "")
        t = yf.Ticker(yf_ticker)
        
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

    return None

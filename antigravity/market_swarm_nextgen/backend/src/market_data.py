import datetime
import yfinance as yf
from typing import List, Dict, Any, Optional

def get_real_price(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetches REAL price from Yahoo Finance. Returns None if fails."""
    try:
        # Sanitize ticker for yfinance (FactSet uses Ticker-US, yfinance uses Ticker)
        yf_ticker = ticker.replace("-US", "").replace("-USA", "")
        t = yf.Ticker(yf_ticker)
        # fast_info is good for price, but .info has the official 'change' fields that match the website
        # We need to access .info to get the correct previous close and calculated change
        info = {}
        try:
             info = t.info
        except:
             pass
        
        price = t.fast_info.last_price
        if price is None:
             price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        if price:
            # Prioritize explicit Change fields from Yahoo (matches their UI)
            change = info.get('regularMarketChange')
            change_percent = info.get('regularMarketChangePercent')
            
            # Fallback Calculation if explicit fields missing
            if change is None or change_percent is None:
                previous_close = info.get('regularMarketPreviousClose') or info.get('previousClose') or t.fast_info.previous_close
                if previous_close:
                    change = price - previous_close
                    if previous_close != 0:
                        change_percent = (change / previous_close) * 100
                else:
                    change = 0.0
                    change_percent = 0.0
            else:
                # Yahoo returns percent as 0.44 for 0.44%? Or 0.0044? 
                # Debug output said: regularMarketChangePercent: 0.446654
                # Usually Yahoo .info returns the float value (e.g. 0.44 is 0.44%).
                # BUT wait, let's check debug output again.
                # regularMarketPrice: 269.86. Previous: 268.66. Diff: +1.20.
                # 1.20 / 268.66 = 0.004466... 
                # Debug output: 0.446654. So it is multiplied by 100 already?
                # 0.0044 * 100 = 0.44. Yes.
                # But sometimes it might be raw? 
                # Text usually expects "0.45%". 
                # My frontend expects the value to be the number to display.
                pass

            now = datetime.datetime.now()
            return {
                "ticker": ticker.upper(),
                "price": round(price, 2),
                "change": round(change, 2) if change else 0.0,
                "changePercent": round(change_percent, 2) if change_percent else 0.0,
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

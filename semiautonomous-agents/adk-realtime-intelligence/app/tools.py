"""Real-time tools for the Google ADK Intelligence Agent.

In the Google Agent Development Kit (ADK), tools can be regular Python functions.
ADK automatically parses:
  1. The function name and signature (type hints).
  2. The docstring (description, arguments, return schema).
These are converted into OpenAPI function declarations for the Gemini model.
"""

from typing import Any, Dict
import httpx
import yfinance as yf


def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """Fetch the real-time stock price and day metrics for a company or ETF.

    Args:
        ticker: The stock ticker symbol (e.g. GOOGL, AAPL, MSFT, NVDA, AMZN, TSLA).

    Returns:
        A dictionary containing ticker, current price, previous close, currency, and status.
    """
    try:
        t = yf.Ticker(ticker.strip().upper())
        info = t.fast_info
        price = getattr(info, "last_price", None)
        prev_close = getattr(info, "previous_close", None)
        currency = getattr(info, "currency", "USD")

        if price is None:
            return {
                "status": "error",
                "message": f"Unable to fetch live price for ticker '{ticker}'. Please verify the symbol.",
            }

        change = round(float(price - prev_close), 2) if prev_close else 0.0
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "current_price": round(float(price), 2),
            "previous_close": round(float(prev_close), 2) if prev_close else None,
            "change": change,
            "change_percent": f"{change_pct:+.2f}%",
            "currency": currency,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Error retrieving stock quote: {str(exc)}"}


def get_company_profile(ticker: str) -> Dict[str, Any]:
    """Fetch company profile, sector, industry, market cap, and business summary.

    Args:
        ticker: The stock ticker symbol (e.g. GOOGL, AAPL, MSFT).

    Returns:
        A dictionary containing company name, sector, industry, market cap, and business summary.
    """
    try:
        t = yf.Ticker(ticker.strip().upper())
        info = t.info or {}
        summary = info.get("longBusinessSummary", "No summary available.")
        if len(summary) > 400:
            summary = summary[:400] + "..."

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "company_name": info.get("longName", ticker.upper()),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "website": info.get("website", "N/A"),
            "summary": summary,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Error retrieving company profile: {str(exc)}"}


def get_live_weather(city: str) -> Dict[str, Any]:
    """Fetch current real-time weather and temperature for any city worldwide.

    Uses Open-Meteo geocoding and real-time atmospheric measurements. Zero API key required.

    Args:
        city: The name of the city (e.g. 'Tokyo', 'London', 'San Francisco', 'New York').

    Returns:
        A dictionary containing city, country, temperature in Celsius and Fahrenheit,
        windspeed, weather condition, and local observation timestamp.
    """
    try:
        # Step 1: Geocode the city name to latitude and longitude
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        with httpx.Client(timeout=8.0) as client:
            geo_resp = client.get(geo_url, params={"name": city.strip(), "count": 1})
            geo_data = geo_resp.json()

            if not geo_data.get("results"):
                return {"status": "error", "message": f"Location '{city}' could not be resolved."}

            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = location.get("name", city)
            country = location.get("country", "")

            # Step 2: Fetch current weather metrics
            weather_url = "https://api.open-meteo.com/v1/forecast"
            w_resp = client.get(
                weather_url,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                },
            )
            w_data = w_resp.json().get("current_weather", {})

        temp_c = w_data.get("temperature", 0.0)
        temp_f = round((temp_c * 9 / 5) + 32, 1)

        # WMO Weather interpretation code mapping
        wmo_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
        }
        condition = wmo_codes.get(w_data.get("weathercode", 0), "Clear / Fair")

        return {
            "status": "success",
            "city": city_name,
            "country": country,
            "temperature_celsius": temp_c,
            "temperature_fahrenheit": temp_f,
            "condition": condition,
            "windspeed_kmh": w_data.get("windspeed"),
            "observation_time": w_data.get("time"),
        }
    except Exception as exc:
        return {"status": "error", "message": f"Error fetching weather data: {str(exc)}"}


def get_crypto_quote(symbol: str) -> Dict[str, Any]:
    """Fetch the real-time price and 24-hour change for major cryptocurrencies.

    Args:
        symbol: The cryptocurrency symbol or name (e.g. 'btc', 'eth', 'sol', 'bitcoin', 'ethereum').

    Returns:
        A dictionary with coin name, price in USD, 24h percentage change, and status.
    """
    try:
        sym = symbol.lower().strip()
        coin_mapping = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "sol": "solana",
            "doge": "dogecoin",
            "xrp": "ripple",
            "ada": "cardano",
            "dot": "polkadot",
            "avax": "avalanche-2",
        }
        coin_id = coin_mapping.get(sym, sym)

        url = "https://api.coingecko.com/api/v3/simple/price"
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(
                url,
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                },
            )
            data = resp.json()

        if coin_id in data:
            price = data[coin_id].get("usd")
            change_24h = data[coin_id].get("usd_24h_change", 0.0)
            return {
                "status": "success",
                "coin": coin_id.capitalize(),
                "price_usd": f"${price:,.2f}" if price else "N/A",
                "change_24h_percent": f"{change_24h:+.2f}%" if change_24h is not None else "N/A",
            }

        return {
            "status": "error",
            "message": f"Cryptocurrency '{symbol}' not found. Try 'btc', 'eth', or 'sol'.",
        }
    except Exception as exc:
        return {"status": "error", "message": f"Error fetching crypto quote: {str(exc)}"}

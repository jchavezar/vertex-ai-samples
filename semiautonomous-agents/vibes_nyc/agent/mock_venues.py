"""
Mock venue data for development.
Avoids burning Foursquare API calls (200K/month limit) during testing.
Set USE_MOCK_DATA=true in .env to enable.
"""
from datetime import datetime


# hours_schedule: {weekday_int: (open_h, open_m, close_h, close_m)}  0=Mon 6=Sun
_COFFEE_SCHEDULE = {
    0: (7, 0, 18, 0),   # Mon
    1: (7, 0, 18, 0),   # Tue
    2: (7, 0, 18, 0),   # Wed
    3: (7, 0, 18, 0),   # Thu
    4: (7, 0, 18, 0),   # Fri
    5: (8, 0, 17, 0),   # Sat
    6: (8, 0, 17, 0),   # Sun
}

_BAR_SCHEDULE = {
    # Mon closed
    1: (18, 0, 26, 0),  # Tue (26h = 2am next day)
    2: (18, 0, 26, 0),
    3: (18, 0, 26, 0),
    4: (18, 0, 26, 0),
    5: (17, 0, 26, 0),  # Fri
    6: (17, 0, 26, 0),  # Sat
}


def _fmt(h: int, m: int) -> str:
    """Convert 24h (or >24h for 2am=26) to 12h display."""
    h24 = h % 24
    period = "AM" if h24 < 12 else "PM"
    h12 = h24 % 12 or 12
    return f"{h12}:{m:02d} {period}"


def _compute_status(schedule: dict) -> dict:
    """Return open/closed status dict based on current local time."""
    now = datetime.now()
    dow = now.weekday()
    entry = schedule.get(dow)

    # Check holiday (US federal holidays hardcoded as examples)
    federal_holidays = {(1, 1), (7, 4), (12, 25), (11, 28), (12, 26)}  # approximate
    today = (now.month, now.day)
    if today in federal_holidays:
        return {
            "is_open_now": False,
            "status": "Closed",
            "open_until": None,
            "is_holiday_closure": True,
            "holiday_note": "Closed for holiday",
            "display": _schedule_to_display(schedule),
        }

    if entry is None:
        return {
            "is_open_now": False,
            "status": "Closed today",
            "open_until": None,
            "is_holiday_closure": False,
            "holiday_note": None,
            "display": _schedule_to_display(schedule),
        }

    oh, om, ch, cm = entry
    current_minutes = now.hour * 60 + now.minute
    open_minutes = oh * 60 + om
    close_minutes = ch * 60 + cm  # may exceed 1440 (midnight rollover)

    is_open = open_minutes <= current_minutes < close_minutes
    close_display = _fmt(ch, cm)
    open_display = _fmt(oh, om)

    if is_open:
        status = f"Open until {close_display}"
    elif current_minutes < open_minutes:
        status = f"Opens at {open_display}"
    else:
        status = "Closed"

    return {
        "is_open_now": is_open,
        "status": status,
        "open_until": close_display if is_open else None,
        "is_holiday_closure": False,
        "holiday_note": None,
        "display": _schedule_to_display(schedule),
    }


def _schedule_to_display(schedule: dict) -> str:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    parts = []
    for dow, entry in sorted(schedule.items()):
        oh, om, ch, cm = entry
        parts.append(f"{days[dow]} {_fmt(oh, om)}–{_fmt(ch, cm)}")
    if not parts:
        return "Hours unavailable"
    # Compact: Mon–Fri if same hours
    return "  ·  ".join(parts[:2]) + ("  ·  ..." if len(parts) > 2 else "")

_COFFEE_HOURS = _compute_status(_COFFEE_SCHEDULE)
_BAR_HOURS    = _compute_status(_BAR_SCHEDULE)

# Curated Unsplash photos — stable direct CDN links, no API key needed
# Coffee shops: intimate interior shots that match each venue's vibe
_P = "https://images.unsplash.com/photo-"

MOCK_COFFEE_VENUES = [
    {
        "fsq_id": "mock_coffee_1",
        "yelp_id": "mock_coffee_1",
        "name": "L Stop Coffee Shop",
        "rating": 4.0,
        "review_count": 45,
        "price": "$",
        "address": "490 Metropolitan Ave, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "categories": ["Coffee Shop"],
        "is_closed": False,
        # industrial / exposed brick / lo-fi
        "photos": [_P + "1501339847302-ac426a4a7cbb?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock1",
        "coordinates": {"latitude": 40.7142, "longitude": -73.9512},
        "distance": 250,
    },
    {
        "fsq_id": "mock_coffee_2",
        "yelp_id": "mock_coffee_2",
        "name": "Devocion",
        "rating": 4.5,
        "review_count": 890,
        "price": "$$",
        "address": "69 Grand St, Brooklyn, NY 11249",
        "neighborhood": "Williamsburg",
        "categories": ["Coffee Shop", "Cafe"],
        "is_closed": False,
        # airy greenhouse / lush greenery
        "photos": [_P + "1525610553991-2bede1a236e2?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock2",
        "coordinates": {"latitude": 40.7138, "longitude": -73.9618},
        "distance": 450,
    },
    {
        "fsq_id": "mock_coffee_3",
        "yelp_id": "mock_coffee_3",
        "name": "Starbucks Reserve",
        "rating": 4.0,
        "review_count": 2500,
        "price": "$$",
        "address": "154 N 7th St, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "categories": ["Coffee Shop"],
        "is_closed": False,
        # polished / commercial / dark wood
        "photos": [_P + "1481833761820-0509d3217039?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock3",
        "coordinates": {"latitude": 40.7172, "longitude": -73.9582},
        "distance": 320,
    },
    {
        "fsq_id": "mock_coffee_4",
        "yelp_id": "mock_coffee_4",
        "name": "Blue Bottle Coffee",
        "rating": 4.2,
        "review_count": 1200,
        "price": "$$",
        "address": "160 Berry St, Brooklyn, NY 11249",
        "neighborhood": "Williamsburg",
        "categories": ["Coffee Shop"],
        "is_closed": False,
        # minimal / white / clean lines
        "photos": [_P + "1509315811345-672d83ef2fbc?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock4",
        "coordinates": {"latitude": 40.7198, "longitude": -73.9601},
        "distance": 580,
    },
    {
        "fsq_id": "mock_coffee_5",
        "yelp_id": "mock_coffee_5",
        "name": "Variety Coffee Roasters",
        "rating": 4.4,
        "review_count": 320,
        "price": "$",
        "address": "368 Graham Ave, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "categories": ["Coffee Shop", "Roastery"],
        "is_closed": False,
        # roastery / bags of coffee / industrial bright
        "photos": [_P + "1493770348161-369560ae357d?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock5",
        "coordinates": {"latitude": 40.7145, "longitude": -73.9445},
        "distance": 680,
    },
    {
        "fsq_id": "mock_coffee_6",
        "yelp_id": "mock_coffee_6",
        "name": "Hidden Gem Cafe",
        "rating": 4.8,
        "review_count": 28,
        "price": "$",
        "address": "123 Bedford Ave, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "categories": ["Coffee Shop", "Cafe"],
        "is_closed": False,
        # cozy / intimate / warm lighting / small tables
        "photos": [_P + "1554118811-1e0d58224f24?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock6",
        "coordinates": {"latitude": 40.7188, "longitude": -73.9572},
        "distance": 150,
    },
]

MOCK_COCKTAIL_VENUES = [
    {
        "fsq_id": "mock_cocktail_1",
        "yelp_id": "mock_cocktail_1",
        "name": "Attaboy",
        "rating": 4.7,
        "review_count": 180,
        "price": "$$$",
        "address": "134 Eldridge St, New York, NY 10002",
        "neighborhood": "Lower East Side",
        "categories": ["Cocktail Bar", "Speakeasy"],
        "is_closed": False,
        # dark speakeasy / moody / backlit bottles
        "photos": [_P + "1567521464027-f127ff144326?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock7",
        "coordinates": {"latitude": 40.7185, "longitude": -73.9912},
        "distance": 320,
    },
    {
        "fsq_id": "mock_cocktail_2",
        "yelp_id": "mock_cocktail_2",
        "name": "Death & Co",
        "rating": 4.5,
        "review_count": 2100,
        "price": "$$$",
        "address": "433 E 6th St, New York, NY 10009",
        "neighborhood": "East Village",
        "categories": ["Cocktail Bar"],
        "is_closed": False,
        # dark wood / intimate bar seating / candlelight
        "photos": [_P + "1559925393-8be0ec4767c8?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock8",
        "coordinates": {"latitude": 40.7262, "longitude": -73.9852},
        "distance": 890,
    },
    {
        "fsq_id": "mock_cocktail_3",
        "yelp_id": "mock_cocktail_3",
        "name": "Please Don't Tell",
        "rating": 4.6,
        "review_count": 1800,
        "price": "$$$",
        "address": "113 St Marks Pl, New York, NY 10009",
        "neighborhood": "East Village",
        "categories": ["Cocktail Bar", "Speakeasy"],
        "is_closed": False,
        # hidden entrance / vintage / moody red
        "photos": [_P + "1571019613454-1cb2f99b2d8b?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock9",
        "coordinates": {"latitude": 40.7275, "longitude": -73.9842},
        "distance": 950,
    },
    {
        "fsq_id": "mock_cocktail_4",
        "yelp_id": "mock_cocktail_4",
        "name": "Suffolk Arms",
        "rating": 4.4,
        "review_count": 95,
        "price": "$$",
        "address": "269 E Houston St, New York, NY 10002",
        "neighborhood": "Lower East Side",
        "categories": ["Cocktail Bar"],
        "is_closed": False,
        # neighbourhood bar / warm / low-key
        "photos": [_P + "1537944434965-cf4679d1a598?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock10",
        "coordinates": {"latitude": 40.7222, "longitude": -73.9878},
        "distance": 420,
    },
    {
        "fsq_id": "mock_cocktail_5",
        "yelp_id": "mock_cocktail_5",
        "name": "Nitecap",
        "rating": 4.5,
        "review_count": 65,
        "price": "$$",
        "address": "151 Rivington St, New York, NY 10002",
        "neighborhood": "Lower East Side",
        "categories": ["Cocktail Bar"],
        "is_closed": False,
        # late night / neon / cozy underground
        "photos": [_P + "1560707303-4e980ce876ad?w=800&fit=crop&q=80"],
        "url": "https://foursquare.com/v/mock11",
        "coordinates": {"latitude": 40.7198, "longitude": -73.9868},
        "distance": 280,
    },
]

def get_mock_venues(query: str) -> list[dict]:
    """Return mock venues based on query type, with live-computed hours."""
    query_lower = query.lower()
    is_bar = any(word in query_lower for word in ["cocktail", "bar", "drink", "night"])

    venues = MOCK_COCKTAIL_VENUES if is_bar else MOCK_COFFEE_VENUES
    schedule = _BAR_SCHEDULE if is_bar else _COFFEE_SCHEDULE

    # Recompute hours at call time so open/closed reflects actual current time
    live_hours = _compute_status(schedule)
    return [{**v, "hours": live_hours} for v in venues]

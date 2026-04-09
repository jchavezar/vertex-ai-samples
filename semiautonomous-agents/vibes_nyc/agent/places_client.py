"""
Google Places API (New) client.
Free tier: 10,000 calls/month on vtxdemos project.
Docs: https://developers.google.com/maps/documentation/places/web-service/text-search
"""
import os
import httpx
from typing import Optional

SEARCH_URL  = "https://places.googleapis.com/v1/places:searchText"
DETAIL_URL  = "https://places.googleapis.com/v1/places/{place_id}"
PHOTO_URL   = "https://places.googleapis.com/v1/{name}/media?maxWidthPx=800&key={api_key}"

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.rating",
    "places.userRatingCount",
    "places.priceLevel",
    "places.currentOpeningHours",
    "places.regularOpeningHours",
    "places.photos",
    "places.types",
    "places.googleMapsUri",
    "places.businessStatus",
    "places.editorialSummary",
    "places.reviews",
    "places.delivery",
    "places.dineIn",
])

_PRICE_MAP = {
    "PRICE_LEVEL_FREE":           "",
    "PRICE_LEVEL_INEXPENSIVE":    "$",
    "PRICE_LEVEL_MODERATE":       "$$",
    "PRICE_LEVEL_EXPENSIVE":      "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

_DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Category photo fallback (Unsplash, verified 200)
_CATEGORY_PHOTOS = {
    "coffee_shop": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&fit=crop&q=80",
    "cafe":        "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800&fit=crop&q=80",
    "bar":         "https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=800&fit=crop&q=80",
    "restaurant":  "https://images.unsplash.com/photo-1481833761820-0509d3217039?w=800&fit=crop&q=80",
    "bakery":      "https://images.unsplash.com/photo-1509315811345-672d83ef2fbc?w=800&fit=crop&q=80",
    "default":     "https://images.unsplash.com/photo-1560707303-4e980ce876ad?w=800&fit=crop&q=80",
}


class GooglePlacesClient:

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "")

    def _headers(self, field_mask: str) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask,
        }

    def _category_photo(self, types: list[str]) -> str:
        for t in types:
            if t in _CATEGORY_PHOTOS:
                return _CATEGORY_PHOTOS[t]
        return _CATEGORY_PHOTOS["default"]

    def _photo_url(self, photos: list[dict]) -> list[str]:
        """Build photo URLs from Places API photo references."""
        urls = []
        for p in photos[:3]:
            name = p.get("name", "")
            if name:
                urls.append(PHOTO_URL.format(name=name, api_key=self.api_key))
        return urls

    def _map_hours(self, opening_hours: Optional[dict]) -> Optional[dict]:
        if not opening_hours:
            return None

        is_open = opening_hours.get("openNow", False)
        periods = opening_hours.get("periods", [])
        weekday_text = opening_hours.get("weekdayDescriptions", [])

        # Build compact display from weekdayDescriptions
        display = "  ·  ".join(weekday_text[:2]) + ("  ·  ..." if len(weekday_text) > 2 else "")

        # Find what time it closes today
        open_until = None
        from datetime import datetime
        today_dow = datetime.now().weekday()
        google_dow = (today_dow + 1) % 7  # Google: 0=Sun, Python: 0=Mon
        for period in periods:
            if period.get("open", {}).get("day") == google_dow:
                close = period.get("close", {})
                if close:
                    h, m = close.get("hour", 0), close.get("minute", 0)
                    period_str = "AM" if h < 12 else "PM"
                    h12 = h % 12 or 12
                    open_until = f"{h12}:{m:02d} {period_str}"
                break

        status = f"Open until {open_until}" if (is_open and open_until) else ("Open now" if is_open else "Closed")

        return {
            "is_open_now": is_open,
            "status": status,
            "open_until": open_until,
            "is_holiday_closure": False,
            "holiday_note": None,
            "display": display,
        }

    def _normalize(self, p: dict, user_lat: float = None, user_lon: float = None) -> dict:
        types = p.get("types", [])
        location = p.get("location", {})
        display_name = p.get("displayName", {}).get("text", "")
        photos_raw = p.get("photos", [])

        # Photos: use real Google photo URLs, fall back to Unsplash category
        photos = self._photo_url(photos_raw) or [self._category_photo(types)]

        # Distance from user location
        distance = None
        if user_lat and user_lon:
            import math
            lat2 = location.get("latitude", 0)
            lon2 = location.get("longitude", 0)
            dlat = math.radians(lat2 - user_lat)
            dlon = math.radians(lon2 - user_lon)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(user_lat)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            distance = int(6371000 * 2 * math.asin(math.sqrt(a)))

        # Business status
        is_closed = p.get("businessStatus", "OPERATIONAL") != "OPERATIONAL"

        # Editorial summary as vibe hint
        summary = p.get("editorialSummary", {}).get("text", "")

        return {
            "fsq_id": p.get("id"),
            "yelp_id": p.get("id"),
            "name": display_name,
            "rating": p.get("rating", 0.0),
            "review_count": p.get("userRatingCount", 0),
            "price": _PRICE_MAP.get(p.get("priceLevel", ""), ""),
            "address": p.get("formattedAddress", ""),
            "neighborhood": "",
            "categories": [t.replace("_", " ").title() for t in types if not t in ("point_of_interest", "establishment", "food", "store")],
            "is_closed": is_closed,
            "photos": photos,
            "url": p.get("googleMapsUri", ""),
            "coordinates": {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
            },
            "distance": distance,
            "hours": self._map_hours(p.get("currentOpeningHours") or p.get("regularOpeningHours")),
            "editorial_summary": summary,
            "reviews": [r.get("text", {}).get("text", "") for r in p.get("reviews", []) if r.get("text", {}).get("text")],
        }

    async def search(
        self,
        query: str,
        lat: float,
        lon: float,
        radius: int = 1500,
        limit: int = 20,
        open_now: bool = False,
    ) -> list[dict]:
        """Text search for places near a location."""
        if os.environ.get("USE_MOCK_DATA", "false").lower() == "true":
            from mock_venues import get_mock_venues
            print(f"[GooglePlaces] MOCK MODE: '{query}'")
            return get_mock_venues(query)

        if not self.api_key:
            print("[GooglePlaces] GOOGLE_PLACES_API_KEY not set")
            return []

        body = {
            "textQuery": query,
            "maxResultCount": min(limit, 20),
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lon},
                    "radius": float(radius),
                }
            },
        }
        if open_now:
            body["openNow"] = True

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(SEARCH_URL, json=body, headers=self._headers(FIELD_MASK))
                if not resp.is_success:
                    print(f"[GooglePlaces] Error {resp.status_code}: {resp.text[:300]}")
                    return []
                places = resp.json().get("places", [])
                print(f"[GooglePlaces] {len(places)} places for '{query}'")
                return [self._normalize(p, lat, lon) for p in places]
        except Exception as e:
            print(f"[GooglePlaces] Search error: {e}")
            return []

    async def get_details(self, place_id: str) -> dict:
        """Get full place details."""
        if not self.api_key:
            return {}
        detail_mask = FIELD_MASK.replace("places.", "")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    DETAIL_URL.format(place_id=place_id),
                    headers=self._headers(detail_mask),
                )
                if resp.is_success:
                    return self._normalize(resp.json())
                return {}
        except Exception as e:
            print(f"[GooglePlaces] Details error: {e}")
            return {}

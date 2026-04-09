"""
Foursquare Places API Client (v3).
Free tier: 200,000 calls/month.
Docs: https://docs.foursquare.com/developer/reference/place-search
"""
import os
import httpx
from typing import Optional


class FoursquareClient:
    """
    Foursquare Places API v3 client.
    Uses Bearer token authentication (Service API Key).
    """

    SEARCH_URL  = "https://api.foursquare.com/v3/places/search"
    DETAIL_URL  = "https://api.foursquare.com/v3/places/{fsq_id}"
    PHOTOS_URL  = "https://api.foursquare.com/v3/places/{fsq_id}/photos"

    # Category → curated Unsplash fallback (used when venue has no photos)
    _CATEGORY_PHOTOS = {
        "coffee":    "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&fit=crop&q=80",
        "cafe":      "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800&fit=crop&q=80",
        "roastery":  "https://images.unsplash.com/photo-1493770348161-369560ae357d?w=800&fit=crop&q=80",
        "cocktail":  "https://images.unsplash.com/photo-1567521464027-f127ff144326?w=800&fit=crop&q=80",
        "bar":       "https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=800&fit=crop&q=80",
        "speakeasy": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&fit=crop&q=80",
        "wine":      "https://images.unsplash.com/photo-1537944434965-cf4679d1a598?w=800&fit=crop&q=80",
        "brewery":   "https://images.unsplash.com/photo-1525610553991-2bede1a236e2?w=800&fit=crop&q=80",
        "bakery":    "https://images.unsplash.com/photo-1509315811345-672d83ef2fbc?w=800&fit=crop&q=80",
        "restaurant":"https://images.unsplash.com/photo-1481833761820-0509d3217039?w=800&fit=crop&q=80",
        "default":   "https://images.unsplash.com/photo-1560707303-4e980ce876ad?w=800&fit=crop&q=80",
    }

    def __init__(self):
        self.api_key = os.environ.get("FOURSQUARE_API_KEY", "")
        self.headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
        }

    def _category_photo(self, categories: list[str]) -> str:
        joined = " ".join(c.lower() for c in categories)
        for key in self._CATEGORY_PHOTOS:
            if key in joined:
                return self._CATEGORY_PHOTOS[key]
        return self._CATEGORY_PHOTOS["default"]

    def _map_hours(self, hours: dict) -> Optional[dict]:
        if not hours:
            return None

        is_open = hours.get("open_now", False)
        display_hours = hours.get("display", "")
        regular = hours.get("regular", [])

        # Build compact display: "Mon-Fri 7:00 AM-6:00 PM"
        display = display_hours or (regular[0].get("open", "") if regular else "")

        return {
            "is_open_now": is_open,
            "status": "Open now" if is_open else "Closed",
            "open_until": None,
            "is_holiday_closure": False,
            "holiday_note": None,
            "display": display,
        }

    def _normalize(self, v: dict) -> dict:
        """Normalize Foursquare v3 place response to app format."""
        location = v.get("location", {})
        categories = v.get("categories", [])
        cat_names = [c.get("name", "") for c in categories]

        # Full address
        address_parts = [
            location.get("address", ""),
            location.get("locality", ""),
            location.get("region", ""),
            location.get("postcode", ""),
        ]
        address = ", ".join(p for p in address_parts if p)

        # Photos: v3 returns prefix/suffix pairs
        photos_raw = v.get("photos", [])
        photos = []
        for p in photos_raw:
            prefix = p.get("prefix", "")
            suffix = p.get("suffix", "")
            if prefix and suffix:
                photos.append(f"{prefix}800x450{suffix}")  # 800x450 crop
        if not photos:
            photos = [self._category_photo(cat_names)]

        # Price: v3 uses 1-4 integer
        price = "$" * v.get("price", 0) if v.get("price") else ""

        # Stats: v3 has popularity (0-1) and rating (0-10)
        rating = round(v.get("rating", 0) / 2, 1) if v.get("rating") else 4.0
        # Use stats.total_ratings as review_count proxy
        stats = v.get("stats", {})
        review_count = stats.get("total_ratings", stats.get("total_tips", 0))

        # Hours
        hours = self._map_hours(v.get("hours"))

        # Popularity (0.0–1.0) — useful for underground score
        popularity = v.get("popularity", 0.0)

        geocodes = v.get("geocodes", {}).get("main", {})

        return {
            "fsq_id": v.get("fsq_id"),
            "yelp_id": v.get("fsq_id"),
            "name": v.get("name"),
            "rating": rating,
            "review_count": review_count,
            "popularity": popularity,
            "price": price,
            "address": address,
            "neighborhood": location.get("neighborhood", location.get("locality", "")),
            "categories": cat_names,
            "is_closed": not (v.get("hours", {}) or {}).get("open_now", True),
            "photos": photos,
            "url": f"https://foursquare.com/v/{v.get('fsq_id')}",
            "coordinates": {
                "latitude": geocodes.get("latitude"),
                "longitude": geocodes.get("longitude"),
            },
            "distance": v.get("distance"),
            "hours": hours,
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
        """Search Foursquare v3 Places API."""
        if os.environ.get("USE_MOCK_DATA", "false").lower() == "true":
            from mock_venues import get_mock_venues
            print(f"[Foursquare] MOCK MODE: '{query}'")
            return get_mock_venues(query)

        if not self.api_key:
            print("[Foursquare] FOURSQUARE_API_KEY not set")
            return []

        params = {
            "query": query,
            "ll": f"{lat},{lon}",
            "radius": radius,
            "limit": limit,
            "fields": "fsq_id,name,location,categories,hours,photos,price,rating,stats,popularity,geocodes,distance",
        }
        if open_now:
            params["open_now"] = "true"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(self.SEARCH_URL, headers=self.headers, params=params)
                if not resp.is_success:
                    print(f"[Foursquare] Error {resp.status_code}: {resp.text[:300]}")
                    return []
                results = resp.json().get("results", [])
                print(f"[Foursquare] v3: {len(results)} venues for '{query}'")
                return [self._normalize(p) for p in results]
        except Exception as e:
            print(f"[Foursquare] Search error: {e}")
            return []

    async def get_details(self, fsq_id: str) -> dict:
        """Get full venue details including photos."""
        if not self.api_key:
            return {}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    self.DETAIL_URL.format(fsq_id=fsq_id),
                    headers=self.headers,
                    params={"fields": "fsq_id,name,location,categories,hours,photos,price,rating,stats,popularity,geocodes,distance"},
                )
                if resp.is_success:
                    return self._normalize(resp.json())
                return {}
        except Exception as e:
            print(f"[Foursquare] Details error: {e}")
            return {}

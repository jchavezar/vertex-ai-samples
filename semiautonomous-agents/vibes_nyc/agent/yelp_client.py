"""
Yelp Fusion API Client.
Free tier: 5,000 requests/day.
"""
import os
import httpx
from typing import Optional


class YelpClient:
    """
    Yelp Fusion API client for venue search.
    Requires YELP_API_KEY environment variable.
    """

    BASE_URL = "https://api.yelp.com/v3/businesses/search"
    DETAIL_URL = "https://api.yelp.com/v3/businesses/{id}"

    def __init__(self):
        self.api_key = os.environ.get("YELP_API_KEY", "")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def search(
        self,
        term: str,
        lat: float,
        lon: float,
        radius: int = 1500,  # meters (~1 mile)
        limit: int = 20,
        open_now: bool = True,
        price: Optional[str] = None,  # "1,2" for $ and $$
    ) -> list[dict]:
        """
        Search Yelp for venues.

        Args:
            term: Search term (e.g., "coffee", "cocktail bar")
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (max 40000)
            limit: Max results (max 50)
            open_now: Filter to currently open venues
            price: Price filter ("1", "1,2", etc.)

        Returns:
            List of normalized venue dictionaries
        """
        if not self.api_key:
            print("[Yelp] Warning: YELP_API_KEY not set")
            return []

        params = {
            "term": term,
            "latitude": lat,
            "longitude": lon,
            "radius": radius,
            "limit": limit,
            "open_now": open_now,
            "sort_by": "best_match",
        }
        if price:
            params["price"] = price

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    self.BASE_URL,
                    headers=self.headers,
                    params=params
                )

                if not resp.is_success:
                    print(f"[Yelp] API error: {resp.status_code} - {resp.text[:200]}")
                    return []

                data = resp.json()
                return [self._normalize(b) for b in data.get("businesses", [])]

        except Exception as e:
            print(f"[Yelp] Search error: {e}")
            return []

    def _normalize(self, b: dict) -> dict:
        """Normalize Yelp business response to standard format."""
        return {
            "yelp_id": b.get("id"),
            "name": b.get("name"),
            "rating": b.get("rating"),
            "review_count": b.get("review_count"),
            "price": b.get("price", ""),
            "address": ", ".join(b.get("location", {}).get("display_address", [])),
            "neighborhood": b.get("location", {}).get("city", ""),
            "categories": [c["title"] for c in b.get("categories", [])],
            "is_closed": b.get("is_closed", False),
            "photos": [b.get("image_url")] if b.get("image_url") else [],
            "url": b.get("url"),
            "coordinates": b.get("coordinates", {}),
            "distance": b.get("distance"),
        }

    async def get_details(self, yelp_id: str) -> dict:
        """
        Get detailed information for a specific venue.

        Args:
            yelp_id: Yelp business ID

        Returns:
            Full venue details dict
        """
        if not self.api_key:
            return {}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    self.DETAIL_URL.format(id=yelp_id),
                    headers=self.headers
                )
                return resp.json() if resp.is_success else {}

        except Exception as e:
            print(f"[Yelp] Details error: {e}")
            return {}

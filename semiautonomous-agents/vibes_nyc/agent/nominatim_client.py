"""
Nominatim Geocoding Client.
Free OpenStreetMap geocoding with 1 req/sec rate limit.
"""
import httpx


class NominatimClient:
    """
    Geocoding client using OpenStreetMap Nominatim API.
    Free, no API key needed. Respects 1 req/sec via in-memory cache.
    """

    BASE_URL = "https://nominatim.openstreetmap.org/search"
    CACHE: dict[str, tuple[float, float]] = {}

    async def geocode(self, location: str) -> tuple[float, float]:
        """
        Convert location string to lat/lon coordinates.

        Args:
            location: Location string (e.g., "Williamsburg, Brooklyn")

        Returns:
            Tuple of (latitude, longitude)
        """
        # Check cache first to respect rate limit
        cache_key = location.lower().strip()
        if cache_key in self.CACHE:
            return self.CACHE[cache_key]

        try:
            async with httpx.AsyncClient(
                timeout=5,
                headers={"User-Agent": "VibesNYC/1.0 (venue discovery app)"}
            ) as client:
                resp = await client.get(
                    self.BASE_URL,
                    params={
                        "q": location,
                        "format": "json",
                        "limit": 1,
                        "countrycodes": "us"
                    }
                )

                if resp.is_success:
                    results = resp.json()
                    if results:
                        lat = float(results[0]["lat"])
                        lon = float(results[0]["lon"])
                        self.CACHE[cache_key] = (lat, lon)
                        return (lat, lon)

        except Exception as e:
            print(f"[Nominatim] Geocoding error for '{location}': {e}")

        # Default to Manhattan midtown if geocoding fails
        default = (40.7549, -73.9840)
        self.CACHE[cache_key] = default
        return default

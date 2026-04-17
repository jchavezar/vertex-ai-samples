"""
Google Photos Tools for Google Workspace MCP Server
"""
import logging
import requests

logger = logging.getLogger("gworkspace-mcp.photos")

PHOTOS_API = "https://photoslibrary.googleapis.com/v1"


def register_photos_tools(mcp, auth_manager):
    """Register Google Photos tools with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}"}

    @mcp.tool()
    def photos_search(query: str, max_results: int = 20) -> str:
        """
        Search Google Photos by text query. Google Photos AI recognizes
        objects, places, people, and text in your photos.

        Args:
            query: Search term (e.g., "ducati", "beach", "birthday", "receipt")
            max_results: Maximum photos to return (default 20)
        """
        try:
            body = {
                "pageSize": min(max_results, 100),
                "filters": {
                    "contentFilter": {
                        "includedContentCategories": []
                    }
                }
            }

            # Google Photos API search uses POST
            response = requests.post(
                f"{PHOTOS_API}/mediaItems:search",
                headers={**get_headers(), "Content-Type": "application/json"},
                json=body
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("mediaItems", [])
            if not items:
                return f"No photos found."

            results = []
            results.append(f"## Google Photos ({len(items)} found)\n")

            for item in items[:max_results]:
                filename = item.get("filename", "Unknown")
                mime = item.get("mimeType", "")
                created = item.get("mediaMetadata", {}).get("creationTime", "Unknown")
                width = item.get("mediaMetadata", {}).get("width", "?")
                height = item.get("mediaMetadata", {}).get("height", "?")
                desc = item.get("description", "")
                url = item.get("productUrl", "")

                results.append(
                    f"**{filename}**\n"
                    f"- Date: {created}\n"
                    f"- Size: {width}x{height} | Type: {mime}\n"
                    f"- Description: {desc or 'N/A'}\n"
                    f"- URL: {url}\n"
                )

            return "\n---\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Photos search error: {e}")
            return f"Error searching photos: {str(e)}"

    @mcp.tool()
    def photos_list_recent(max_results: int = 20) -> str:
        """
        List recent photos from Google Photos.

        Args:
            max_results: Maximum photos to return (default 20)
        """
        try:
            response = requests.get(
                f"{PHOTOS_API}/mediaItems",
                headers=get_headers(),
                params={"pageSize": min(max_results, 100)}
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("mediaItems", [])
            if not items:
                return "No photos found."

            results = []
            results.append(f"## Recent Photos ({len(items)} found)\n")

            for item in items[:max_results]:
                filename = item.get("filename", "Unknown")
                mime = item.get("mimeType", "")
                created = item.get("mediaMetadata", {}).get("creationTime", "Unknown")
                width = item.get("mediaMetadata", {}).get("width", "?")
                height = item.get("mediaMetadata", {}).get("height", "?")
                desc = item.get("description", "")
                url = item.get("productUrl", "")

                results.append(
                    f"**{filename}**\n"
                    f"- Date: {created}\n"
                    f"- Size: {width}x{height} | Type: {mime}\n"
                    f"- Description: {desc or 'N/A'}\n"
                    f"- URL: {url}\n"
                )

            return "\n---\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Photos list error: {e}")
            return f"Error listing photos: {str(e)}"

    @mcp.tool()
    def photos_list_albums(max_results: int = 50) -> str:
        """List all Google Photos albums."""
        try:
            response = requests.get(
                f"{PHOTOS_API}/albums",
                headers=get_headers(),
                params={"pageSize": min(max_results, 50)}
            )
            response.raise_for_status()
            data = response.json()

            albums = data.get("albums", [])
            if not albums:
                return "No albums found."

            results = []
            results.append(f"## Google Photos Albums ({len(albums)} found)\n")

            for album in albums:
                title = album.get("title", "Untitled")
                count = album.get("mediaItemsCount", "0")
                album_id = album.get("id", "")
                url = album.get("productUrl", "")

                results.append(
                    f"- **{title}** ({count} items) — ID: `{album_id[:20]}...`\n"
                    f"  URL: {url}"
                )

            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Albums list error: {e}")
            return f"Error listing albums: {str(e)}"

    @mcp.tool()
    def photos_search_by_date(year: int, month: int = 0, day: int = 0, max_results: int = 20) -> str:
        """
        Search Google Photos by date.

        Args:
            year: Year (e.g., 2025)
            month: Month 1-12 (0 for entire year)
            day: Day 1-31 (0 for entire month)
            max_results: Maximum photos to return (default 20)
        """
        try:
            date_filter = {"dates": [{"year": year}]}
            if month > 0:
                date_filter["dates"][0]["month"] = month
            if day > 0:
                date_filter["dates"][0]["day"] = day

            body = {
                "pageSize": min(max_results, 100),
                "filters": {
                    "dateFilter": date_filter
                }
            }

            response = requests.post(
                f"{PHOTOS_API}/mediaItems:search",
                headers={**get_headers(), "Content-Type": "application/json"},
                json=body
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("mediaItems", [])
            if not items:
                date_str = f"{year}"
                if month:
                    date_str += f"-{month:02d}"
                if day:
                    date_str += f"-{day:02d}"
                return f"No photos found for {date_str}."

            results = []
            results.append(f"## Photos ({len(items)} found)\n")

            for item in items[:max_results]:
                filename = item.get("filename", "Unknown")
                created = item.get("mediaMetadata", {}).get("creationTime", "Unknown")
                width = item.get("mediaMetadata", {}).get("width", "?")
                height = item.get("mediaMetadata", {}).get("height", "?")
                url = item.get("productUrl", "")

                results.append(
                    f"**{filename}** — {created}\n"
                    f"- Size: {width}x{height} | URL: {url}\n"
                )

            return "\n---\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Photos date search error: {e}")
            return f"Error searching photos: {str(e)}"

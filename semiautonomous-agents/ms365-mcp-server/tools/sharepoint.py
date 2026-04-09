"""
SharePoint and OneDrive Tools for Microsoft 365 MCP Server
"""
import logging
import base64
from typing import Optional
from graph_client import get_graph_client, GraphAPIError

logger = logging.getLogger("ms365-mcp.tools.sharepoint")


def list_sharepoint_sites(search: str = "") -> str:
    """
    List SharePoint sites you have access to.

    Args:
        search: Optional search term to filter sites by name
    """
    try:
        client = get_graph_client()

        if search:
            # Search for sites matching the term
            result = client.get(f"/sites?search={search}")
        else:
            # Get user's followed/recent sites
            result = client.get("/sites?search=*")

        sites = result.get("value", [])

        if not sites:
            return "No SharePoint sites found. Try a different search term."

        output = "## SharePoint Sites\n\n"
        output += "| Name | URL | ID |\n"
        output += "|------|-----|----|\n"

        for site in sites[:20]:  # Limit to 20 results
            name = site.get("displayName", "Unnamed")
            url = site.get("webUrl", "")
            site_id = site.get("id", "")
            output += f"| {name} | {url} | `{site_id}` |\n"

        if len(sites) > 20:
            output += f"\n*Showing 20 of {len(sites)} sites. Use search to narrow results.*"

        return output

    except GraphAPIError as e:
        return f"Error listing sites: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] List sites failed: {e}")
        return f"Error: {str(e)}"


def list_site_drives(site_id: str) -> str:
    """
    List document libraries (drives) in a SharePoint site.

    Args:
        site_id: The SharePoint site ID (from list_sharepoint_sites)
    """
    try:
        client = get_graph_client()
        result = client.get(f"/sites/{site_id}/drives")

        drives = result.get("value", [])

        if not drives:
            return "No document libraries found in this site."

        output = f"## Document Libraries\n\n"
        output += "| Name | Drive ID | Web URL |\n"
        output += "|------|----------|--------|\n"

        for drive in drives:
            name = drive.get("name", "Unnamed")
            drive_id = drive.get("id", "")
            web_url = drive.get("webUrl", "")
            output += f"| {name} | `{drive_id}` | {web_url} |\n"

        return output

    except GraphAPIError as e:
        return f"Error listing drives: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] List drives failed: {e}")
        return f"Error: {str(e)}"


def list_folder_files(
    drive_id: str,
    folder_path: str = "/",
    limit: int = 50
) -> str:
    """
    List files and folders in a OneDrive or SharePoint drive.

    Args:
        drive_id: The drive ID (from list_site_drives or use 'me' for OneDrive)
        folder_path: Path to folder (e.g., '/Documents/Reports') or '/' for root
        limit: Maximum number of items to return (default 50)
    """
    try:
        client = get_graph_client()

        # Build endpoint based on drive_id
        if drive_id.lower() == "me":
            base = "/me/drive"
        else:
            base = f"/drives/{drive_id}"

        # Build path
        if folder_path == "/" or not folder_path:
            endpoint = f"{base}/root/children"
        else:
            # Normalize path
            path = folder_path.strip("/")
            endpoint = f"{base}/root:/{path}:/children"

        result = client.get(endpoint, params={"$top": limit})
        items = result.get("value", [])

        if not items:
            return f"No files or folders found in: {folder_path}"

        output = f"## Files in `{folder_path}`\n\n"
        output += "| Type | Name | Size | Modified |\n"
        output += "|------|------|------|----------|\n"

        for item in items:
            is_folder = "folder" in item
            type_icon = "[Folder]" if is_folder else "[File]"
            name = item.get("name", "Unnamed")
            size = item.get("size", 0)
            size_str = f"{size / 1024:.1f} KB" if not is_folder else "-"
            modified = item.get("lastModifiedDateTime", "")[:10]
            output += f"| {type_icon} | {name} | {size_str} | {modified} |\n"

        return output

    except GraphAPIError as e:
        return f"Error listing files: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] List files failed: {e}")
        return f"Error: {str(e)}"


def list_onedrive_files(folder_path: str = "/", limit: int = 50) -> str:
    """
    List files and folders in your personal OneDrive.

    Args:
        folder_path: Path to folder (e.g., '/Documents') or '/' for root
        limit: Maximum number of items to return (default 50)
    """
    return list_folder_files(drive_id="me", folder_path=folder_path, limit=limit)


def upload_file(
    drive_id: str,
    folder_path: str,
    file_name: str,
    content: str,
    is_base64: bool = False
) -> str:
    """
    Upload a file to SharePoint or OneDrive.

    Args:
        drive_id: The drive ID or 'me' for OneDrive
        folder_path: Destination folder path (e.g., '/Documents/Reports')
        file_name: Name for the uploaded file
        content: File content (text or base64-encoded binary)
        is_base64: Set to True if content is base64-encoded
    """
    try:
        client = get_graph_client()

        # Build endpoint
        if drive_id.lower() == "me":
            base = "/me/drive"
        else:
            base = f"/drives/{drive_id}"

        # Normalize path
        path = folder_path.strip("/")
        if path:
            endpoint = f"{base}/root:/{path}/{file_name}:/content"
        else:
            endpoint = f"{base}/root:/{file_name}:/content"

        # Decode content if base64
        if is_base64:
            file_bytes = base64.b64decode(content)
        else:
            file_bytes = content.encode("utf-8")

        result = client.put(endpoint, content=file_bytes)

        return f"""## File Uploaded Successfully

**Name:** {result.get('name', file_name)}
**Path:** {folder_path}/{file_name}
**Size:** {result.get('size', len(file_bytes))} bytes
**Web URL:** {result.get('webUrl', 'N/A')}"""

    except GraphAPIError as e:
        return f"Error uploading file: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] Upload failed: {e}")
        return f"Error: {str(e)}"


def download_file(drive_id: str, file_path: str) -> str:
    """
    Download a file from SharePoint or OneDrive.

    Args:
        drive_id: The drive ID or 'me' for OneDrive
        file_path: Path to the file (e.g., '/Documents/report.txt')

    Returns:
        File content as text (for text files) or base64-encoded string (for binary)
    """
    try:
        client = get_graph_client()

        # Build endpoint
        if drive_id.lower() == "me":
            base = "/me/drive"
        else:
            base = f"/drives/{drive_id}"

        path = file_path.strip("/")
        endpoint = f"{base}/root:/{path}:/content"

        # Get download URL
        import httpx
        from auth import get_auth_manager

        token = get_auth_manager().get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        with httpx.Client(follow_redirects=True) as http_client:
            response = http_client.get(
                f"https://graph.microsoft.com/v1.0{endpoint}",
                headers=headers
            )
            response.raise_for_status()

            # Detect binary content and use base64 for non-text files
            content_type = response.headers.get("content-type", "")
            ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
            binary_types = {"pdf", "docx", "xlsx", "pptx", "zip", "png", "jpg", "jpeg", "gif"}
            is_binary = ext in binary_types or "octet-stream" in content_type or "application/pdf" in content_type

            if is_binary:
                content_b64 = base64.b64encode(response.content).decode("utf-8")
                return f"## File Content (Base64)\n\n```\n{content_b64}\n```"
            else:
                content = response.text
                return f"## File Content\n\n```\n{content}\n```"

    except GraphAPIError as e:
        return f"Error downloading file: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] Download failed: {e}")
        return f"Error: {str(e)}"


def create_folder(drive_id: str, parent_path: str, folder_name: str) -> str:
    """
    Create a new folder in SharePoint or OneDrive.

    Args:
        drive_id: The drive ID or 'me' for OneDrive
        parent_path: Parent folder path (e.g., '/Documents') or '/' for root
        folder_name: Name for the new folder
    """
    try:
        client = get_graph_client()

        # Build endpoint
        if drive_id.lower() == "me":
            base = "/me/drive"
        else:
            base = f"/drives/{drive_id}"

        # Normalize path
        path = parent_path.strip("/")
        if path:
            endpoint = f"{base}/root:/{path}:/children"
        else:
            endpoint = f"{base}/root/children"

        result = client.post(endpoint, json_data={
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail"
        })

        return f"""## Folder Created

**Name:** {result.get('name', folder_name)}
**Path:** {parent_path}/{folder_name}
**Web URL:** {result.get('webUrl', 'N/A')}"""

    except GraphAPIError as e:
        if "nameAlreadyExists" in str(e):
            return f"Folder '{folder_name}' already exists at {parent_path}"
        return f"Error creating folder: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] Create folder failed: {e}")
        return f"Error: {str(e)}"


def search_files(query: str, drive_id: Optional[str] = None, limit: int = 25) -> str:
    """
    Search for files across SharePoint and OneDrive.

    Args:
        query: Search query (file name, content, etc.) - cannot be empty or wildcard
        drive_id: Optional drive ID to limit search scope, or 'me' for OneDrive only
        limit: Maximum number of results (default 25)
    """
    try:
        # Validate query - Graph API doesn't support empty or wildcard searches
        if not query or query.strip() in ("*", "**", ""):
            return "Error: Please provide a specific search term. Wildcards (*) are not supported. Use 'onedrive_list_files' or 'sp_list_files' to browse all files."

        client = get_graph_client()

        if drive_id:
            if drive_id.lower() == "me":
                endpoint = f"/me/drive/root/search(q='{query}')"
            else:
                endpoint = f"/drives/{drive_id}/root/search(q='{query}')"
        else:
            # Search across all accessible drives
            endpoint = f"/me/drive/root/search(q='{query}')"

        result = client.get(endpoint, params={"$top": limit})
        items = result.get("value", [])

        if not items:
            return f"No files found matching: '{query}'"

        output = f"## Search Results for '{query}'\n\n"
        output += "| Name | Path | Size | Modified |\n"
        output += "|------|------|------|----------|\n"

        for item in items:
            name = item.get("name", "Unnamed")
            parent_path = item.get("parentReference", {}).get("path", "")
            # Clean up path
            if "/root:" in parent_path:
                parent_path = parent_path.split("/root:")[-1] or "/"
            size = item.get("size", 0)
            size_str = f"{size / 1024:.1f} KB"
            modified = item.get("lastModifiedDateTime", "")[:10]
            output += f"| {name} | {parent_path} | {size_str} | {modified} |\n"

        return output

    except GraphAPIError as e:
        return f"Error searching files: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] Search failed: {e}")
        return f"Error: {str(e)}"


def search_content(query: str, limit: int = 10) -> str:
    """
    Search within document content across SharePoint and OneDrive.
    Uses Microsoft Graph Search API to find text inside documents.

    Args:
        query: Search query to find within document content
        limit: Maximum number of results (default 10)
    """
    try:
        if not query or query.strip() == "":
            return "Error: Please provide a search term."

        client = get_graph_client()

        # Use the Search API to search within document content
        search_request = {
            "requests": [
                {
                    "entityTypes": ["driveItem"],
                    "query": {
                        "queryString": query
                    },
                    "from": 0,
                    "size": limit,
                    "fields": [
                        "name",
                        "webUrl",
                        "lastModifiedDateTime",
                        "createdBy",
                        "size"
                    ]
                }
            ]
        }

        result = client.post("/search/query", json_data=search_request)

        hits = []
        for response in result.get("value", []):
            for hit_container in response.get("hitsContainers", []):
                hits.extend(hit_container.get("hits", []))

        if not hits:
            return f"No content found matching: '{query}'"

        output = f"## Content Search Results for '{query}'\n\n"
        output += f"*Found {len(hits)} document(s) containing this text*\n\n"

        for i, hit in enumerate(hits, 1):
            resource = hit.get("resource", {})
            name = resource.get("name", "Unknown")
            web_url = resource.get("webUrl", "")
            modified = resource.get("lastModifiedDateTime", "")[:10] if resource.get("lastModifiedDateTime") else "N/A"

            # Get summary/snippet if available
            summary = hit.get("summary", "")

            output += f"### {i}. {name}\n"
            output += f"- **URL**: {web_url}\n"
            output += f"- **Modified**: {modified}\n"
            if summary:
                output += f"- **Snippet**: {summary}\n"
            output += "\n"

        return output

    except GraphAPIError as e:
        return f"Error searching content: {e}"
    except Exception as e:
        logger.error(f"[SharePoint] Content search failed: {e}")
        return f"Error: {str(e)}"

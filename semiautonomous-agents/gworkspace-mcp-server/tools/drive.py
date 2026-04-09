"""
Google Drive Tools for Google Workspace MCP Server
"""
import logging
import base64
from typing import Optional
import requests

logger = logging.getLogger("gworkspace-mcp.drive")

DRIVE_API = "https://www.googleapis.com/drive/v3"


def register_drive_tools(mcp, auth_manager):
    """Register Google Drive tools with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}"}

    @mcp.tool()
    def drive_list_files(
        max_results: int = 20,
        query: str = "",
        folder_id: str = "",
        order_by: str = "modifiedTime desc"
    ) -> str:
        """
        List files in Google Drive.

        Args:
            max_results: Maximum files to return (default 20, max 100)
            query: Drive search query (e.g., "name contains 'report'")
            folder_id: List files in specific folder (optional)
            order_by: Sort order (default "modifiedTime desc")
        """
        try:
            params = {
                "pageSize": min(max_results, 100),
                "fields": "files(id,name,mimeType,size,modifiedTime,webViewLink,parents)",
                "orderBy": order_by,
            }

            q_parts = []
            if query:
                q_parts.append(query)
            if folder_id:
                q_parts.append(f"'{folder_id}' in parents")
            q_parts.append("trashed = false")

            params["q"] = " and ".join(q_parts)

            response = requests.get(
                f"{DRIVE_API}/files",
                headers=get_headers(),
                params=params
            )
            response.raise_for_status()
            data = response.json()

            files = data.get("files", [])
            if not files:
                return "No files found."

            results = []
            for f in files:
                size = f.get("size", "N/A")
                if size != "N/A":
                    size = f"{int(size) / 1024:.1f} KB"

                mime = f.get("mimeType", "")
                file_type = "Folder" if "folder" in mime else mime.split("/")[-1] if "/" in mime else mime

                results.append(
                    f"**{f['name']}**\n"
                    f"  - ID: `{f['id']}`\n"
                    f"  - Type: {file_type}\n"
                    f"  - Size: {size}\n"
                    f"  - Modified: {f.get('modifiedTime', 'Unknown')}\n"
                    f"  - [Open]({f.get('webViewLink', '#')})"
                )

            return f"## Google Drive Files ({len(results)} found)\n\n" + "\n\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive list error: {e}")
            return f"Error listing files: {str(e)}"

    @mcp.tool()
    def drive_search(query: str, max_results: int = 20) -> str:
        """
        Search for files in Google Drive.

        Args:
            query: Search query (searches file names and content)
            max_results: Maximum results (default 20)
        """
        search_query = f"fullText contains '{query}' or name contains '{query}'"
        return drive_list_files(max_results=max_results, query=search_query)

    @mcp.tool()
    def drive_get_file(file_id: str) -> str:
        """
        Get metadata for a specific file.

        Args:
            file_id: The file ID to retrieve
        """
        try:
            response = requests.get(
                f"{DRIVE_API}/files/{file_id}",
                headers=get_headers(),
                params={
                    "fields": "id,name,mimeType,size,createdTime,modifiedTime,webViewLink,webContentLink,owners,shared,permissions"
                }
            )
            response.raise_for_status()
            f = response.json()

            size = f.get("size", "N/A")
            if size != "N/A":
                size = f"{int(size) / 1024:.1f} KB"

            owners = ", ".join([o.get("emailAddress", "Unknown") for o in f.get("owners", [])])

            return f"""## File Details

**Name:** {f.get('name')}
**ID:** `{f.get('id')}`
**Type:** {f.get('mimeType')}
**Size:** {size}
**Created:** {f.get('createdTime', 'Unknown')}
**Modified:** {f.get('modifiedTime', 'Unknown')}
**Owner(s):** {owners}
**Shared:** {f.get('shared', False)}
**View Link:** {f.get('webViewLink', 'N/A')}
**Download Link:** {f.get('webContentLink', 'N/A')}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive get error: {e}")
            return f"Error getting file: {str(e)}"

    @mcp.tool()
    def drive_download_file(file_id: str) -> str:
        """
        Download content of a Google Drive file (text-based files only).

        Args:
            file_id: The file ID to download
        """
        try:
            # First get file metadata
            meta_response = requests.get(
                f"{DRIVE_API}/files/{file_id}",
                headers=get_headers(),
                params={"fields": "name,mimeType,size"}
            )
            meta_response.raise_for_status()
            meta = meta_response.json()

            mime_type = meta.get("mimeType", "")

            # Handle Google Workspace files (export as text)
            export_types = {
                "application/vnd.google-apps.document": "text/plain",
                "application/vnd.google-apps.spreadsheet": "text/csv",
                "application/vnd.google-apps.presentation": "text/plain",
            }

            if mime_type in export_types:
                response = requests.get(
                    f"{DRIVE_API}/files/{file_id}/export",
                    headers=get_headers(),
                    params={"mimeType": export_types[mime_type]}
                )
            else:
                response = requests.get(
                    f"{DRIVE_API}/files/{file_id}",
                    headers=get_headers(),
                    params={"alt": "media"}
                )

            response.raise_for_status()

            # Limit content size
            content = response.text[:50000]
            if len(response.text) > 50000:
                content += "\n\n... (content truncated)"

            return f"""## File Content: {meta.get('name')}

{content}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive download error: {e}")
            return f"Error downloading file: {str(e)}"

    @mcp.tool()
    def drive_create_folder(
        name: str,
        parent_id: str = ""
    ) -> str:
        """
        Create a new folder in Google Drive.

        Args:
            name: Folder name
            parent_id: Parent folder ID (optional, defaults to root)
        """
        try:
            metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if parent_id:
                metadata["parents"] = [parent_id]

            response = requests.post(
                f"{DRIVE_API}/files",
                headers={**get_headers(), "Content-Type": "application/json"},
                json=metadata
            )
            response.raise_for_status()
            data = response.json()

            return f"Folder created successfully!\n\n**Name:** {data.get('name')}\n**ID:** `{data.get('id')}`"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive create folder error: {e}")
            return f"Error creating folder: {str(e)}"

    @mcp.tool()
    def drive_upload_file(
        name: str,
        content: str,
        mime_type: str = "text/plain",
        parent_id: str = ""
    ) -> str:
        """
        Upload a text file to Google Drive.

        Args:
            name: File name
            content: File content (text)
            mime_type: MIME type (default "text/plain")
            parent_id: Parent folder ID (optional)
        """
        try:
            metadata = {"name": name}
            if parent_id:
                metadata["parents"] = [parent_id]

            # Use multipart upload
            boundary = "===boundary==="
            body = (
                f"--{boundary}\r\n"
                f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                f'{{"name": "{name}"' + (f', "parents": ["{parent_id}"]' if parent_id else '') + '}\r\n'
                f"--{boundary}\r\n"
                f"Content-Type: {mime_type}\r\n\r\n"
                f"{content}\r\n"
                f"--{boundary}--"
            )

            response = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                headers={
                    **get_headers(),
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                data=body.encode("utf-8")
            )
            response.raise_for_status()
            data = response.json()

            return f"File uploaded successfully!\n\n**Name:** {data.get('name')}\n**ID:** `{data.get('id')}`"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive upload error: {e}")
            return f"Error uploading file: {str(e)}"

    @mcp.tool()
    def drive_upload_binary(
        name: str,
        content_base64: str = "",
        file_path: str = "",
        gcs_uri: str = "",
        mime_type: str = "application/octet-stream",
        parent_id: str = ""
    ) -> str:
        """
        Upload a binary file to Google Drive.

        Args:
            name: File name (e.g., "image.png")
            content_base64: Base64-encoded file content (option 1)
            file_path: Local file path to read from (option 2)
            gcs_uri: GCS URI to download from, e.g. gs://bucket/path (option 3)
            mime_type: MIME type (e.g., "image/png", "application/pdf")
            parent_id: Parent folder ID (optional)
        """
        try:
            # Get binary content from one of the sources
            if file_path:
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
            elif gcs_uri:
                # Download from GCS using google-cloud-storage
                from google.cloud import storage
                # Parse gs://bucket/path
                if not gcs_uri.startswith('gs://'):
                    return "Error: gcs_uri must start with gs://"
                parts = gcs_uri[5:].split('/', 1)
                if len(parts) != 2:
                    return "Error: gcs_uri must be gs://bucket/path"
                bucket_name, blob_path = parts
                client = storage.Client()
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(blob_path)
                binary_content = blob.download_as_bytes()
            elif content_base64:
                binary_content = base64.b64decode(content_base64)
            else:
                return "Error: Must provide content_base64, file_path, or gcs_uri"

            import json
            metadata = {"name": name}
            if parent_id:
                metadata["parents"] = [parent_id]

            # Use multipart upload with binary content
            boundary = "===boundary_binary==="

            # Build multipart body
            body_parts = []
            body_parts.append(f"--{boundary}".encode())
            body_parts.append(b"Content-Type: application/json; charset=UTF-8")
            body_parts.append(b"")
            body_parts.append(json.dumps(metadata).encode())
            body_parts.append(f"--{boundary}".encode())
            body_parts.append(f"Content-Type: {mime_type}".encode())
            body_parts.append(b"Content-Transfer-Encoding: binary")
            body_parts.append(b"")
            body_parts.append(binary_content)
            body_parts.append(f"--{boundary}--".encode())

            body = b"\r\n".join(body_parts)

            response = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                headers={
                    **get_headers(),
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                data=body
            )
            response.raise_for_status()
            data = response.json()

            return f"Binary file uploaded successfully!\n\n**Name:** {data.get('name')}\n**ID:** `{data.get('id')}`\n**View:** https://drive.google.com/file/d/{data.get('id')}/view"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive binary upload error: {e}")
            return f"Error uploading binary file: {str(e)}"

    @mcp.tool()
    def drive_delete_file(file_id: str) -> str:
        """
        Delete a file from Google Drive (moves to trash).

        Args:
            file_id: The file ID to delete
        """
        try:
            # Move to trash instead of permanent delete
            response = requests.patch(
                f"{DRIVE_API}/files/{file_id}",
                headers={**get_headers(), "Content-Type": "application/json"},
                json={"trashed": True}
            )
            response.raise_for_status()

            return f"File moved to trash successfully (ID: {file_id})"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Drive delete error: {e}")
            return f"Error deleting file: {str(e)}"

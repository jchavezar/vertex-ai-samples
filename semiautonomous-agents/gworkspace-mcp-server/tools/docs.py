"""
Google Docs Tools for Google Workspace MCP Server
"""
import logging
from typing import Optional
import requests

logger = logging.getLogger("gworkspace-mcp.docs")

DOCS_API = "https://docs.googleapis.com/v1"
DRIVE_API = "https://www.googleapis.com/drive/v3"


def register_docs_tools(mcp, auth_manager):
    """Register Google Docs tools with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}"}

    @mcp.tool()
    def docs_list() -> str:
        """List Google Docs in Drive."""
        try:
            response = requests.get(
                f"{DRIVE_API}/files",
                headers=get_headers(),
                params={
                    "q": "mimeType='application/vnd.google-apps.document' and trashed=false",
                    "pageSize": 20,
                    "fields": "files(id,name,modifiedTime,webViewLink)",
                    "orderBy": "modifiedTime desc"
                }
            )
            response.raise_for_status()
            data = response.json()

            files = data.get("files", [])
            if not files:
                return "No Google Docs found."

            results = []
            for f in files:
                results.append(
                    f"**{f['name']}**\n"
                    f"  - ID: `{f['id']}`\n"
                    f"  - Modified: {f.get('modifiedTime', 'Unknown')}\n"
                    f"  - [Open]({f.get('webViewLink', '#')})"
                )

            return f"## Google Docs ({len(results)} found)\n\n" + "\n\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Docs list error: {e}")
            return f"Error listing docs: {str(e)}"

    @mcp.tool()
    def docs_get(document_id: str) -> str:
        """
        Get content of a Google Doc.

        Args:
            document_id: The document ID
        """
        try:
            response = requests.get(
                f"{DOCS_API}/documents/{document_id}",
                headers=get_headers()
            )
            response.raise_for_status()
            doc = response.json()

            # Extract text content
            content = []
            for element in doc.get("body", {}).get("content", []):
                if "paragraph" in element:
                    para_text = ""
                    for elem in element["paragraph"].get("elements", []):
                        if "textRun" in elem:
                            para_text += elem["textRun"].get("content", "")
                    if para_text.strip():
                        content.append(para_text)

            text_content = "".join(content)

            # Truncate if too long
            if len(text_content) > 50000:
                text_content = text_content[:50000] + "\n\n... (content truncated)"

            return f"""## Document: {doc.get('title', 'Untitled')}

**ID:** `{doc.get('documentId')}`

---

{text_content}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Docs get error: {e}")
            return f"Error getting document: {str(e)}"

    @mcp.tool()
    def docs_create(
        title: str,
        content: str = ""
    ) -> str:
        """
        Create a new Google Doc.

        Args:
            title: Document title
            content: Initial content (optional)
        """
        try:
            # Create empty document
            response = requests.post(
                f"{DOCS_API}/documents",
                headers={**get_headers(), "Content-Type": "application/json"},
                json={"title": title}
            )
            response.raise_for_status()
            doc = response.json()
            doc_id = doc.get("documentId")

            # Add content if provided
            if content:
                requests_body = {
                    "requests": [
                        {
                            "insertText": {
                                "location": {"index": 1},
                                "text": content
                            }
                        }
                    ]
                }

                update_response = requests.post(
                    f"{DOCS_API}/documents/{doc_id}:batchUpdate",
                    headers={**get_headers(), "Content-Type": "application/json"},
                    json=requests_body
                )
                update_response.raise_for_status()

            # Get document link
            drive_response = requests.get(
                f"{DRIVE_API}/files/{doc_id}",
                headers=get_headers(),
                params={"fields": "webViewLink"}
            )
            web_link = drive_response.json().get("webViewLink", "N/A") if drive_response.ok else "N/A"

            return f"""Document created successfully!

**Title:** {title}
**ID:** `{doc_id}`
**Link:** {web_link}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Docs create error: {e}")
            return f"Error creating document: {str(e)}"

    @mcp.tool()
    def docs_append(
        document_id: str,
        text: str
    ) -> str:
        """
        Append text to the end of a Google Doc.

        Args:
            document_id: The document ID
            text: Text to append
        """
        try:
            # First get document to find end index
            doc_response = requests.get(
                f"{DOCS_API}/documents/{document_id}",
                headers=get_headers()
            )
            doc_response.raise_for_status()
            doc = doc_response.json()

            # Find the end index
            end_index = 1
            for element in doc.get("body", {}).get("content", []):
                if "endIndex" in element:
                    end_index = element["endIndex"]

            # Insert at end (before the final newline)
            insert_index = max(1, end_index - 1)

            requests_body = {
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": insert_index},
                            "text": "\n" + text
                        }
                    }
                ]
            }

            response = requests.post(
                f"{DOCS_API}/documents/{document_id}:batchUpdate",
                headers={**get_headers(), "Content-Type": "application/json"},
                json=requests_body
            )
            response.raise_for_status()

            return f"Text appended successfully to document {document_id}"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Docs append error: {e}")
            return f"Error appending to document: {str(e)}"

    @mcp.tool()
    def docs_search(query: str) -> str:
        """
        Search for Google Docs by name.

        Args:
            query: Search query
        """
        try:
            response = requests.get(
                f"{DRIVE_API}/files",
                headers=get_headers(),
                params={
                    "q": f"mimeType='application/vnd.google-apps.document' and name contains '{query}' and trashed=false",
                    "pageSize": 20,
                    "fields": "files(id,name,modifiedTime,webViewLink)",
                    "orderBy": "modifiedTime desc"
                }
            )
            response.raise_for_status()
            data = response.json()

            files = data.get("files", [])
            if not files:
                return f"No Google Docs found matching '{query}'."

            results = []
            for f in files:
                results.append(
                    f"**{f['name']}**\n"
                    f"  - ID: `{f['id']}`\n"
                    f"  - Modified: {f.get('modifiedTime', 'Unknown')}\n"
                    f"  - [Open]({f.get('webViewLink', '#')})"
                )

            return f"## Search Results for '{query}' ({len(results)} found)\n\n" + "\n\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Docs search error: {e}")
            return f"Error searching docs: {str(e)}"

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

            # Extract text content recursively (handling paragraphs, tables, etc.)
            def extract_text(element) -> str:
                text = ""
                if "paragraph" in element:
                    for elem in element["paragraph"].get("elements", []):
                        if "textRun" in elem:
                            text += elem["textRun"].get("content", "")
                elif "table" in element:
                    for row in element["table"].get("tableRows", []):
                        for cell in row.get("tableCells", []):
                            for cell_element in cell.get("content", []):
                                text += extract_text(cell_element)
                elif "tableOfContents" in element:
                    for toc_element in element["tableOfContents"].get("content", []):
                        text += extract_text(toc_element)
                return text

            content = []
            for element in doc.get("body", {}).get("content", []):
                text = extract_text(element)
                if text.strip():
                    content.append(text)

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
        content: str = "",
        parent_id: str = "",
        is_html: bool = False
    ) -> str:
        """
        Create a new Google Doc (supports direct Drive folder placement and HTML/text conversion).

        Args:
            title: Document title
            content: Initial content (text or HTML)
            parent_id: Optional Google Drive folder ID to place the document in
            is_html: Set True if content is HTML for rich formatting (headings, tables, bold)
        """
        try:
            import json
            metadata = {
                "name": title,
                "mimeType": "application/vnd.google-apps.document"
            }
            if parent_id:
                metadata["parents"] = [parent_id]

            content_type = "text/html" if is_html else "text/plain"
            boundary = "===gdoc_create_boundary==="
            body = (
                f"--{boundary}\r\n"
                f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                f"{json.dumps(metadata)}\r\n"
                f"--{boundary}\r\n"
                f"Content-Type: {content_type}; charset=UTF-8\r\n\r\n"
                f"{content}\r\n"
                f"--{boundary}--"
            )

            response = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink",
                headers={
                    **get_headers(),
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                data=body.encode("utf-8")
            )
            response.raise_for_status()
            doc = response.json()
            doc_id = doc.get("id")
            web_link = doc.get("webViewLink", f"https://docs.google.com/document/d/{doc_id}/edit")

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
            # Export existing text via Drive API
            exp_response = requests.get(
                f"{DRIVE_API}/files/{document_id}/export",
                headers=get_headers(),
                params={"mimeType": "text/plain"}
            )
            exp_response.raise_for_status()
            existing_text = exp_response.text
            updated_text = existing_text.rstrip() + "\n\n" + text

            boundary = "===gdoc_append_boundary==="
            body = (
                f"--{boundary}\r\n"
                f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                f"{{}}\r\n"
                f"--{boundary}\r\n"
                f"Content-Type: text/plain; charset=UTF-8\r\n\r\n"
                f"{updated_text}\r\n"
                f"--{boundary}--"
            )

            response = requests.patch(
                f"https://www.googleapis.com/upload/drive/v3/files/{document_id}?uploadType=multipart",
                headers={
                    **get_headers(),
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                data=body.encode("utf-8")
            )
            response.raise_for_status()

            return f"Text appended successfully to document {document_id}"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Docs append error: {e}")
            return f"Error appending to document: {str(e)}"

    @mcp.tool()
    def docs_replace_text(
        document_id: str,
        find_text: str,
        replace_text: str
    ) -> str:
        """
        Replace occurrences of text in a Google Doc.

        Args:
            document_id: The document ID
            find_text: Exact text to find
            replace_text: Replacement text
        """
        try:
            exp_response = requests.get(
                f"{DRIVE_API}/files/{document_id}/export",
                headers=get_headers(),
                params={"mimeType": "text/plain"}
            )
            exp_response.raise_for_status()
            existing_text = exp_response.text
            if find_text not in existing_text:
                return f"Text '{find_text}' not found in document {document_id}."

            updated_text = existing_text.replace(find_text, replace_text)
            boundary = "===gdoc_replace_boundary==="
            body = (
                f"--{boundary}\r\n"
                f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                f"{{}}\r\n"
                f"--{boundary}\r\n"
                f"Content-Type: text/plain; charset=UTF-8\r\n\r\n"
                f"{updated_text}\r\n"
                f"--{boundary}--"
            )
            response = requests.patch(
                f"https://www.googleapis.com/upload/drive/v3/files/{document_id}?uploadType=multipart",
                headers={
                    **get_headers(),
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                data=body.encode("utf-8")
            )
            response.raise_for_status()
            return f"Successfully replaced '{find_text}' with '{replace_text}' in document {document_id}"
        except Exception as e:
            logger.error(f"Docs replace error: {e}")
            return f"Error replacing text: {str(e)}"

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

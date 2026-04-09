"""
Gmail Tools for Google Workspace MCP Server
"""
import base64
import logging
from email.mime.text import MIMEText
from typing import Optional, List
import requests

logger = logging.getLogger("gworkspace-mcp.gmail")

GMAIL_API = "https://gmail.googleapis.com/gmail/v1"


def register_gmail_tools(mcp, auth_manager):
    """Register Gmail tools with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}"}

    @mcp.tool()
    def gmail_list_messages(
        max_results: int = 10,
        query: str = "",
        label_ids: str = "INBOX"
    ) -> str:
        """
        List Gmail messages.

        Args:
            max_results: Maximum number of messages to return (default 10, max 100)
            query: Gmail search query (e.g., "from:someone@example.com", "is:unread")
            label_ids: Comma-separated label IDs (default "INBOX")
        """
        try:
            params = {
                "maxResults": min(max_results, 100),
            }
            if query:
                params["q"] = query
            if label_ids:
                params["labelIds"] = label_ids.split(",")

            response = requests.get(
                f"{GMAIL_API}/users/me/messages",
                headers=get_headers(),
                params=params
            )
            response.raise_for_status()
            data = response.json()

            messages = data.get("messages", [])
            if not messages:
                return "No messages found."

            # Get details for each message
            results = []
            for msg in messages[:max_results]:
                msg_response = requests.get(
                    f"{GMAIL_API}/users/me/messages/{msg['id']}",
                    headers=get_headers(),
                    params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]}
                )
                if msg_response.ok:
                    msg_data = msg_response.json()
                    headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
                    snippet = msg_data.get("snippet", "")[:100]
                    results.append(
                        f"**ID:** {msg['id']}\n"
                        f"**From:** {headers.get('From', 'Unknown')}\n"
                        f"**Subject:** {headers.get('Subject', '(no subject)')}\n"
                        f"**Date:** {headers.get('Date', 'Unknown')}\n"
                        f"**Preview:** {snippet}...\n"
                    )

            return f"## Gmail Messages ({len(results)} found)\n\n" + "\n---\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Gmail list error: {e}")
            return f"Error listing messages: {str(e)}"

    @mcp.tool()
    def gmail_get_message(message_id: str) -> str:
        """
        Get full content of a Gmail message.

        Args:
            message_id: The message ID to retrieve
        """
        try:
            response = requests.get(
                f"{GMAIL_API}/users/me/messages/{message_id}",
                headers=get_headers(),
                params={"format": "full"}
            )
            response.raise_for_status()
            data = response.json()

            headers = {h["name"]: h["value"] for h in data.get("payload", {}).get("headers", [])}

            # Extract body
            body = ""
            payload = data.get("payload", {})
            if "body" in payload and payload["body"].get("data"):
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
            elif "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        break

            return f"""## Email Details

**From:** {headers.get('From', 'Unknown')}
**To:** {headers.get('To', 'Unknown')}
**Subject:** {headers.get('Subject', '(no subject)')}
**Date:** {headers.get('Date', 'Unknown')}

---

{body or data.get('snippet', 'No body content')}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Gmail get error: {e}")
            return f"Error getting message: {str(e)}"

    @mcp.tool()
    def gmail_send_message(
        to: str,
        subject: str,
        body: str,
        cc: str = "",
        bcc: str = ""
    ) -> str:
        """
        Send an email via Gmail.

        Args:
            to: Recipient email address(es), comma-separated
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (optional, comma-separated)
            bcc: BCC recipients (optional, comma-separated)
        """
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            response = requests.post(
                f"{GMAIL_API}/users/me/messages/send",
                headers=get_headers(),
                json={"raw": raw}
            )
            response.raise_for_status()
            data = response.json()

            return f"Email sent successfully! Message ID: {data.get('id')}"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Gmail send error: {e}")
            return f"Error sending email: {str(e)}"

    @mcp.tool()
    def gmail_search(query: str, max_results: int = 20) -> str:
        """
        Search Gmail messages.

        Args:
            query: Gmail search query (supports Gmail search operators)
            max_results: Maximum results to return (default 20)
        """
        return gmail_list_messages(max_results=max_results, query=query, label_ids="")

    @mcp.tool()
    def gmail_list_labels() -> str:
        """List all Gmail labels."""
        try:
            response = requests.get(
                f"{GMAIL_API}/users/me/labels",
                headers=get_headers()
            )
            response.raise_for_status()
            data = response.json()

            labels = data.get("labels", [])
            system_labels = [l for l in labels if l.get("type") == "system"]
            user_labels = [l for l in labels if l.get("type") == "user"]

            result = "## Gmail Labels\n\n### System Labels\n"
            for label in system_labels:
                result += f"- {label['name']} (ID: {label['id']})\n"

            result += "\n### User Labels\n"
            for label in user_labels:
                result += f"- {label['name']} (ID: {label['id']})\n"

            return result

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Gmail labels error: {e}")
            return f"Error listing labels: {str(e)}"

    @mcp.tool()
    def gmail_modify_labels(
        message_id: str,
        add_labels: str = "",
        remove_labels: str = ""
    ) -> str:
        """
        Modify labels on a Gmail message.

        Args:
            message_id: The message ID to modify
            add_labels: Comma-separated label IDs to add
            remove_labels: Comma-separated label IDs to remove
        """
        try:
            body = {}
            if add_labels:
                body["addLabelIds"] = [l.strip() for l in add_labels.split(",")]
            if remove_labels:
                body["removeLabelIds"] = [l.strip() for l in remove_labels.split(",")]

            if not body:
                return "Error: Must specify add_labels or remove_labels"

            response = requests.post(
                f"{GMAIL_API}/users/me/messages/{message_id}/modify",
                headers=get_headers(),
                json=body
            )
            response.raise_for_status()

            return f"Labels modified successfully on message {message_id}"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Gmail modify error: {e}")
            return f"Error modifying labels: {str(e)}"

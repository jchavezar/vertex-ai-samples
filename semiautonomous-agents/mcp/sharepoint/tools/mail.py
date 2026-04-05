"""
Outlook Mail Tools for Microsoft 365 MCP Server
"""
import logging
from typing import Optional, List
from graph_client import get_graph_client, GraphAPIError

logger = logging.getLogger("ms365-mcp.tools.mail")


def list_mail_messages(
    folder: str = "inbox",
    limit: int = 25,
    unread_only: bool = False
) -> str:
    """
    List emails from your mailbox.

    Args:
        folder: Mail folder ('inbox', 'sentitems', 'drafts', 'deleteditems') or folder ID
        limit: Maximum number of emails to return (default 25)
        unread_only: If True, only show unread emails
    """
    try:
        client = get_graph_client()

        # Map common folder names
        folder_map = {
            "inbox": "inbox",
            "sent": "sentitems",
            "sentitems": "sentitems",
            "drafts": "drafts",
            "deleted": "deleteditems",
            "deleteditems": "deleteditems",
            "junk": "junkemail",
        }
        folder_id = folder_map.get(folder.lower(), folder)

        endpoint = f"/me/mailFolders/{folder_id}/messages"
        params = {
            "$top": limit,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview"
        }

        if unread_only:
            params["$filter"] = "isRead eq false"

        result = client.get(endpoint, params=params)
        messages = result.get("value", [])

        if not messages:
            return f"No emails found in {folder}."

        output = f"## Emails in {folder.title()}\n\n"

        for msg in messages:
            is_read = "[Read]" if msg.get("isRead") else "[Unread]"
            subject = msg.get("subject", "(No Subject)")[:60]
            from_addr = msg.get("from", {}).get("emailAddress", {})
            from_name = from_addr.get("name", from_addr.get("address", "Unknown"))
            received = msg.get("receivedDateTime", "")[:16].replace("T", " ")
            msg_id = msg.get("id", "")[:20]
            preview = msg.get("bodyPreview", "")[:100].replace("\n", " ")

            output += f"### {is_read} {subject}\n"
            output += f"**From:** {from_name}  \n"
            output += f"**Date:** {received}  \n"
            output += f"**ID:** `{msg_id}...`\n\n"
            output += f"> {preview}...\n\n---\n\n"

        return output

    except GraphAPIError as e:
        return f"Error listing emails: {e}"
    except Exception as e:
        logger.error(f"[Mail] List messages failed: {e}")
        return f"Error: {str(e)}"


def get_mail_message(message_id: str) -> str:
    """
    Get full details of a specific email.

    Args:
        message_id: The message ID (from list_mail_messages)
    """
    try:
        client = get_graph_client()

        result = client.get(f"/me/messages/{message_id}")

        subject = result.get("subject", "(No Subject)")
        from_addr = result.get("from", {}).get("emailAddress", {})
        from_email = f"{from_addr.get('name', '')} <{from_addr.get('address', '')}>"

        to_list = result.get("toRecipients", [])
        to_emails = ", ".join([
            r.get("emailAddress", {}).get("address", "")
            for r in to_list
        ])

        cc_list = result.get("ccRecipients", [])
        cc_emails = ", ".join([
            r.get("emailAddress", {}).get("address", "")
            for r in cc_list
        ]) if cc_list else "None"

        received = result.get("receivedDateTime", "")[:19].replace("T", " ")
        body = result.get("body", {})
        body_content = body.get("content", "")

        # Strip HTML if needed
        if body.get("contentType") == "html":
            # Basic HTML stripping
            import re
            body_content = re.sub(r'<[^>]+>', '', body_content)
            body_content = body_content[:2000]  # Limit length

        output = f"""## {subject}

**From:** {from_email}
**To:** {to_emails}
**CC:** {cc_emails}
**Date:** {received}

---

{body_content}
"""
        return output

    except GraphAPIError as e:
        return f"Error getting email: {e}"
    except Exception as e:
        logger.error(f"[Mail] Get message failed: {e}")
        return f"Error: {str(e)}"


def send_mail(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    is_html: bool = False
) -> str:
    """
    Send an email.

    Args:
        to: Recipient email address(es), comma-separated for multiple
        subject: Email subject
        body: Email body content
        cc: Optional CC recipients, comma-separated
        is_html: If True, body is treated as HTML content
    """
    try:
        client = get_graph_client()

        # Build recipient list
        to_recipients = [
            {"emailAddress": {"address": addr.strip()}}
            for addr in to.split(",")
        ]

        cc_recipients = []
        if cc:
            cc_recipients = [
                {"emailAddress": {"address": addr.strip()}}
                for addr in cc.split(",")
            ]

        message = {
            "subject": subject,
            "body": {
                "contentType": "HTML" if is_html else "Text",
                "content": body
            },
            "toRecipients": to_recipients,
        }

        if cc_recipients:
            message["ccRecipients"] = cc_recipients

        client.post("/me/sendMail", json_data={"message": message})

        return f"""## Email Sent Successfully

**To:** {to}
**Subject:** {subject}
**CC:** {cc or 'None'}"""

    except GraphAPIError as e:
        return f"Error sending email: {e}"
    except Exception as e:
        logger.error(f"[Mail] Send mail failed: {e}")
        return f"Error: {str(e)}"


def list_mail_folders() -> str:
    """
    List all mail folders in your mailbox.
    """
    try:
        client = get_graph_client()

        result = client.get("/me/mailFolders", params={"$top": 50})
        folders = result.get("value", [])

        if not folders:
            return "No mail folders found."

        output = "## Mail Folders\n\n"
        output += "| Name | Unread | Total | ID |\n"
        output += "|------|--------|-------|----|\n"

        for folder in folders:
            name = folder.get("displayName", "Unnamed")
            unread = folder.get("unreadItemCount", 0)
            total = folder.get("totalItemCount", 0)
            folder_id = folder.get("id", "")[:20]
            output += f"| {name} | {unread} | {total} | `{folder_id}...` |\n"

        return output

    except GraphAPIError as e:
        return f"Error listing folders: {e}"
    except Exception as e:
        logger.error(f"[Mail] List folders failed: {e}")
        return f"Error: {str(e)}"


def search_mail(query: str, limit: int = 25) -> str:
    """
    Search emails by subject, body, or sender.

    Args:
        query: Search query
        limit: Maximum results (default 25)
    """
    try:
        client = get_graph_client()

        endpoint = "/me/messages"
        params = {
            "$search": f'"{query}"',
            "$top": limit,
            "$select": "id,subject,from,receivedDateTime,bodyPreview"
        }

        result = client.get(endpoint, params=params)
        messages = result.get("value", [])

        if not messages:
            return f"No emails found matching: '{query}'"

        output = f"## Search Results for '{query}'\n\n"

        for msg in messages:
            subject = msg.get("subject", "(No Subject)")[:50]
            from_addr = msg.get("from", {}).get("emailAddress", {})
            from_name = from_addr.get("name", from_addr.get("address", "Unknown"))
            received = msg.get("receivedDateTime", "")[:10]
            msg_id = msg.get("id", "")[:20]

            output += f"- **{subject}** - {from_name} ({received}) `{msg_id}...`\n"

        return output

    except GraphAPIError as e:
        return f"Error searching emails: {e}"
    except Exception as e:
        logger.error(f"[Mail] Search failed: {e}")
        return f"Error: {str(e)}"

"""
Gmail Tools for Google Workspace MCP Server
100% 1-to-1 Parity with Gemini Enterprise (GE App) Gmail Action Connector (25 Actions).
"""
import base64
import json
import logging
from email.mime.text import MIMEText
from typing import Optional, List
import requests

logger = logging.getLogger("gworkspace-mcp.gmail")

GMAIL_API = "https://gmail.googleapis.com/gmail/v1"


def register_gmail_tools(mcp, auth_manager):
    """Register all 25 Gemini Enterprise Gmail Connector actions with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # -------------------------------------------------------------------------
    # 1-4. Batch Label / Unlabel Messages & Threads
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_batch_label_messages(message_ids: str, add_label_ids: str) -> str:
        """Add one or more labels to multiple Gmail messages in a single request (comma-separated IDs)."""
        try:
            ids = [i.strip() for i in message_ids.split(",") if i.strip()]
            labels = [l.strip() for l in add_label_ids.split(",") if l.strip()]
            resp = requests.post(
                f"{GMAIL_API}/users/me/messages/batchModify",
                headers=get_headers(),
                json={"ids": ids, "addLabelIds": labels}
            )
            resp.raise_for_status()
            return f"Successfully added labels {labels} to {len(ids)} messages."
        except Exception as e:
            return f"Error batch labeling messages: {e}"

    @mcp.tool()
    def gmail_batch_unlabel_messages(message_ids: str, remove_label_ids: str) -> str:
        """Remove one or more labels from multiple Gmail messages in a single request (comma-separated IDs)."""
        try:
            ids = [i.strip() for i in message_ids.split(",") if i.strip()]
            labels = [l.strip() for l in remove_label_ids.split(",") if l.strip()]
            resp = requests.post(
                f"{GMAIL_API}/users/me/messages/batchModify",
                headers=get_headers(),
                json={"ids": ids, "removeLabelIds": labels}
            )
            resp.raise_for_status()
            return f"Successfully removed labels {labels} from {len(ids)} messages."
        except Exception as e:
            return f"Error batch unlabeling messages: {e}"

    @mcp.tool()
    def gmail_batch_label_threads(thread_ids: str, add_label_ids: str) -> str:
        """Add one or more labels to multiple Gmail threads in a single request (comma-separated IDs)."""
        try:
            t_ids = [i.strip() for i in thread_ids.split(",") if i.strip()]
            labels = [l.strip() for l in add_label_ids.split(",") if l.strip()]
            for tid in t_ids:
                requests.post(
                    f"{GMAIL_API}/users/me/threads/{tid}/modify",
                    headers=get_headers(),
                    json={"addLabelIds": labels}
                ).raise_for_status()
            return f"Successfully added labels {labels} to {len(t_ids)} threads."
        except Exception as e:
            return f"Error batch labeling threads: {e}"

    @mcp.tool()
    def gmail_batch_unlabel_threads(thread_ids: str, remove_label_ids: str) -> str:
        """Remove one or more labels from multiple Gmail threads in a single request (comma-separated IDs)."""
        try:
            t_ids = [i.strip() for i in thread_ids.split(",") if i.strip()]
            labels = [l.strip() for l in remove_label_ids.split(",") if l.strip()]
            for tid in t_ids:
                requests.post(
                    f"{GMAIL_API}/users/me/threads/{tid}/modify",
                    headers=get_headers(),
                    json={"removeLabelIds": labels}
                ).raise_for_status()
            return f"Successfully removed labels {labels} from {len(t_ids)} threads."
        except Exception as e:
            return f"Error batch unlabeling threads: {e}"

    # -------------------------------------------------------------------------
    # 5, 15, 24. Draft Operations: Create draft, List drafts, Update draft
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_create_draft(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        """Create a new Gmail draft."""
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            resp = requests.post(
                f"{GMAIL_API}/users/me/drafts",
                headers=get_headers(),
                json={"message": {"raw": raw}}
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Draft created successfully! Draft ID: {data.get('id')}"
        except Exception as e:
            return f"Error creating draft: {e}"

    @mcp.tool()
    def gmail_list_drafts(max_results: int = 20) -> str:
        """List Gmail drafts in the user's mailbox."""
        try:
            resp = requests.get(
                f"{GMAIL_API}/users/me/drafts",
                headers=get_headers(),
                params={"maxResults": max_results}
            )
            resp.raise_for_status()
            drafts = resp.json().get("drafts", [])
            if not drafts:
                return "No drafts found."
            lines = []
            for d in drafts:
                did = d["id"]
                detail = requests.get(f"{GMAIL_API}/users/me/drafts/{did}", headers=get_headers()).json()
                headers = {h["name"]: h["value"] for h in detail.get("message", {}).get("payload", {}).get("headers", [])}
                lines.append(f"- **Draft ID:** `{did}` | **To:** {headers.get('To', 'N/A')} | **Subject:** {headers.get('Subject', '(no subject)')}")
            return "## Gmail Drafts\n\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing drafts: {e}"

    @mcp.tool()
    def gmail_update_draft(draft_id: str, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        """Update an existing Gmail draft."""
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            resp = requests.put(
                f"{GMAIL_API}/users/me/drafts/{draft_id}",
                headers=get_headers(),
                json={"id": draft_id, "message": {"raw": raw}}
            )
            resp.raise_for_status()
            return f"Draft `{draft_id}` updated successfully!"
        except Exception as e:
            return f"Error updating draft: {e}"

    # -------------------------------------------------------------------------
    # 6, 8, 16. Filter Operations: Create filter, Delete filter, List filters
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_create_filter(from_email: str = "", query: str = "", add_label_ids: str = "", mark_important: bool = False) -> str:
        """Create a new Gmail filter."""
        try:
            criteria = {}
            if from_email:
                criteria["from"] = from_email
            if query:
                criteria["query"] = query
            action = {}
            if add_label_ids:
                action["addLabelIds"] = [l.strip() for l in add_label_ids.split(",") if l.strip()]
            if mark_important:
                action.setdefault("addLabelIds", []).append("IMPORTANT")
            resp = requests.post(
                f"{GMAIL_API}/users/me/settings/filters",
                headers=get_headers(),
                json={"criteria": criteria, "action": action}
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Filter created successfully! Filter ID: `{data.get('id')}`"
        except Exception as e:
            return f"Error creating filter: {e}"

    @mcp.tool()
    def gmail_delete_filter(filter_id: str) -> str:
        """Delete an existing Gmail filter."""
        try:
            resp = requests.delete(f"{GMAIL_API}/users/me/settings/filters/{filter_id}", headers=get_headers())
            resp.raise_for_status()
            return f"Filter `{filter_id}` deleted successfully."
        except Exception as e:
            return f"Error deleting filter: {e}"

    @mcp.tool()
    def gmail_list_filters() -> str:
        """List Gmail filters in the user's mailbox."""
        try:
            resp = requests.get(f"{GMAIL_API}/users/me/settings/filters", headers=get_headers())
            resp.raise_for_status()
            filters = resp.json().get("filter", [])
            if not filters:
                return "No Gmail filters configured."
            lines = [f"- **ID:** `{f.get('id')}` | **Criteria:** `{json.dumps(f.get('criteria', {}))}` | **Action:** `{json.dumps(f.get('action', {}))}`" for f in filters]
            return "## Gmail Filters\n\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing filters: {e}"

    # -------------------------------------------------------------------------
    # 7, 9, 17, 25. Label CRUD: Create label, Delete label, List labels, Update label
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_create_label(name: str) -> str:
        """Create a new label in Gmail."""
        try:
            resp = requests.post(
                f"{GMAIL_API}/users/me/labels",
                headers=get_headers(),
                json={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Label created! Name: **{data.get('name')}** | ID: `{data.get('id')}`"
        except Exception as e:
            return f"Error creating label: {e}"

    @mcp.tool()
    def gmail_delete_label(label_id: str) -> str:
        """Delete an existing Gmail label."""
        try:
            resp = requests.delete(f"{GMAIL_API}/users/me/labels/{label_id}", headers=get_headers())
            resp.raise_for_status()
            return f"Label `{label_id}` deleted successfully."
        except Exception as e:
            return f"Error deleting label: {e}"

    @mcp.tool()
    def gmail_update_label(label_id: str, new_name: str) -> str:
        """Update an existing Gmail label."""
        try:
            resp = requests.patch(
                f"{GMAIL_API}/users/me/labels/{label_id}",
                headers=get_headers(),
                json={"name": new_name}
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Label `{label_id}` updated to **{data.get('name')}**."
        except Exception as e:
            return f"Error updating label: {e}"

    @mcp.tool()
    def gmail_list_labels() -> str:
        """List labels defined in the user's Gmail mailbox."""
        try:
            resp = requests.get(f"{GMAIL_API}/users/me/labels", headers=get_headers())
            resp.raise_for_status()
            labels = resp.json().get("labels", [])
            lines = [f"- **{l.get('name')}** (ID: `{l.get('id')}`, Type: {l.get('type')})" for l in labels]
            return "## Gmail Labels\n\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing labels: {e}"

    # -------------------------------------------------------------------------
    # 10, 19, 21. Send, Reply, Forward
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_send_message(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        """Send a new Gmail message."""
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            resp = requests.post(
                f"{GMAIL_API}/users/me/messages/send",
                headers=get_headers(),
                json={"raw": raw}
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Email sent successfully! Message ID: {data.get('id')} | Thread ID: {data.get('threadId')}"
        except Exception as e:
            return f"Error sending email: {e}"

    @mcp.tool()
    def gmail_reply(message_id: str, body: str, reply_all: bool = False) -> str:
        """Reply to an existing Gmail message."""
        try:
            orig = requests.get(f"{GMAIL_API}/users/me/messages/{message_id}", headers=get_headers()).json()
            thread_id = orig.get("threadId")
            headers = {h["name"]: h["value"] for h in orig.get("payload", {}).get("headers", [])}
            subject = headers.get("Subject", "")
            if not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"
            to_addr = headers.get("Reply-To") or headers.get("From", "")
            msg_id_hdr = headers.get("Message-ID", "")

            message = MIMEText(body)
            message["to"] = to_addr
            message["subject"] = subject
            if msg_id_hdr:
                message["In-Reply-To"] = msg_id_hdr
                message["References"] = msg_id_hdr
            if reply_all and headers.get("Cc"):
                message["cc"] = headers.get("Cc")

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            resp = requests.post(
                f"{GMAIL_API}/users/me/messages/send",
                headers=get_headers(),
                json={"raw": raw, "threadId": thread_id}
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Reply sent successfully! Message ID: `{data.get('id')}` in Thread `{thread_id}`"
        except Exception as e:
            return f"Error replying to message: {e}"

    @mcp.tool()
    def gmail_forward(message_id: str, to: str, comment: str = "") -> str:
        """Forward an existing Gmail message."""
        try:
            orig = requests.get(f"{GMAIL_API}/users/me/messages/{message_id}", headers=get_headers()).json()
            headers = {h["name"]: h["value"] for h in orig.get("payload", {}).get("headers", [])}
            subject = headers.get("Subject", "")
            if not subject.lower().startswith("fwd:"):
                subject = f"Fwd: {subject}"
            snippet = orig.get("snippet", "")
            full_body = f"{comment}\n\n---------- Forwarded message ---------\nFrom: {headers.get('From')}\nSubject: {headers.get('Subject')}\n\n{snippet}"
            return gmail_send_message(to=to, subject=subject, body=full_body)
        except Exception as e:
            return f"Error forwarding message: {e}"

    # -------------------------------------------------------------------------
    # 11. Get message attachment metadata
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_get_message_attachment(message_id: str, attachment_id: str) -> str:
        """Fetch metadata and size for an attachment on a Gmail message."""
        try:
            resp = requests.get(
                f"{GMAIL_API}/users/me/messages/{message_id}/attachments/{attachment_id}",
                headers=get_headers()
            )
            resp.raise_for_status()
            data = resp.json()
            return f"Attachment ID: `{attachment_id}` | Size: {data.get('size', 0)} bytes"
        except Exception as e:
            return f"Error fetching attachment: {e}"

    # -------------------------------------------------------------------------
    # 12, 18, 20. Thread Discovery: Get thread, List threads, Search threads
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_get_thread(thread_id: str) -> str:
        """Fetch the full contents of a Gmail thread."""
        try:
            resp = requests.get(f"{GMAIL_API}/users/me/threads/{thread_id}", headers=get_headers())
            resp.raise_for_status()
            data = resp.json()
            msgs = data.get("messages", [])
            output = [f"## Thread `{thread_id}` ({len(msgs)} messages)\n"]
            for m in msgs:
                headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
                output.append(
                    f"### Message `{m['id']}` | From: {headers.get('From')} | Date: {headers.get('Date')}\n"
                    f"**Subject:** {headers.get('Subject')}\n\n"
                    f"{m.get('snippet', '')}\n"
                )
            return "\n---\n".join(output)
        except Exception as e:
            return f"Error getting thread: {e}"

    @mcp.tool()
    def gmail_list_threads(max_results: int = 15, query: str = "") -> str:
        """List Gmail threads in the user's mailbox."""
        try:
            params = {"maxResults": max_results}
            if query:
                params["q"] = query
            resp = requests.get(f"{GMAIL_API}/users/me/threads", headers=get_headers(), params=params)
            resp.raise_for_status()
            threads = resp.json().get("threads", [])
            if not threads:
                return "No threads found."
            lines = [f"- **Thread ID:** `{t['id']}` — {t.get('snippet', '')[:100]}..." for t in threads]
            return "## Gmail Threads\n\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing threads: {e}"

    @mcp.tool()
    def gmail_search_threads(query: str, max_results: int = 15) -> str:
        """Search for Gmail threads matching a query."""
        return gmail_list_threads(max_results=max_results, query=query)

    # -------------------------------------------------------------------------
    # 13, 14, 22, 23. Single Message/Thread Label & Unlabel
    # -------------------------------------------------------------------------
    @mcp.tool()
    def gmail_label_message(message_id: str, add_label_ids: str) -> str:
        """Add one or more existing labels to a specific Gmail message."""
        return gmail_batch_label_messages(message_ids=message_id, add_label_ids=add_label_ids)

    @mcp.tool()
    def gmail_unlabel_message(message_id: str, remove_label_ids: str) -> str:
        """Remove one or more existing labels from a specific Gmail message."""
        return gmail_batch_unlabel_messages(message_ids=message_id, remove_label_ids=remove_label_ids)

    @mcp.tool()
    def gmail_label_thread(thread_id: str, add_label_ids: str) -> str:
        """Add one or more existing labels to a specific Gmail thread."""
        return gmail_batch_label_threads(thread_ids=thread_id, add_label_ids=add_label_ids)

    @mcp.tool()
    def gmail_unlabel_thread(thread_id: str, remove_label_ids: str) -> str:
        """Remove one or more existing labels from a specific Gmail thread."""
        return gmail_batch_unlabel_threads(thread_ids=thread_id, remove_label_ids=remove_label_ids)

    # Legacy helper aliases
    @mcp.tool()
    def gmail_list_messages(max_results: int = 10, query: str = "") -> str:
        """List Gmail messages matching query."""
        return gmail_list_threads(max_results=max_results, query=query)

    @mcp.tool()
    def gmail_get_message(message_id: str) -> str:
        """Get content of a specific Gmail message."""
        try:
            resp = requests.get(f"{GMAIL_API}/users/me/messages/{message_id}", headers=get_headers()).json()
            return gmail_get_thread(resp.get("threadId", message_id))
        except Exception as e:
            return f"Error getting message: {e}"

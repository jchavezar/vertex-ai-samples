"""
Microsoft Teams Tools for Microsoft 365 MCP Server
"""
import logging
from typing import Optional
from graph_client import get_graph_client, GraphAPIError

logger = logging.getLogger("ms365-mcp.tools.teams")


def list_teams() -> str:
    """
    List all Teams you are a member of.
    """
    try:
        client = get_graph_client()

        result = client.get("/me/joinedTeams")
        teams = result.get("value", [])

        if not teams:
            return "You are not a member of any Teams."

        output = "## Your Teams\n\n"
        output += "| Team Name | Description | ID |\n"
        output += "|-----------|-------------|----|\n"

        for team in teams:
            name = team.get("displayName", "Unnamed")
            desc = (team.get("description") or "")[:40]
            team_id = team.get("id", "")[:20]
            output += f"| {name} | {desc} | `{team_id}...` |\n"

        return output

    except GraphAPIError as e:
        return f"Error listing teams: {e}"
    except Exception as e:
        logger.error(f"[Teams] List teams failed: {e}")
        return f"Error: {str(e)}"


def list_team_channels(team_id: str) -> str:
    """
    List channels in a Team.

    Args:
        team_id: The Team ID (from list_teams)
    """
    try:
        client = get_graph_client()

        result = client.get(f"/teams/{team_id}/channels")
        channels = result.get("value", [])

        if not channels:
            return "No channels found in this team."

        output = "## Team Channels\n\n"
        output += "| Channel Name | Description | ID |\n"
        output += "|--------------|-------------|----|\n"

        for channel in channels:
            name = channel.get("displayName", "Unnamed")
            desc = (channel.get("description") or "")[:40]
            channel_id = channel.get("id", "")[:20]
            output += f"| {name} | {desc} | `{channel_id}...` |\n"

        return output

    except GraphAPIError as e:
        return f"Error listing channels: {e}"
    except Exception as e:
        logger.error(f"[Teams] List channels failed: {e}")
        return f"Error: {str(e)}"


def list_channel_messages(
    team_id: str,
    channel_id: str,
    limit: int = 20
) -> str:
    """
    List recent messages in a Teams channel.

    Args:
        team_id: The Team ID
        channel_id: The Channel ID (from list_team_channels)
        limit: Maximum number of messages to return (default 20)
    """
    try:
        client = get_graph_client()

        endpoint = f"/teams/{team_id}/channels/{channel_id}/messages"
        result = client.get(endpoint, params={"$top": limit})
        messages = result.get("value", [])

        if not messages:
            return "No messages found in this channel."

        output = "## Channel Messages\n\n"

        for msg in messages:
            msg_type = msg.get("messageType", "message")
            if msg_type != "message":
                continue  # Skip system messages

            sender = msg.get("from", {}).get("user", {})
            sender_name = sender.get("displayName", "Unknown")

            created = msg.get("createdDateTime", "")[:16].replace("T", " ")

            body = msg.get("body", {})
            content = body.get("content", "")

            # Strip HTML
            import re
            content = re.sub(r'<[^>]+>', '', content)[:200]

            msg_id = msg.get("id", "")[:20]

            output += f"**{sender_name}** ({created})\n"
            output += f"> {content}\n"
            output += f"*ID: `{msg_id}...`*\n\n---\n\n"

        return output

    except GraphAPIError as e:
        return f"Error listing messages: {e}"
    except Exception as e:
        logger.error(f"[Teams] List messages failed: {e}")
        return f"Error: {str(e)}"


def send_channel_message(
    team_id: str,
    channel_id: str,
    message: str
) -> str:
    """
    Send a message to a Teams channel.

    Args:
        team_id: The Team ID
        channel_id: The Channel ID
        message: The message content
    """
    try:
        client = get_graph_client()

        endpoint = f"/teams/{team_id}/channels/{channel_id}/messages"
        result = client.post(endpoint, json_data={
            "body": {
                "content": message
            }
        })

        msg_id = result.get("id", "")[:20]
        return f"""## Message Sent

**Channel:** {channel_id[:20]}...
**Message ID:** `{msg_id}...`
**Content:** {message[:100]}..."""

    except GraphAPIError as e:
        return f"Error sending message: {e}"
    except Exception as e:
        logger.error(f"[Teams] Send message failed: {e}")
        return f"Error: {str(e)}"


def list_chats(limit: int = 25) -> str:
    """
    List your recent Teams chats.

    Args:
        limit: Maximum number of chats to return (default 25)
    """
    try:
        client = get_graph_client()

        result = client.get("/me/chats", params={
            "$top": limit,
            "$expand": "members"
        })
        chats = result.get("value", [])

        if not chats:
            return "No chats found."

        output = "## Your Chats\n\n"

        for chat in chats:
            chat_type = chat.get("chatType", "unknown")
            topic = chat.get("topic", "")
            chat_id = chat.get("id", "")[:20]

            # Get member names
            members = chat.get("members", [])
            member_names = [
                m.get("displayName", "Unknown")
                for m in members[:5]
            ]
            members_str = ", ".join(member_names)
            if len(members) > 5:
                members_str += f" +{len(members) - 5} more"

            if chat_type == "oneOnOne":
                title = f"Chat with {members_str}"
            elif chat_type == "group":
                title = topic or f"Group: {members_str}"
            else:
                title = topic or f"Chat ({chat_type})"

            output += f"### {title}\n"
            output += f"**Type:** {chat_type}  \n"
            output += f"**ID:** `{chat_id}...`\n\n"

        return output

    except GraphAPIError as e:
        return f"Error listing chats: {e}"
    except Exception as e:
        logger.error(f"[Teams] List chats failed: {e}")
        return f"Error: {str(e)}"


def list_chat_messages(chat_id: str, limit: int = 20) -> str:
    """
    List recent messages in a Teams chat.

    Args:
        chat_id: The chat ID (from list_chats)
        limit: Maximum number of messages to return (default 20)
    """
    try:
        client = get_graph_client()

        endpoint = f"/me/chats/{chat_id}/messages"
        result = client.get(endpoint, params={"$top": limit})
        messages = result.get("value", [])

        if not messages:
            return "No messages found in this chat."

        output = "## Chat Messages\n\n"

        for msg in messages:
            msg_type = msg.get("messageType", "message")
            if msg_type != "message":
                continue

            sender = msg.get("from", {}).get("user", {})
            sender_name = sender.get("displayName", "Unknown")

            created = msg.get("createdDateTime", "")[:16].replace("T", " ")

            body = msg.get("body", {})
            content = body.get("content", "")

            # Strip HTML
            import re
            content = re.sub(r'<[^>]+>', '', content)[:200]

            output += f"**{sender_name}** ({created})\n"
            output += f"> {content}\n\n---\n\n"

        return output

    except GraphAPIError as e:
        return f"Error listing chat messages: {e}"
    except Exception as e:
        logger.error(f"[Teams] List chat messages failed: {e}")
        return f"Error: {str(e)}"


def send_chat_message(chat_id: str, message: str) -> str:
    """
    Send a message to a Teams chat.

    Args:
        chat_id: The chat ID (from list_chats)
        message: The message content
    """
    try:
        client = get_graph_client()

        endpoint = f"/me/chats/{chat_id}/messages"
        result = client.post(endpoint, json_data={
            "body": {
                "content": message
            }
        })

        msg_id = result.get("id", "")[:20]
        return f"""## Message Sent

**Chat ID:** `{chat_id[:20]}...`
**Message ID:** `{msg_id}...`
**Content:** {message[:100]}..."""

    except GraphAPIError as e:
        return f"Error sending message: {e}"
    except Exception as e:
        logger.error(f"[Teams] Send chat message failed: {e}")
        return f"Error: {str(e)}"

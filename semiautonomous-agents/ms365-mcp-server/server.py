"""
Microsoft 365 MCP Server
Secure MCP server for Claude Code with delegated authentication.
"""
import os
import logging
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ms365-mcp")

# Initialize FastMCP server
mcp = FastMCP("Microsoft 365 MCP Server")

# ============================================================
# AUTHENTICATION TOOLS
# ============================================================

from tools.auth_tools import login, complete_login, logout, verify_login


@mcp.tool()
def ms365_login() -> str:
    """
    Start the Microsoft 365 login process using device code flow.
    Returns instructions for the user to complete authentication.
    """
    return login()


@mcp.tool()
def ms365_complete_login() -> str:
    """
    Complete the Microsoft 365 login after user has authenticated in browser.
    Must be called after 'ms365_login' and after user has completed browser authentication.
    """
    return complete_login()


@mcp.tool()
def ms365_logout() -> str:
    """
    Log out from Microsoft 365 and clear all cached tokens.
    """
    return logout()


@mcp.tool()
def ms365_verify_login() -> str:
    """
    Verify current Microsoft 365 authentication status.
    """
    return verify_login()


# ============================================================
# SHAREPOINT / ONEDRIVE TOOLS
# ============================================================

from tools.sharepoint import (
    list_sharepoint_sites,
    list_site_drives,
    list_folder_files,
    list_onedrive_files,
    upload_file,
    download_file,
    create_folder,
    search_files,
    search_content,
)


@mcp.tool()
def sp_list_sites(search: str = "") -> str:
    """
    List SharePoint sites you have access to.

    Args:
        search: Optional search term to filter sites by name
    """
    return list_sharepoint_sites(search)


@mcp.tool()
def sp_list_drives(site_id: str) -> str:
    """
    List document libraries (drives) in a SharePoint site.

    Args:
        site_id: The SharePoint site ID (from sp_list_sites)
    """
    return list_site_drives(site_id)


@mcp.tool()
def sp_list_files(drive_id: str, folder_path: str = "/", limit: int = 50) -> str:
    """
    List files and folders in a SharePoint or OneDrive location.

    Args:
        drive_id: The drive ID (from sp_list_drives) or 'me' for OneDrive
        folder_path: Path to folder (e.g., '/Documents/Reports') or '/' for root
        limit: Maximum number of items to return (default 50)
    """
    return list_folder_files(drive_id, folder_path, limit)


@mcp.tool()
def onedrive_list_files(folder_path: str = "/", limit: int = 50) -> str:
    """
    List files and folders in your personal OneDrive.

    Args:
        folder_path: Path to folder (e.g., '/Documents') or '/' for root
        limit: Maximum number of items to return (default 50)
    """
    return list_onedrive_files(folder_path, limit)


@mcp.tool()
def sp_upload_file(
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
    return upload_file(drive_id, folder_path, file_name, content, is_base64)


@mcp.tool()
def sp_download_file(drive_id: str, file_path: str) -> str:
    """
    Download a file from SharePoint or OneDrive.

    Args:
        drive_id: The drive ID or 'me' for OneDrive
        file_path: Path to the file (e.g., '/Documents/report.txt')
    """
    return download_file(drive_id, file_path)


@mcp.tool()
def sp_create_folder(drive_id: str, parent_path: str, folder_name: str) -> str:
    """
    Create a new folder in SharePoint or OneDrive.

    Args:
        drive_id: The drive ID or 'me' for OneDrive
        parent_path: Parent folder path (e.g., '/Documents') or '/' for root
        folder_name: Name for the new folder
    """
    return create_folder(drive_id, parent_path, folder_name)


@mcp.tool()
def sp_search_files(query: str, drive_id: str = "", limit: int = 25) -> str:
    """
    Search for files across SharePoint and OneDrive by file name.

    Args:
        query: Search query (file name)
        drive_id: Optional drive ID to limit search scope, or 'me' for OneDrive only
        limit: Maximum number of results (default 25)
    """
    return search_files(query, drive_id or None, limit)


@mcp.tool()
def sp_search_content(query: str, limit: int = 10) -> str:
    """
    Search within document content across SharePoint and OneDrive.
    Finds text inside documents (PDFs, Word docs, etc.) not just file names.

    Args:
        query: Text to search for within document content
        limit: Maximum number of results (default 10)
    """
    return search_content(query, limit)


# ============================================================
# MAIL (OUTLOOK) TOOLS
# ============================================================

from tools.mail import (
    list_mail_messages,
    get_mail_message,
    send_mail,
    list_mail_folders,
    search_mail,
)


@mcp.tool()
def mail_list_messages(
    folder: str = "inbox",
    limit: int = 25,
    unread_only: bool = False
) -> str:
    """
    List emails from your mailbox.

    Args:
        folder: Mail folder ('inbox', 'sent', 'drafts', 'deleted') or folder ID
        limit: Maximum number of emails to return (default 25)
        unread_only: If True, only show unread emails
    """
    return list_mail_messages(folder, limit, unread_only)


@mcp.tool()
def mail_get_message(message_id: str) -> str:
    """
    Get full details of a specific email.

    Args:
        message_id: The message ID (from mail_list_messages)
    """
    return get_mail_message(message_id)


@mcp.tool()
def mail_send(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
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
    return send_mail(to, subject, body, cc or None, is_html)


@mcp.tool()
def mail_list_folders() -> str:
    """
    List all mail folders in your mailbox.
    """
    return list_mail_folders()


@mcp.tool()
def mail_search(query: str, limit: int = 25) -> str:
    """
    Search emails by subject, body, or sender.

    Args:
        query: Search query
        limit: Maximum results (default 25)
    """
    return search_mail(query, limit)


# ============================================================
# CALENDAR TOOLS
# ============================================================

from tools.calendar import (
    list_calendar_events,
    get_calendar_event,
    create_calendar_event,
    list_calendars,
    delete_calendar_event,
)


@mcp.tool()
def cal_list_events(days_ahead: int = 7, limit: int = 25) -> str:
    """
    List upcoming calendar events.

    Args:
        days_ahead: Number of days to look ahead (default 7)
        limit: Maximum number of events to return (default 25)
    """
    return list_calendar_events(days_ahead, limit)


@mcp.tool()
def cal_get_event(event_id: str) -> str:
    """
    Get full details of a specific calendar event.

    Args:
        event_id: The event ID (from cal_list_events)
    """
    return get_calendar_event(event_id)


@mcp.tool()
def cal_create_event(
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: str = "",
    location: str = "",
    body: str = "",
    is_all_day: bool = False
) -> str:
    """
    Create a new calendar event.

    Args:
        subject: Event title
        start_datetime: Start time in ISO format (e.g., '2024-03-15T10:00:00')
        end_datetime: End time in ISO format (e.g., '2024-03-15T11:00:00')
        attendees: Optional comma-separated email addresses
        location: Optional location string
        body: Optional event description
        is_all_day: If True, create an all-day event
    """
    return create_calendar_event(
        subject, start_datetime, end_datetime,
        attendees or None, location or None, body or None, is_all_day
    )


@mcp.tool()
def cal_list_calendars() -> str:
    """
    List all calendars in your account.
    """
    return list_calendars()


@mcp.tool()
def cal_delete_event(event_id: str) -> str:
    """
    Delete a calendar event.

    Args:
        event_id: The event ID (from cal_list_events)
    """
    return delete_calendar_event(event_id)


# ============================================================
# TEAMS TOOLS
# ============================================================

from tools.teams import (
    list_teams,
    list_team_channels,
    list_channel_messages,
    send_channel_message,
    list_chats,
    list_chat_messages,
    send_chat_message,
)


@mcp.tool()
def teams_list_teams() -> str:
    """
    List all Teams you are a member of.
    """
    return list_teams()


@mcp.tool()
def teams_list_channels(team_id: str) -> str:
    """
    List channels in a Team.

    Args:
        team_id: The Team ID (from teams_list_teams)
    """
    return list_team_channels(team_id)


@mcp.tool()
def teams_list_channel_messages(team_id: str, channel_id: str, limit: int = 20) -> str:
    """
    List recent messages in a Teams channel.

    Args:
        team_id: The Team ID
        channel_id: The Channel ID (from teams_list_channels)
        limit: Maximum number of messages to return (default 20)
    """
    return list_channel_messages(team_id, channel_id, limit)


@mcp.tool()
def teams_send_channel_message(team_id: str, channel_id: str, message: str) -> str:
    """
    Send a message to a Teams channel.

    Args:
        team_id: The Team ID
        channel_id: The Channel ID
        message: The message content
    """
    return send_channel_message(team_id, channel_id, message)


@mcp.tool()
def teams_list_chats(limit: int = 25) -> str:
    """
    List your recent Teams chats.

    Args:
        limit: Maximum number of chats to return (default 25)
    """
    return list_chats(limit)


@mcp.tool()
def teams_list_chat_messages(chat_id: str, limit: int = 20) -> str:
    """
    List recent messages in a Teams chat.

    Args:
        chat_id: The chat ID (from teams_list_chats)
        limit: Maximum number of messages to return (default 20)
    """
    return list_chat_messages(chat_id, limit)


@mcp.tool()
def teams_send_chat_message(chat_id: str, message: str) -> str:
    """
    Send a message to a Teams chat.

    Args:
        chat_id: The chat ID (from teams_list_chats)
        message: The message content
    """
    return send_chat_message(chat_id, message)


# ============================================================
# SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")

    logger.info(f"[MCP] Starting Microsoft 365 MCP Server")
    logger.info(f"[MCP] Transport: {transport}")
    logger.info(f"[MCP] Port: {port}")

    mcp.run(
        transport=transport,
        host="0.0.0.0",
        port=port
    )

"""
Calendar Tools for Microsoft 365 MCP Server
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from graph_client import get_graph_client, GraphAPIError

logger = logging.getLogger("ms365-mcp.tools.calendar")


def list_calendar_events(
    days_ahead: int = 7,
    limit: int = 25
) -> str:
    """
    List upcoming calendar events.

    Args:
        days_ahead: Number of days to look ahead (default 7)
        limit: Maximum number of events to return (default 25)
    """
    try:
        client = get_graph_client()

        # Calculate date range
        now = datetime.utcnow()
        start_time = now.strftime("%Y-%m-%dT%H:%M:%S.0000000")
        end_time = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%S.0000000")

        endpoint = "/me/calendarView"
        params = {
            "startDateTime": start_time,
            "endDateTime": end_time,
            "$top": limit,
            "$orderby": "start/dateTime",
            "$select": "id,subject,start,end,location,organizer,isAllDay,webLink"
        }

        result = client.get(endpoint, params=params)
        events = result.get("value", [])

        if not events:
            return f"No upcoming events in the next {days_ahead} days."

        output = f"## Upcoming Events (Next {days_ahead} Days)\n\n"

        for event in events:
            subject = event.get("subject", "(No Title)")
            is_all_day = event.get("isAllDay", False)

            start = event.get("start", {})
            end = event.get("end", {})

            if is_all_day:
                start_str = start.get("dateTime", "")[:10]
                time_str = "All Day"
            else:
                start_dt = start.get("dateTime", "")[:16].replace("T", " ")
                end_dt = end.get("dateTime", "")[11:16]
                time_str = f"{start_dt} - {end_dt}"

            location = event.get("location", {}).get("displayName", "")
            location_str = f" | {location}" if location else ""

            organizer = event.get("organizer", {}).get("emailAddress", {})
            organizer_name = organizer.get("name", organizer.get("address", ""))

            event_id = event.get("id", "")[:20]

            output += f"### {subject}\n"
            output += f"**When:** {time_str}{location_str}\n"
            if organizer_name:
                output += f"**Organizer:** {organizer_name}\n"
            output += f"**ID:** `{event_id}...`\n\n"

        return output

    except GraphAPIError as e:
        return f"Error listing events: {e}"
    except Exception as e:
        logger.error(f"[Calendar] List events failed: {e}")
        return f"Error: {str(e)}"


def get_calendar_event(event_id: str) -> str:
    """
    Get full details of a specific calendar event.

    Args:
        event_id: The event ID (from list_calendar_events)
    """
    try:
        client = get_graph_client()

        result = client.get(f"/me/events/{event_id}")

        subject = result.get("subject", "(No Title)")
        body = result.get("body", {}).get("content", "")

        # Strip HTML
        import re
        body = re.sub(r'<[^>]+>', '', body)[:1000]

        start = result.get("start", {})
        end = result.get("end", {})
        is_all_day = result.get("isAllDay", False)

        if is_all_day:
            time_str = f"{start.get('dateTime', '')[:10]} (All Day)"
        else:
            start_str = start.get("dateTime", "")[:16].replace("T", " ")
            end_str = end.get("dateTime", "")[:16].replace("T", " ")
            time_str = f"{start_str} to {end_str}"

        location = result.get("location", {}).get("displayName", "Not specified")

        organizer = result.get("organizer", {}).get("emailAddress", {})
        organizer_str = f"{organizer.get('name', '')} <{organizer.get('address', '')}>"

        attendees = result.get("attendees", [])
        attendee_list = []
        for att in attendees[:10]:
            email = att.get("emailAddress", {})
            status = att.get("status", {}).get("response", "none")
            attendee_list.append(f"- {email.get('name', email.get('address', ''))} ({status})")

        attendees_str = "\n".join(attendee_list) if attendee_list else "None"

        web_link = result.get("webLink", "")

        output = f"""## {subject}

**When:** {time_str}
**Location:** {location}
**Organizer:** {organizer_str}

### Attendees
{attendees_str}

### Description
{body if body else 'No description'}

**Link:** {web_link}
"""
        return output

    except GraphAPIError as e:
        return f"Error getting event: {e}"
    except Exception as e:
        logger.error(f"[Calendar] Get event failed: {e}")
        return f"Error: {str(e)}"


def create_calendar_event(
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: Optional[str] = None,
    location: Optional[str] = None,
    body: Optional[str] = None,
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
        is_all_day: If True, create an all-day event (use date only, e.g., '2024-03-15')
    """
    try:
        client = get_graph_client()

        event = {
            "subject": subject,
            "start": {
                "dateTime": start_datetime,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": "UTC"
            },
            "isAllDay": is_all_day
        }

        if location:
            event["location"] = {"displayName": location}

        if body:
            event["body"] = {
                "contentType": "Text",
                "content": body
            }

        if attendees:
            event["attendees"] = [
                {
                    "emailAddress": {"address": addr.strip()},
                    "type": "required"
                }
                for addr in attendees.split(",")
            ]

        result = client.post("/me/events", json_data=event)

        created_id = result.get("id", "")[:20]
        web_link = result.get("webLink", "")

        return f"""## Event Created Successfully

**Subject:** {subject}
**Start:** {start_datetime}
**End:** {end_datetime}
**Location:** {location or 'Not specified'}
**Attendees:** {attendees or 'None'}
**ID:** `{created_id}...`
**Link:** {web_link}"""

    except GraphAPIError as e:
        return f"Error creating event: {e}"
    except Exception as e:
        logger.error(f"[Calendar] Create event failed: {e}")
        return f"Error: {str(e)}"


def list_calendars() -> str:
    """
    List all calendars in your account.
    """
    try:
        client = get_graph_client()

        result = client.get("/me/calendars")
        calendars = result.get("value", [])

        if not calendars:
            return "No calendars found."

        output = "## Your Calendars\n\n"
        output += "| Name | Can Edit | Color | ID |\n"
        output += "|------|----------|-------|----|\n"

        for cal in calendars:
            name = cal.get("name", "Unnamed")
            can_edit = "Yes" if cal.get("canEdit", False) else "No"
            color = cal.get("color", "auto")
            cal_id = cal.get("id", "")[:20]
            output += f"| {name} | {can_edit} | {color} | `{cal_id}...` |\n"

        return output

    except GraphAPIError as e:
        return f"Error listing calendars: {e}"
    except Exception as e:
        logger.error(f"[Calendar] List calendars failed: {e}")
        return f"Error: {str(e)}"


def delete_calendar_event(event_id: str) -> str:
    """
    Delete a calendar event.

    Args:
        event_id: The event ID (from list_calendar_events)
    """
    try:
        client = get_graph_client()
        client.delete(f"/me/events/{event_id}")
        return f"Event deleted successfully. ID: `{event_id[:20]}...`"

    except GraphAPIError as e:
        return f"Error deleting event: {e}"
    except Exception as e:
        logger.error(f"[Calendar] Delete event failed: {e}")
        return f"Error: {str(e)}"

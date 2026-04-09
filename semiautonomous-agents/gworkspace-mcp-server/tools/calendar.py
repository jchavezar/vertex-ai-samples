"""
Google Calendar Tools for Google Workspace MCP Server
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import requests

logger = logging.getLogger("gworkspace-mcp.calendar")

CALENDAR_API = "https://www.googleapis.com/calendar/v3"


def register_calendar_tools(mcp, auth_manager):
    """Register Google Calendar tools with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}"}

    @mcp.tool()
    def calendar_list_calendars() -> str:
        """List all calendars accessible to the user."""
        try:
            response = requests.get(
                f"{CALENDAR_API}/users/me/calendarList",
                headers=get_headers()
            )
            response.raise_for_status()
            data = response.json()

            calendars = data.get("items", [])
            if not calendars:
                return "No calendars found."

            results = []
            for cal in calendars:
                primary = " (Primary)" if cal.get("primary") else ""
                results.append(
                    f"**{cal.get('summary', 'Unnamed')}**{primary}\n"
                    f"  - ID: `{cal.get('id')}`\n"
                    f"  - Access Role: {cal.get('accessRole', 'Unknown')}"
                )

            return f"## Your Calendars ({len(results)} found)\n\n" + "\n\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Calendar list error: {e}")
            return f"Error listing calendars: {str(e)}"

    @mcp.tool()
    def calendar_list_events(
        calendar_id: str = "primary",
        max_results: int = 10,
        days_ahead: int = 7
    ) -> str:
        """
        List upcoming calendar events.

        Args:
            calendar_id: Calendar ID (default "primary")
            max_results: Maximum events to return (default 10)
            days_ahead: Number of days to look ahead (default 7)
        """
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + "Z"
            time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"

            response = requests.get(
                f"{CALENDAR_API}/calendars/{calendar_id}/events",
                headers=get_headers(),
                params={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "maxResults": max_results,
                    "singleEvents": True,
                    "orderBy": "startTime"
                }
            )
            response.raise_for_status()
            data = response.json()

            events = data.get("items", [])
            if not events:
                return f"No events found in the next {days_ahead} days."

            results = []
            for event in events:
                start = event.get("start", {})
                end = event.get("end", {})

                # Handle all-day vs timed events
                if "date" in start:
                    start_str = start["date"]
                    end_str = end.get("date", "")
                    time_info = f"All day: {start_str}"
                else:
                    start_str = start.get("dateTime", "")[:16].replace("T", " ")
                    end_str = end.get("dateTime", "")[:16].replace("T", " ")
                    time_info = f"{start_str} - {end_str}"

                location = event.get("location", "")
                location_str = f"\n  - Location: {location}" if location else ""

                attendees = event.get("attendees", [])
                attendees_str = ""
                if attendees:
                    names = [a.get("email", "Unknown") for a in attendees[:5]]
                    if len(attendees) > 5:
                        names.append(f"...and {len(attendees) - 5} more")
                    attendees_str = f"\n  - Attendees: {', '.join(names)}"

                results.append(
                    f"**{event.get('summary', '(No title)')}**\n"
                    f"  - ID: `{event.get('id')}`\n"
                    f"  - Time: {time_info}{location_str}{attendees_str}"
                )

            return f"## Upcoming Events ({len(results)} found)\n\n" + "\n\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Calendar events error: {e}")
            return f"Error listing events: {str(e)}"

    @mcp.tool()
    def calendar_get_event(
        event_id: str,
        calendar_id: str = "primary"
    ) -> str:
        """
        Get details of a specific calendar event.

        Args:
            event_id: The event ID
            calendar_id: Calendar ID (default "primary")
        """
        try:
            response = requests.get(
                f"{CALENDAR_API}/calendars/{calendar_id}/events/{event_id}",
                headers=get_headers()
            )
            response.raise_for_status()
            event = response.json()

            start = event.get("start", {})
            end = event.get("end", {})

            if "date" in start:
                time_info = f"All day: {start['date']} to {end.get('date', '')}"
            else:
                time_info = f"{start.get('dateTime', '')[:16]} to {end.get('dateTime', '')[:16]}"

            attendees = event.get("attendees", [])
            attendees_str = "\n".join([
                f"  - {a.get('email')} ({a.get('responseStatus', 'unknown')})"
                for a in attendees
            ]) or "None"

            return f"""## Event Details

**Title:** {event.get('summary', '(No title)')}
**ID:** `{event.get('id')}`
**Status:** {event.get('status', 'Unknown')}
**Time:** {time_info}
**Location:** {event.get('location', 'None')}
**Organizer:** {event.get('organizer', {}).get('email', 'Unknown')}
**Created:** {event.get('created', 'Unknown')}

**Description:**
{event.get('description', 'No description')}

**Attendees:**
{attendees_str}

**Link:** {event.get('htmlLink', 'N/A')}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Calendar get event error: {e}")
            return f"Error getting event: {str(e)}"

    @mcp.tool()
    def calendar_create_event(
        summary: str,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
        description: str = "",
        location: str = "",
        attendees: str = ""
    ) -> str:
        """
        Create a new calendar event.

        Args:
            summary: Event title
            start_time: Start time in ISO format (e.g., "2024-01-15T10:00:00")
            end_time: End time in ISO format (e.g., "2024-01-15T11:00:00")
            calendar_id: Calendar ID (default "primary")
            description: Event description (optional)
            location: Event location (optional)
            attendees: Comma-separated email addresses (optional)
        """
        try:
            event = {
                "summary": summary,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }

            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if attendees:
                event["attendees"] = [
                    {"email": email.strip()} for email in attendees.split(",")
                ]

            response = requests.post(
                f"{CALENDAR_API}/calendars/{calendar_id}/events",
                headers={**get_headers(), "Content-Type": "application/json"},
                json=event
            )
            response.raise_for_status()
            data = response.json()

            return f"""Event created successfully!

**Title:** {data.get('summary')}
**ID:** `{data.get('id')}`
**Link:** {data.get('htmlLink')}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Calendar create error: {e}")
            return f"Error creating event: {str(e)}"

    @mcp.tool()
    def calendar_delete_event(
        event_id: str,
        calendar_id: str = "primary"
    ) -> str:
        """
        Delete a calendar event.

        Args:
            event_id: The event ID to delete
            calendar_id: Calendar ID (default "primary")
        """
        try:
            response = requests.delete(
                f"{CALENDAR_API}/calendars/{calendar_id}/events/{event_id}",
                headers=get_headers()
            )
            response.raise_for_status()

            return f"Event deleted successfully (ID: {event_id})"

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Calendar delete error: {e}")
            return f"Error deleting event: {str(e)}"

    @mcp.tool()
    def calendar_update_event(
        event_id: str,
        calendar_id: str = "primary",
        summary: str = "",
        start_time: str = "",
        end_time: str = "",
        description: str = "",
        location: str = ""
    ) -> str:
        """
        Update an existing calendar event.

        Args:
            event_id: The event ID to update
            calendar_id: Calendar ID (default "primary")
            summary: New event title (optional)
            start_time: New start time in ISO format (optional)
            end_time: New end time in ISO format (optional)
            description: New description (optional)
            location: New location (optional)
        """
        try:
            # First get existing event
            response = requests.get(
                f"{CALENDAR_API}/calendars/{calendar_id}/events/{event_id}",
                headers=get_headers()
            )
            response.raise_for_status()
            event = response.json()

            # Update fields
            if summary:
                event["summary"] = summary
            if start_time:
                event["start"] = {"dateTime": start_time, "timeZone": "UTC"}
            if end_time:
                event["end"] = {"dateTime": end_time, "timeZone": "UTC"}
            if description:
                event["description"] = description
            if location:
                event["location"] = location

            # Update event
            response = requests.put(
                f"{CALENDAR_API}/calendars/{calendar_id}/events/{event_id}",
                headers={**get_headers(), "Content-Type": "application/json"},
                json=event
            )
            response.raise_for_status()
            data = response.json()

            return f"""Event updated successfully!

**Title:** {data.get('summary')}
**ID:** `{data.get('id')}`
**Link:** {data.get('htmlLink')}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Calendar update error: {e}")
            return f"Error updating event: {str(e)}"

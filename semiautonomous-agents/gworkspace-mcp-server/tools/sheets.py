"""
Google Sheets Tools for Google Workspace MCP Server
"""
import logging
from typing import Optional, List
import requests

logger = logging.getLogger("gworkspace-mcp.sheets")

SHEETS_API = "https://sheets.googleapis.com/v4"
DRIVE_API = "https://www.googleapis.com/drive/v3"


def register_sheets_tools(mcp, auth_manager):
    """Register Google Sheets tools with the MCP server."""

    def get_headers():
        token = auth_manager.get_access_token()
        if not token:
            raise ValueError("Not authenticated. Run gworkspace_login first.")
        return {"Authorization": f"Bearer {token}"}

    @mcp.tool()
    def sheets_list() -> str:
        """List Google Sheets in Drive."""
        try:
            response = requests.get(
                f"{DRIVE_API}/files",
                headers=get_headers(),
                params={
                    "q": "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                    "pageSize": 20,
                    "fields": "files(id,name,modifiedTime,webViewLink)",
                    "orderBy": "modifiedTime desc"
                }
            )
            response.raise_for_status()
            data = response.json()

            files = data.get("files", [])
            if not files:
                return "No Google Sheets found."

            results = []
            for f in files:
                results.append(
                    f"**{f['name']}**\n"
                    f"  - ID: `{f['id']}`\n"
                    f"  - Modified: {f.get('modifiedTime', 'Unknown')}\n"
                    f"  - [Open]({f.get('webViewLink', '#')})"
                )

            return f"## Google Sheets ({len(results)} found)\n\n" + "\n\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Sheets list error: {e}")
            return f"Error listing sheets: {str(e)}"

    @mcp.tool()
    def sheets_get(
        spreadsheet_id: str,
        range: str = ""
    ) -> str:
        """
        Get data from a Google Sheet.

        Args:
            spreadsheet_id: The spreadsheet ID
            range: A1 notation range (e.g., "Sheet1!A1:D10"). If empty, gets first sheet.
        """
        try:
            # First get spreadsheet metadata
            meta_response = requests.get(
                f"{SHEETS_API}/spreadsheets/{spreadsheet_id}",
                headers=get_headers(),
                params={"fields": "properties.title,sheets.properties"}
            )
            meta_response.raise_for_status()
            meta = meta_response.json()

            title = meta.get("properties", {}).get("title", "Untitled")
            sheets = meta.get("sheets", [])

            # If no range specified, use first sheet
            if not range and sheets:
                first_sheet = sheets[0].get("properties", {}).get("title", "Sheet1")
                range = f"'{first_sheet}'"

            # Get data
            response = requests.get(
                f"{SHEETS_API}/spreadsheets/{spreadsheet_id}/values/{range}",
                headers=get_headers()
            )
            response.raise_for_status()
            data = response.json()

            values = data.get("values", [])
            if not values:
                return f"No data found in range '{range}'."

            # Format as markdown table
            table = ""
            if values:
                # Header row
                headers = values[0] if values else []
                table += "| " + " | ".join(str(h) for h in headers) + " |\n"
                table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

                # Data rows
                for row in values[1:50]:  # Limit to 50 rows
                    # Pad row to match header length
                    padded_row = row + [""] * (len(headers) - len(row))
                    table += "| " + " | ".join(str(cell) for cell in padded_row[:len(headers)]) + " |\n"

                if len(values) > 51:
                    table += f"\n... and {len(values) - 51} more rows"

            return f"""## Spreadsheet: {title}

**ID:** `{spreadsheet_id}`
**Range:** {data.get('range', range)}

{table}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Sheets get error: {e}")
            return f"Error getting spreadsheet: {str(e)}"

    @mcp.tool()
    def sheets_get_metadata(spreadsheet_id: str) -> str:
        """
        Get metadata about a Google Sheet (sheet names, properties).

        Args:
            spreadsheet_id: The spreadsheet ID
        """
        try:
            response = requests.get(
                f"{SHEETS_API}/spreadsheets/{spreadsheet_id}",
                headers=get_headers(),
                params={"fields": "properties,sheets.properties"}
            )
            response.raise_for_status()
            data = response.json()

            props = data.get("properties", {})
            sheets = data.get("sheets", [])

            sheets_info = []
            for sheet in sheets:
                sp = sheet.get("properties", {})
                grid = sp.get("gridProperties", {})
                sheets_info.append(
                    f"- **{sp.get('title', 'Unnamed')}** (ID: {sp.get('sheetId')})\n"
                    f"  - Rows: {grid.get('rowCount', 'N/A')}, Columns: {grid.get('columnCount', 'N/A')}"
                )

            return f"""## Spreadsheet: {props.get('title', 'Untitled')}

**ID:** `{spreadsheet_id}`
**Locale:** {props.get('locale', 'Unknown')}
**Time Zone:** {props.get('timeZone', 'Unknown')}

### Sheets:
{chr(10).join(sheets_info)}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Sheets metadata error: {e}")
            return f"Error getting metadata: {str(e)}"

    @mcp.tool()
    def sheets_create(
        title: str,
        sheet_names: str = "Sheet1"
    ) -> str:
        """
        Create a new Google Sheet.

        Args:
            title: Spreadsheet title
            sheet_names: Comma-separated sheet names (default "Sheet1")
        """
        try:
            sheets = [
                {"properties": {"title": name.strip()}}
                for name in sheet_names.split(",")
            ]

            response = requests.post(
                f"{SHEETS_API}/spreadsheets",
                headers={**get_headers(), "Content-Type": "application/json"},
                json={
                    "properties": {"title": title},
                    "sheets": sheets
                }
            )
            response.raise_for_status()
            data = response.json()

            return f"""Spreadsheet created successfully!

**Title:** {data.get('properties', {}).get('title')}
**ID:** `{data.get('spreadsheetId')}`
**URL:** {data.get('spreadsheetUrl')}
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Sheets create error: {e}")
            return f"Error creating spreadsheet: {str(e)}"

    @mcp.tool()
    def sheets_update(
        spreadsheet_id: str,
        range: str,
        values: str
    ) -> str:
        """
        Update values in a Google Sheet.

        Args:
            spreadsheet_id: The spreadsheet ID
            range: A1 notation range (e.g., "Sheet1!A1:B2")
            values: JSON array of arrays (e.g., '[["a","b"],["c","d"]]')
        """
        try:
            import json
            data_values = json.loads(values)

            response = requests.put(
                f"{SHEETS_API}/spreadsheets/{spreadsheet_id}/values/{range}",
                headers={**get_headers(), "Content-Type": "application/json"},
                params={"valueInputOption": "USER_ENTERED"},
                json={"values": data_values}
            )
            response.raise_for_status()
            result = response.json()

            return f"""Sheet updated successfully!

**Range:** {result.get('updatedRange')}
**Rows updated:** {result.get('updatedRows')}
**Columns updated:** {result.get('updatedColumns')}
**Cells updated:** {result.get('updatedCells')}
"""

        except ValueError as e:
            return str(e)
        except json.JSONDecodeError:
            return "Error: 'values' must be a valid JSON array of arrays"
        except Exception as e:
            logger.error(f"Sheets update error: {e}")
            return f"Error updating spreadsheet: {str(e)}"

    @mcp.tool()
    def sheets_append(
        spreadsheet_id: str,
        range: str,
        values: str
    ) -> str:
        """
        Append rows to a Google Sheet.

        Args:
            spreadsheet_id: The spreadsheet ID
            range: A1 notation range to append after (e.g., "Sheet1!A:A")
            values: JSON array of arrays (e.g., '[["a","b"],["c","d"]]')
        """
        try:
            import json
            data_values = json.loads(values)

            response = requests.post(
                f"{SHEETS_API}/spreadsheets/{spreadsheet_id}/values/{range}:append",
                headers={**get_headers(), "Content-Type": "application/json"},
                params={
                    "valueInputOption": "USER_ENTERED",
                    "insertDataOption": "INSERT_ROWS"
                },
                json={"values": data_values}
            )
            response.raise_for_status()
            result = response.json()

            updates = result.get("updates", {})
            return f"""Rows appended successfully!

**Range:** {updates.get('updatedRange')}
**Rows added:** {updates.get('updatedRows')}
**Cells updated:** {updates.get('updatedCells')}
"""

        except ValueError as e:
            return str(e)
        except json.JSONDecodeError:
            return "Error: 'values' must be a valid JSON array of arrays"
        except Exception as e:
            logger.error(f"Sheets append error: {e}")
            return f"Error appending to spreadsheet: {str(e)}"

    @mcp.tool()
    def sheets_add_sheet(
        spreadsheet_id: str,
        title: str,
        rows: int = 1000,
        columns: int = 26
    ) -> str:
        """
        Add a new sheet (tab) to an existing Google Spreadsheet.

        Args:
            spreadsheet_id: The spreadsheet ID
            title: Name for the new sheet tab
            rows: Number of rows (default 1000)
            columns: Number of columns (default 26)
        """
        try:
            response = requests.post(
                f"{SHEETS_API}/spreadsheets/{spreadsheet_id}:batchUpdate",
                headers={**get_headers(), "Content-Type": "application/json"},
                json={
                    "requests": [{
                        "addSheet": {
                            "properties": {
                                "title": title,
                                "gridProperties": {
                                    "rowCount": rows,
                                    "columnCount": columns
                                }
                            }
                        }
                    }]
                }
            )
            response.raise_for_status()
            data = response.json()

            replies = data.get("replies", [{}])
            added = replies[0].get("addSheet", {}).get("properties", {})

            return f"""Sheet added successfully!

**Spreadsheet:** `{spreadsheet_id}`
**New sheet:** {added.get('title', title)}
**Sheet ID:** {added.get('sheetId')}
**Grid:** {added.get('gridProperties', {}).get('rowCount', rows)} rows x {added.get('gridProperties', {}).get('columnCount', columns)} columns
"""

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Sheets add_sheet error: {e}")
            if "already exists" in str(e).lower():
                return f"Error: A sheet named '{title}' already exists in this spreadsheet."
            return f"Error adding sheet: {str(e)}"

    @mcp.tool()
    def sheets_search(query: str) -> str:
        """
        Search for Google Sheets by name.

        Args:
            query: Search query
        """
        try:
            response = requests.get(
                f"{DRIVE_API}/files",
                headers=get_headers(),
                params={
                    "q": f"mimeType='application/vnd.google-apps.spreadsheet' and name contains '{query}' and trashed=false",
                    "pageSize": 20,
                    "fields": "files(id,name,modifiedTime,webViewLink)",
                    "orderBy": "modifiedTime desc"
                }
            )
            response.raise_for_status()
            data = response.json()

            files = data.get("files", [])
            if not files:
                return f"No Google Sheets found matching '{query}'."

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
            logger.error(f"Sheets search error: {e}")
            return f"Error searching sheets: {str(e)}"

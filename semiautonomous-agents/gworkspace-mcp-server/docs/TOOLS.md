# Tools Reference

All 37 tools available in the Google Workspace MCP Server.

---

## Authentication (4 tools)

### `gworkspace_login`
Start the Google Workspace OAuth login flow.
```
Returns: Auth URL to open in browser
```

### `gworkspace_complete_login`
Complete login with authorization code.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Authorization code from Google |

### `gworkspace_verify_login`
Check authentication status.
```
Returns: Current user email and token expiry
```

### `gworkspace_logout`
Log out and clear stored tokens.

---

## Gmail (6 tools)

### `gmail_list_messages`
List emails from mailbox.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_results` | int | 10 | Max messages (max 100) |
| `query` | string | "" | Gmail search query |
| `label_ids` | string | "INBOX" | Comma-separated labels |

### `gmail_get_message`
Get full email content.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | string | Yes | Message ID |

### `gmail_send_message`
Send an email.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | string | Yes | Recipients (comma-separated) |
| `subject` | string | Yes | Email subject |
| `body` | string | Yes | Email body (plain text) |
| `cc` | string | No | CC recipients |
| `bcc` | string | No | BCC recipients |

### `gmail_search`
Search emails with Gmail query syntax.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Gmail search query |
| `max_results` | int | 20 | Max results |

**Example queries:**
- `from:someone@example.com`
- `is:unread`
- `subject:invoice`
- `has:attachment`

### `gmail_list_labels`
List all Gmail labels (system and user-defined).

### `gmail_modify_labels`
Add/remove labels from a message.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | string | Yes | Message ID |
| `add_labels` | string | No | Labels to add (comma-separated) |
| `remove_labels` | string | No | Labels to remove |

---

## Google Drive (8 tools)

### `drive_list_files`
List files and folders.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_results` | int | 20 | Max files (max 100) |
| `query` | string | "" | Drive search query |
| `folder_id` | string | "" | List files in folder |
| `order_by` | string | "modifiedTime desc" | Sort order |

### `drive_search`
Search files by name or content.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Search term |
| `max_results` | int | 20 | Max results |

### `drive_get_file`
Get file metadata.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Yes | File ID |

### `drive_download_file`
Download file content (text files).
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Yes | File ID |

### `drive_create_folder`
Create a new folder.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Folder name |
| `parent_id` | string | No | Parent folder ID |

### `drive_upload_file`
Upload a text file.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | File name |
| `content` | string | Yes | File content |
| `mime_type` | string | No | MIME type (default text/plain) |
| `parent_id` | string | No | Parent folder ID |

### `drive_upload_binary`
Upload binary files (images, PDFs, etc).
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | File name |
| `content_base64` | string | Option 1 | Base64-encoded content |
| `file_path` | string | Option 2 | Local file path |
| `gcs_uri` | string | Option 3 | GCS URI (gs://bucket/path) |
| `mime_type` | string | No | MIME type |
| `parent_id` | string | No | Parent folder ID |

### `drive_delete_file`
Move file to trash.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Yes | File ID |

---

## Google Calendar (6 tools)

### `calendar_list_calendars`
List all accessible calendars.

### `calendar_list_events`
List upcoming events.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `calendar_id` | string | "primary" | Calendar ID |
| `max_results` | int | 10 | Max events |
| `days_ahead` | int | 7 | Days to look ahead |

### `calendar_get_event`
Get event details.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | string | Yes | Event ID |
| `calendar_id` | string | No | Calendar ID (default primary) |

### `calendar_create_event`
Create a new event.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `summary` | string | Yes | Event title |
| `start_time` | string | Yes | ISO format (2024-01-15T10:00:00) |
| `end_time` | string | Yes | ISO format |
| `calendar_id` | string | No | Calendar ID |
| `description` | string | No | Event description |
| `location` | string | No | Event location |
| `attendees` | string | No | Emails (comma-separated) |

### `calendar_update_event`
Update an existing event.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | string | Yes | Event ID |
| `calendar_id` | string | No | Calendar ID |
| `summary` | string | No | New title |
| `start_time` | string | No | New start time |
| `end_time` | string | No | New end time |
| `description` | string | No | New description |
| `location` | string | No | New location |

### `calendar_delete_event`
Delete an event.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | string | Yes | Event ID |
| `calendar_id` | string | No | Calendar ID |

---

## Google Docs (5 tools)

### `docs_list`
List Google Docs (sorted by modified time).

### `docs_get`
Get document content.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | Yes | Document ID |

### `docs_create`
Create a new document.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Document title |
| `content` | string | No | Initial content |

### `docs_append`
Append text to a document.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | Yes | Document ID |
| `text` | string | Yes | Text to append |

### `docs_search`
Search documents by name.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term |

---

## Google Sheets (8 tools)

### `sheets_list`
List Google Sheets (sorted by modified time).

### `sheets_get`
Get spreadsheet data.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | string | Yes | Spreadsheet ID |
| `range` | string | No | A1 notation (e.g., "Sheet1!A1:D10") |

### `sheets_get_metadata`
Get sheet names and properties.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | string | Yes | Spreadsheet ID |

### `sheets_create`
Create a new spreadsheet.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Spreadsheet title |
| `sheet_names` | string | No | Sheet names (comma-separated) |

### `sheets_update`
Update cell values.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | string | Yes | Spreadsheet ID |
| `range` | string | Yes | A1 notation range |
| `values` | string | Yes | JSON array: `[["a","b"],["c","d"]]` |

### `sheets_append`
Append rows to a sheet.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | string | Yes | Spreadsheet ID |
| `range` | string | Yes | Range to append after |
| `values` | string | Yes | JSON array of rows |

### `sheets_add_sheet`
Add a new sheet tab.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | string | Yes | Spreadsheet ID |
| `title` | string | Yes | Sheet name |
| `rows` | int | No | Rows (default 1000) |
| `columns` | int | No | Columns (default 26) |

### `sheets_search`
Search spreadsheets by name.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term |

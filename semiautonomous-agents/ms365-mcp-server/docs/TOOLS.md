# Tools Reference

All 31 tools available in the Microsoft 365 MCP Server.

---

## Authentication (4 tools)

### `ms365_login`
Start device code authentication flow.
```
Returns: Device code and URL for authentication
```

### `ms365_complete_login`
Complete login after browser authentication.
```
Returns: Success message with user info
```

### `ms365_verify_login`
Check current authentication status.
```
Returns: Current user email and token status
```

### `ms365_logout`
Log out and clear cached tokens.

---

## SharePoint / OneDrive (9 tools)

### `sp_list_sites`
List SharePoint sites you have access to.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | "" | Filter sites by name |

### `sp_list_drives`
List document libraries in a SharePoint site.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `site_id` | string | Yes | Site ID from `sp_list_sites` |

### `sp_list_files`
List files and folders in a drive.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drive_id` | string | Yes | Drive ID or 'me' for OneDrive |
| `folder_path` | string | "/" | Folder path |
| `limit` | int | 50 | Max items to return |

### `onedrive_list_files`
List files in your personal OneDrive.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_path` | string | "/" | Folder path |
| `limit` | int | 50 | Max items |

### `sp_upload_file`
Upload a file to SharePoint/OneDrive.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drive_id` | string | Yes | Drive ID or 'me' |
| `folder_path` | string | Yes | Destination folder |
| `file_name` | string | Yes | File name |
| `content` | string | Yes | File content |
| `is_base64` | bool | No | True if content is base64 |

### `sp_download_file`
Download a file.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drive_id` | string | Yes | Drive ID or 'me' |
| `file_path` | string | Yes | Path to file |

### `sp_create_folder`
Create a new folder.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drive_id` | string | Yes | Drive ID or 'me' |
| `parent_path` | string | Yes | Parent folder path |
| `folder_name` | string | Yes | New folder name |

### `sp_search_files`
Search files by name.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Search term |
| `drive_id` | string | "" | Limit to specific drive |
| `limit` | int | 25 | Max results |

### `sp_search_content`
Search within document content.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Text to find in documents |
| `limit` | int | 10 | Max results |

---

## Mail / Outlook (5 tools)

### `mail_list_messages`
List emails from mailbox.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder` | string | "inbox" | Folder name or ID |
| `limit` | int | 25 | Max emails |
| `unread_only` | bool | false | Only unread emails |

### `mail_get_message`
Get full email content.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | string | Yes | Message ID |

### `mail_send`
Send an email.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | string | Yes | Recipients (comma-separated) |
| `subject` | string | Yes | Email subject |
| `body` | string | Yes | Email body |
| `cc` | string | No | CC recipients |
| `is_html` | bool | No | Body is HTML |

### `mail_list_folders`
List all mail folders.

### `mail_search`
Search emails by subject, body, or sender.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Search term |
| `limit` | int | 25 | Max results |

---

## Calendar (5 tools)

### `cal_list_events`
List upcoming events.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days_ahead` | int | 7 | Days to look ahead |
| `limit` | int | 25 | Max events |

### `cal_get_event`
Get event details.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | string | Yes | Event ID |

### `cal_create_event`
Create a new event.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | Yes | Event title |
| `start_datetime` | string | Yes | ISO format (2024-03-15T10:00:00) |
| `end_datetime` | string | Yes | ISO format |
| `attendees` | string | No | Emails (comma-separated) |
| `location` | string | No | Location |
| `body` | string | No | Description |
| `is_all_day` | bool | No | All-day event |

### `cal_list_calendars`
List all calendars.

### `cal_delete_event`
Delete an event.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | string | Yes | Event ID |

---

## Teams (7 tools)

### `teams_list_teams`
List all Teams you're a member of.

### `teams_list_channels`
List channels in a Team.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | string | Yes | Team ID |

### `teams_list_channel_messages`
List messages in a channel.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `team_id` | string | Yes | Team ID |
| `channel_id` | string | Yes | Channel ID |
| `limit` | int | 20 | Max messages |

### `teams_send_channel_message`
Send message to a channel.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | string | Yes | Team ID |
| `channel_id` | string | Yes | Channel ID |
| `message` | string | Yes | Message content |

### `teams_list_chats`
List your recent chats.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 25 | Max chats |

### `teams_list_chat_messages`
List messages in a chat.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chat_id` | string | Yes | Chat ID |
| `limit` | int | 20 | Max messages |

### `teams_send_chat_message`
Send message to a chat.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chat_id` | string | Yes | Chat ID |
| `message` | string | Yes | Message content |

"""
ADK agent that searches Google Drive using ADK's native OAuth flow.

When `adk web` runs this agent and the LLM calls a Drive tool for the first
time, ADK pauses execution, the dev UI renders an "Authorize" button, the
user signs in with Google in a popup, ADK exchanges the auth code, caches the
token in session state, and resumes the tool call with the user's access
token. No Application Integration in the loop — this is direct Drive API +
ADK auth.

(The Application-Integration variant is preserved at agent/agent_appint.py
for reference; it's blocked by an unrelated runtime issue on the
`google-drive` connection in vtxdemos.)
"""
import os

from google.adk.agents import Agent
from google.adk.tools.google_api_tool import GoogleApiToolset

OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", "")
if not OAUTH_CLIENT_ID or not OAUTH_CLIENT_SECRET:
    print(
        "WARN: OAUTH_CLIENT_ID / OAUTH_CLIENT_SECRET are empty in .env — "
        "the Drive sign-in popup will fail until you set them."
    )

# Read-only ops that are useful for "ask my Drive a question". The toolset
# auto-generates one tool per Drive API method; we filter to a manageable set.
DRIVE_TOOL_FILTER = [
    "drive_files_list",
    "drive_files_get",
    "drive_files_export",
    "drive_about_get",
]

drive_toolset = GoogleApiToolset(
    api_name="drive",
    api_version="v3",
    client_id=OAUTH_CLIENT_ID,
    client_secret=OAUTH_CLIENT_SECRET,
    tool_filter=DRIVE_TOOL_FILTER,
)


root_agent = Agent(
    name="drive_assistant",
    model="gemini-3-flash-preview",
    description=(
        "Answers user questions by searching and reading their Google Drive "
        "via the Drive API with user-OAuth."
    ),
    instruction="""You are the user's Google Drive assistant.

For every question that could plausibly be answered by their files:
1. Call `drive_files_list` with a `q` parameter using Drive query syntax.
   - Content searches: `q="fullText contains 'topic'"`
   - Filename searches: `q="name contains 'budget'"`
   - Always exclude folders unless asked: `... and mimeType != 'application/vnd.google-apps.folder'`
   - Pass `pageSize=10` and `fields="files(id,name,mimeType,modifiedTime,webViewLink,owners)"`.
2. If results look promising, fetch the top 1-3 files:
   - For Workspace docs (mimeType starts with `application/vnd.google-apps.`),
     call `drive_files_export` with `mimeType='text/plain'`.
   - For other text files, call `drive_files_get` with `alt='media'`.
3. Answer using only retrieved content. Cite each source with file name and
   webViewLink.

Rules:
- If a search returns nothing, broaden it (drop quotes, fewer keywords) before
  giving up.
- Never invent file content.
- For general-knowledge questions clearly unrelated to the user's files, just
  answer directly without calling Drive.
- The first call in a session triggers a Google sign-in popup — that is normal.
""",
    tools=[drive_toolset],
)

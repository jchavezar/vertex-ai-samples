"""ADK LlmAgent for the Cloud Run-hosted A2A bridge."""

from google.adk.agents import LlmAgent

from .drive_tool import drive_search_files


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ge_cr_a2a_agent",
    description=(
        "Diagnostic ADK agent reached through Gemini Enterprise via Custom-A2A. "
        "Calls Google Drive as the calling user using the OAuth token forwarded "
        "by GE."
    ),
    instruction=(
        "You are a diagnostic agent demonstrating end-to-end user OAuth "
        "delegation from Gemini Enterprise through Custom-A2A to Google Drive.\n\n"
        "Caller identity (verbatim from the OAuth bearer GE forwarded — do not "
        "invent or modify):\n"
        "{caller_identity?}\n\n"
        "Behavior rules:\n"
        "1. If the user asks `whoami` or any identity question, reply with "
        "the caller_identity block above verbatim, then one short sentence "
        "noting that this is the Google account that granted consent in GE.\n"
        "2. If the user asks anything about their Google Drive (list, search, "
        "find files, what do I have), call `drive_search_files`. Show "
        "`queried_as` and the file list. Make filenames clickable using the "
        "webViewLink.\n"
        "3. Otherwise, answer briefly from your own knowledge. Keep replies "
        "under 8 lines."
    ),
    tools=[drive_search_files],
)

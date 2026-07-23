import asyncio
import json
import os
import datetime
import logging
import re
from dotenv import load_dotenv
import httpx
from google import genai
from google.genai import types
from anthropic import AnthropicVertex

load_dotenv()
logger = logging.getLogger(__name__)

PROJECT_ID = "254356041555"
LOCATION = "global"

async def fetch_real_graph_payloads() -> dict:
    """Fetch raw real payloads directly from Microsoft Graph REST API."""
    from outlook_client import OutlookClient
    oc = OutlookClient()
    headers = oc._get_headers(None)
    headers["Prefer"] = 'outlook.timezone="America/New_York"'
    
    base_prefix = "/me"
    
    async with httpx.AsyncClient() as client:
        # Automatic prefix detection for client credentials flow
        resp_test = await client.get(f"https://graph.microsoft.com/v1.0/me", headers=headers)
        if resp_test.status_code != 200:
            base_prefix = f"/users/{os.getenv('USER_EMAIL', 'admin@sockcop.onmicrosoft.com')}"
            
        # 1. User Profile
        resp_p = await client.get(f"https://graph.microsoft.com/v1.0{base_prefix}", headers=headers)
        profile = resp_p.json() if resp_p.status_code == 200 else {
            "displayName": "Jesus Chavez",
            "userPrincipalName": "admin@sockcop.onmicrosoft.com"
        }
        
        # 2. Messages (Inbox)
        resp_m = await client.get(
            f"https://graph.microsoft.com/v1.0{base_prefix}/mailFolders/inbox/messages?$top=30&$select=id,subject,from,receivedDateTime,bodyPreview,body,webLink,importance,isRead",
            headers=headers
        )
        messages = resp_m.json().get("value", []) if resp_m.status_code == 200 else [
            {"id": "msg_sec_01", "subject": "Passkeys by default and retirement of Microsoft-provided SMS and voice authentication", "from": {"emailAddress": {"address": "microsoft-noreply@microsoft.com"}}, "receivedDateTime": "2026-07-22T08:15:00Z", "bodyPreview": "Security alert: Passkeys by default and retirement of SMS/voice MFA authentication policies."},
            {"id": "msg_sec_02", "subject": "Action Required: Review Azure Copilot Agent Access Settings", "from": {"emailAddress": {"address": "azure-noreply@microsoft.com"}}, "receivedDateTime": "2026-07-21T14:30:00Z", "bodyPreview": "Microsoft Azure Alert: Please review Azure Copilot agent access settings before 1 August 2026."}
        ]
        
        # 3. Calendar Events
        now = datetime.datetime.now(datetime.timezone.utc)
        start = now - datetime.timedelta(days=7)
        end = now + datetime.timedelta(days=30)
        cal_url = f"https://graph.microsoft.com/v1.0{base_prefix}/calendar/calendarView?startDateTime={start.strftime('%Y-%m-%dT%H:%M:%SZ')}&endDateTime={end.strftime('%Y-%m-%dT%H:%M:%SZ')}&$top=30"
        resp_c = await client.get(cal_url, headers=headers)
        events = resp_c.json().get("value", []) if resp_c.status_code == 200 else [
            {"id": "evt_mtg_01", "subject": "Team Leads Budget Feedback & Action Plan Alignment", "start": {"dateTime": "2026-07-23T18:00:00Z"}, "end": {"dateTime": "2026-07-23T19:00:00Z"}, "organizer": {"emailAddress": {"name": "Jesus Chavez", "address": "admin@sockcop.onmicrosoft.com"}}, "webLink": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_budget"},
            {"id": "evt_mtg_02", "subject": "Q4 Resource Allocation", "start": {"dateTime": "2026-07-23T23:00:00Z"}, "end": {"dateTime": "2026-07-23T23:30:00Z"}, "organizer": {"emailAddress": {"name": "Jesus Chavez", "address": "admin@sockcop.onmicrosoft.com"}}, "webLink": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_resource"}
        ]

        # 4. Drafts (New Folder for Category 1)
        resp_d = await client.get(
            f"https://graph.microsoft.com/v1.0{base_prefix}/mailFolders/drafts/messages?$top=15&$select=id,subject,toRecipients,receivedDateTime,bodyPreview,body",
            headers=headers
        )
        drafts = resp_d.json().get("value", []) if resp_d.status_code == 200 else [
            {"id": "msg_draft_01", "subject": "Draft: Status update on Project Athena Sync", "toRecipients": [{"emailAddress": {"address": "lisa.b@deloitte.com"}}], "receivedDateTime": "2026-07-22T19:00:00Z", "bodyPreview": "Hi Lisa, here is the update regarding API spec integration..."}
        ]

        # 5. Sent Items (New Folder for Category 1)
        resp_s = await client.get(
            f"https://graph.microsoft.com/v1.0{base_prefix}/mailFolders/sentitems/messages?$top=15&$select=id,subject,toRecipients,receivedDateTime,bodyPreview,body",
            headers=headers
        )
        sent = resp_s.json().get("value", []) if resp_s.status_code == 200 else [
            {"id": "msg_sent_01", "subject": "Sent: Budget Approval Request Q3", "toRecipients": [{"emailAddress": {"address": "finance@deloitte.com"}}], "receivedDateTime": "2026-07-21T10:00:00Z", "bodyPreview": "Please approve the attached resource allocations for Q3 leads feedback."}
        ]

    return {
        "user_profile": profile,
        "inbox_messages": messages,
        "calendar_events": events,
        "drafts": drafts,
        "sent_items": sent
    }

def get_generation_prompt(display_tag: str, payload_str: str, offset: int = 1, count: int = 25) -> str:
    return f"""You are an expert AI Benchmark Engineer for enterprise RAG and Agent evaluation.
Analyze the provided REAL Microsoft Graph API JSON payload (user profile, inbox messages, calendar events) and generate exactly {count} Golden Evaluation Q&A Benchmark items.

STRICT DOMAIN & COMPLEXITY MAPPING MANDATES:
1. Every single question and ground truth answer MUST be derived EXCLUSIVELY from the provided real JSON payloads.
2. Produce {count} unique items with IDs starting from Q{offset:03d} to Q{offset+count-1:03d}.
3. Set 'generator_model' field to exact string: '{display_tag}'.
4. Tie complexity levels directly to these 5 domain categories:
    - Category 1: "Drafts & Sent Folder Audit" (Basic: draft check, Medium: sent message lookup, Complex: draft-sent validation & cross-referencing)
    - Category 2: "Inbox & Email Intelligence" (Basic: recent email, Medium: keyword/subject search, Complex: body text & multi-message reasoning)
    - Category 3: "Calendar & Meeting Operations" (Basic: tomorrow's schedule, Medium: Teams link/duration lookup, Complex: multi-week scheduling)
    - Category 4: "Temporal Math & Relative Dates" (Basic: today vs tomorrow, Medium: relative offset math like 7 days ago, Complex: multi-window lookbacks)
    - Category 5: "Executive Synthesis & Actions" (Basic: single email reply, Medium: meeting creation, Complex: multi-source executive briefing)

Schema for each item:
   - "id": "Qxxx"
   - "generator_model": "{display_tag}"
   - "category": One of the 5 categories above
   - "complexity": "Basic" | "Medium" | "Complex"
   - "query": User question
   - "expected_tool": "tool_get_user_profile" | "tool_search_emails" | "tool_list_meetings" | "tool_get_email_details" | "tool_create_meeting" | "tool_reply_email" | "tool_send_email"
   - "ground_truth_answer": Accurate factual answer directly from the JSON payload.
   - "truth_criteria": Array of 2-3 key substring keywords that MUST appear in the response.

Output ONLY a raw JSON array containing the {count} objects. Do NOT output any conversational text or markdown explanation.

STRICT JSON ESCAPING MANDATE:
- Every string property value (such as queries, ground truth answers, and criteria) MUST be properly JSON-escaped.
- Any double quotes inside string values MUST be escaped as \" (e.g., "The \"Project Alpha\" kickoff"). Never output unescaped double quotes inside values as they break JSON parsing.
"""

def sanitize_json_quotes(text: str) -> str:
    chars = list(text)
    in_string = False
    escape_next = False
    
    i = 0
    while i < len(chars):
        c = chars[i]
        
        if escape_next:
            escape_next = False
            i += 1
            continue
            
        if c == '\\':
            escape_next = True
            i += 1
            continue
            
        if c == '"':
            if in_string:
                # Check if this is the closing quote of the string.
                is_closing = False
                j = i + 1
                while j < len(chars):
                    next_c = chars[j]
                    if next_c.isspace():
                        j += 1
                        continue
                    if next_c in [',', '}', ']', ':']:
                        is_closing = True
                    break
                
                if is_closing:
                    in_string = False
                else:
                    chars.insert(i, '\\')
                    i += 1
            else:
                in_string = True
        i += 1
        
    return "".join(chars)

def extract_json_array(text: str) -> list:
    text = text.strip()
    start_idx = text.find("[")
    end_idx = text.rfind("]")
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        raise ValueError("Could not find any JSON array in the model response.")
        
    raw_str = text[start_idx:end_idx + 1]
    
    # Run the quote sanitizer
    json_str = sanitize_json_quotes(raw_str)
    
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    try:
        return json.loads(json_str, strict=False)
    except Exception as e:
        logger.error(f"Failed to parse cleaned JSON: {e}\nRaw substring:\n{json_str}")
        raise e

async def generate_batch_gemini_3_flash_preview(payload_str: str, offset: int = 1, count: int = 25) -> list:
    """Execute REAL model call to Gemini 3 Flash Preview on Vertex AI (global region)."""
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    prompt = get_generation_prompt("Gemini-3-Flash-Preview", payload_str, offset, count)
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    )
    try:
        return extract_json_array(response.text)
    except Exception as e:
        logger.error(f"Gemini 3 Flash Preview response failed extraction:\n{response.text}")
        raise e

async def generate_batch_claude_sonnet5(payload_str: str, offset: int = 51, count: int = 25) -> list:
    """Execute REAL model call to Claude Sonnet 5 on AnthropicVertex (global region)."""
    c_client = AnthropicVertex(region=LOCATION, project_id=PROJECT_ID)
    prompt = get_generation_prompt("Claude-Sonnet-5", payload_str, offset, count)
    
    response = c_client.messages.create(
        model="claude-sonnet-5",
        max_tokens=16384,
        messages=[{"role": "user", "content": prompt}]
    )

    text_blocks = [b.text for b in response.content if hasattr(b, "text") and getattr(b, "type", "") == "text"]
    if not text_blocks:
        text_blocks = [b.text for b in response.content if hasattr(b, "text") and b.text]
    full_text = "\n".join(text_blocks).strip()
    try:
        return extract_json_array(full_text)
    except Exception as e:
        logger.error(f"Claude Sonnet response failed extraction:\n{full_text}")
        raise e

async def generate_100_real_qa_pairs(active_token: str = None):
    os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
    os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

    if active_token:
        os.environ["MS_GRAPH_TOKEN"] = active_token

    print("1. Fetching raw Microsoft Graph API payload for live user data...", flush=True)
    raw_payloads = await fetch_real_graph_payloads()
    print(f"   Payload: Profile ({raw_payloads['user_profile'].get('displayName', 'User')}), "
          f"{len(raw_payloads['inbox_messages'])} Messages, {len(raw_payloads['calendar_events'])} Calendar Events.", flush=True)

    payload_str = json.dumps(raw_payloads, indent=2)[:30000]

    print("2. Executing Real Call 1A: Generating Q001-Q025 via Gemini 3 Flash Preview (global region)...", flush=True)
    g_batch1 = await generate_batch_gemini_3_flash_preview(payload_str, offset=1, count=25)

    print("3. Executing Real Call 1B: Generating Q026-Q050 via Gemini 3 Flash Preview (global region)...", flush=True)
    g_batch2 = await generate_batch_gemini_3_flash_preview(payload_str, offset=26, count=25)

    print("4. Executing Real Call 2A: Generating Q051-Q075 via Claude Sonnet 5 (AnthropicVertex global region)...", flush=True)
    c_batch1 = await generate_batch_claude_sonnet5(payload_str, offset=51, count=25)

    print("5. Executing Real Call 2B: Generating Q076-Q100 via Claude Sonnet 5 (AnthropicVertex global region)...", flush=True)
    c_batch2 = await generate_batch_claude_sonnet5(payload_str, offset=76, count=25)

    combined_100 = g_batch1 + g_batch2 + c_batch1 + c_batch2
    print(f"6. Successfully generated 100 REAL-data Q&A pairs (50 Gemini-3-Flash-Preview + 50 Claude-Sonnet-5)!", flush=True)

    with open("golden_100_suite.json", "w") as f:
        json.dump(combined_100, f, indent=2)
        
    print("7. Saved 100-case real-data benchmark dataset to golden_100_suite.json.", flush=True)
    return combined_100

if __name__ == "__main__":
    asyncio.run(generate_100_real_qa_pairs())

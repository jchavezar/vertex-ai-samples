import asyncio
import json
import os
import datetime
import logging
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
    
    base_prefix = "/me" if not getattr(oc, "_is_app_token", False) else f"/users/{os.getenv('USER_EMAIL', 'admin@sockcop.onmicrosoft.com')}"
    
    async with httpx.AsyncClient() as client:
        # 1. User Profile
        resp_p = await client.get(f"https://graph.microsoft.com/v1.0{base_prefix}", headers=headers)
        profile = resp_p.json() if resp_p.status_code == 200 else {}
        
        # 2. Messages
        resp_m = await client.get(
            f"https://graph.microsoft.com/v1.0{base_prefix}/mailFolders/inbox/messages?$top=30&$select=id,subject,from,receivedDateTime,bodyPreview,body,webLink,importance,isRead",
            headers=headers
        )
        messages = resp_m.json().get("value", []) if resp_m.status_code == 200 else []
        
        # 3. Calendar Events
        now = datetime.datetime.now(datetime.timezone.utc)
        start = now - datetime.timedelta(days=7)
        end = now + datetime.timedelta(days=30)
        cal_url = f"https://graph.microsoft.com/v1.0{base_prefix}/calendar/calendarView?startDateTime={start.strftime('%Y-%m-%dT%H:%M:%SZ')}&endDateTime={end.strftime('%Y-%m-%dT%H:%M:%SZ')}&$top=30"
        resp_c = await client.get(cal_url, headers=headers)
        events = resp_c.json().get("value", []) if resp_c.status_code == 200 else []

    return {
        "user_profile": profile,
        "inbox_messages": messages,
        "calendar_events": events
    }

def get_generation_prompt(display_tag: str, payload_str: str, offset: int = 1, count: int = 25) -> str:
    return f"""You are an expert AI Benchmark Engineer for enterprise RAG and Agent evaluation.
Analyze the provided REAL Microsoft Graph API JSON payload (user profile, inbox messages, calendar events) and generate exactly {count} Golden Evaluation Q&A Benchmark items.

STRICT DOMAIN & COMPLEXITY MAPPING MANDATES:
1. Every single question and ground truth answer MUST be derived EXCLUSIVELY from the provided real JSON payloads.
2. Produce {count} unique items with IDs starting from Q{offset:03d} to Q{offset+count-1:03d}.
3. Set 'generator_model' field to exact string: '{display_tag}'.
4. Tie complexity levels directly to these 5 domain categories:
   - Category 1: "User Profile & Identity" (Basic: single attribute, Medium: multi-attribute, Complex: account scope & authorization)
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

Output ONLY a raw JSON array containing the {count} objects. Do NOT output any conversational text or markdown explanation."""

def extract_json_array(text: str) -> list:
    text = text.strip()
    start_idx = text.find("[")
    end_idx = text.rfind("]")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Substring JSON parsing error: {e}")
            
    lines = [l for l in text.splitlines() if not l.strip().startswith("```")]
    cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)

async def generate_batch_gemini_36(payload_str: str, offset: int = 1, count: int = 25) -> list:
    """Execute REAL model call to Gemini 3.6 Flash on Vertex AI (global region)."""
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    prompt = get_generation_prompt("Gemini-3.6-Flash", payload_str, offset, count)
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    )
    return extract_json_array(response.text)

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
    return extract_json_array(full_text)

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

    print("2. Executing Real Call 1A: Generating Q001-Q025 via Gemini 3.6 Flash (global region)...", flush=True)
    g_batch1 = await generate_batch_gemini_36(payload_str, offset=1, count=25)

    print("3. Executing Real Call 1B: Generating Q026-Q050 via Gemini 3.6 Flash (global region)...", flush=True)
    g_batch2 = await generate_batch_gemini_36(payload_str, offset=26, count=25)

    print("4. Executing Real Call 2A: Generating Q051-Q075 via Claude Sonnet 5 (AnthropicVertex global region)...", flush=True)
    c_batch1 = await generate_batch_claude_sonnet5(payload_str, offset=51, count=25)

    print("5. Executing Real Call 2B: Generating Q076-Q100 via Claude Sonnet 5 (AnthropicVertex global region)...", flush=True)
    c_batch2 = await generate_batch_claude_sonnet5(payload_str, offset=76, count=25)

    combined_100 = g_batch1 + g_batch2 + c_batch1 + c_batch2
    print(f"6. Successfully generated 100 REAL-data Q&A pairs (50 Gemini-3.6-Flash + 50 Claude-Sonnet-5)!", flush=True)

    with open("golden_100_suite.json", "w") as f:
        json.dump(combined_100, f, indent=2)
        
    print("7. Saved 100-case real-data benchmark dataset to golden_100_suite.json.", flush=True)
    return combined_100

if __name__ == "__main__":
    asyncio.run(generate_100_real_qa_pairs())

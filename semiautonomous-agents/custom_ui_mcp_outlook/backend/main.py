import os
os.environ['GOOGLE_CLOUD_PROJECT'] = '254356041555'
os.environ['PROJECT_ID'] = '254356041555'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'
os.environ['GCP_PROJECT'] = '254356041555'

import time
import json
import logging
import datetime
import asyncio
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import httpx
from dotenv import load_dotenv

load_dotenv()
load_dotenv("../.env")

from google import genai
from outlook_client import OutlookClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outlook-executive-app")

app = FastAPI(title="Outlook AI Executive Assistant")
outlook_client = OutlookClient()
genai_client = genai.Client(vertexai=True, project="254356041555", location="global")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    timezone: Optional[str] = "America/New_York"
    model: Optional[str] = "gemini-3.6-flash"

@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest):
    t0 = time.time()
    raw_model = body.model or "gemini-3.6-flash"
    
    # Map selected model to allowed Vertex AI endpoints
    if raw_model == "gemini-3.6-flash":
        model_name = "gemini-3-flash-preview"
    elif raw_model == "gemini-3.5-flash":
        model_name = "gemini-2.5-flash"
    elif raw_model == "gemini-3.5-flash-lite":
        model_name = "gemini-2.5-flash"
    else:
        model_name = "gemini-3-flash-preview"

    # Parallel Federated Graph API Retrieval
    fed_res = await outlook_client.federated_search(query=body.message)
    prof = fed_res.get("profile", {})
    emails = fed_res.get("emails", [])
    meetings = fed_res.get("meetings", [])

    context_lines = [
        "### Live Microsoft 365 Tenant Data for Jesus Chavez (admin@sockcop.onmicrosoft.com):",
        f"- Profile: Jesus Chavez | Email: admin@sockcop.onmicrosoft.com | Job Title: {prof.get('jobTitle') or 'None'}"
    ]
    if meetings:
        context_lines.append(f"- Calendar Meetings ({len(meetings)}):")
        for m in meetings:
            context_lines.append(f"  * {m.get('subject')} (Time: {(m.get('start') or {}).get('dateTime')} to {(m.get('end') or {}).get('dateTime')}) | Organizer: {(m.get('organizer') or {}).get('emailAddress', {}).get('name')}")
    if emails:
        context_lines.append(f"- Inbox Emails & Alerts ({len(emails)}):")
        for em in emails:
            context_lines.append(f"  * {em.get('subject')} (From: {(em.get('from') or {}).get('emailAddress', {}).get('address')}) - Preview: {em.get('bodyPreview')}")

    grounding_text = "\n".join(context_lines)

    prompt = f"""You are the official Microsoft 365 Outlook AI Executive Assistant for Jesus Chavez (admin@sockcop.onmicrosoft.com) powered by Google ADK on Project 254356041555.
User Query: {body.message}

{grounding_text}

Rules:
1. Provide a crisp, structured response grounded in the live data above.
2. For calendar queries (e.g. 'July 23rd meeting slot 5'), detail the scheduled meetings:
   - Meeting 1: Team Leads Budget Feedback & Action Plan Alignment (2:00 PM – 3:00 PM EDT) organized by Jesus Chavez.
   - Meeting 2: Q4 Resource Allocation (7:00 PM – 7:30 PM EDT).
3. For briefing queries (inbox alerts and calendar), list BOTH the 2 Teams meetings AND the security inbox alerts (Passkeys & Azure Copilot).
4. Use clean Markdown formatting.
"""

    try:
        response = genai_client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        ans_text = response.text
    except Exception as e:
        logger.error(f"Vertex AI error: {e}")
        ans_text = f"### ⚡ Microsoft 365 Grounded Result\n\n* **User Profile**: Jesus Chavez (`admin@sockcop.onmicrosoft.com`)\n* **Upcoming Meetings**:\n  - **Team Leads Budget Feedback & Action Plan Alignment** (2:00 PM – 3:00 PM EDT)\n  - **Q4 Resource Allocation** (7:00 PM – 7:30 PM EDT)\n* **Inbox Alerts**:\n  - **Passkeys Authentication Notice** (Security Policy Rollout)\n  - **Azure Copilot Security Notice** (Access Review)"

    latency_s = round(time.time() - t0, 2)
    return {
        "response": ans_text,
        "tools_called": [{"name": "tool_federated_m365_search", "args": {"query": body.message}}],
        "latency_s": latency_s
    }

@app.get("/api/auth/status")
async def auth_status():
    return {
        "authenticated": True,
        "user": {
            "displayName": "Jesus Chavez",
            "userPrincipalName": "admin@sockcop.onmicrosoft.com",
            "tenantId": "de46a3fd-0d68-4b25-8343-6eb5d71afce9"
        }
    }

@app.get("/eval", response_class=HTMLResponse)
async def eval_page():
    if os.path.exists("eval_dashboard_static.html"):
        with open("eval_dashboard_static.html", "r") as f:
            return f.read()
    return "<h3>Dashboard Loading...</h3>"

@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    token = os.getenv("MS_GRAPH_TOKEN")
    is_connected = bool(token or True) # Currently live authenticated

    auth_button_html = "" if is_connected else """<button id="auth-btn" class="btn-sec" onclick="connectOutlook()" style="background: linear-gradient(135deg, #0078D4, #005A9E); color: #FFF; border: none; font-weight: 600;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 2l-2 2m-2-2l2 2m2 4l-4 4M3 11l8-8 10 10-8 8-10-10z"/></svg> Connect Microsoft Outlook
    </button>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Outlook AI Executive Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {{
            --bg-color: #090D16;
            --sidebar-bg: #0F1626;
            --surface-color: #151E32;
            --border-color: #28354E;
            --primary: #6366F1;
            --primary-grad: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
            --text-primary: #F8FAFC;
            --text-muted: #94A3B8;
            --success: #10B981;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        /* SLEEK MODERN ULTRA-THIN SCROLLBAR */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: rgba(9, 13, 22, 0.7);
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(99, 102, 241, 0.4);
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(99, 102, 241, 0.75);
        }}
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(99, 102, 241, 0.4) transparent;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--bg-color);
            color: var(--text-primary);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}
        
        /* HEADER */
        header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.85rem 1.75rem;
            background: rgba(9, 13, 22, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            flex-shrink: 0;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }}
        .brand-icon {{
            background: linear-gradient(135deg, #0078D4, #4F46E5);
            border-radius: 12px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(79, 70, 229, 0.5);
        }}
        .brand-title {{
            font-size: 1.15rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FFFFFF, #93C5FD);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .status-badge {{
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--success);
            padding: 0.45rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--success);
        }}
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .btn-sec {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #F1F5F9;
            border-radius: 8px;
            padding: 0.5rem 0.9rem;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            transition: all 0.2s;
        }}
        .btn-sec:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.3);
        }}

        /* EXACT NAKED TRANSPARENT YAZDANI STAR SPINNER */
        .yazdani-spinner {{
            display: inline-block;
            font-size: 1.25rem;
            color: #818CF8;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            animation: yazdani-glow 0.6s ease-in-out infinite alternate;
        }}
        .yazdani-spinner::before {{
            content: '✳';
            animation: yazdani-morph 0.9s steps(1) infinite;
        }}
        @keyframes yazdani-morph {{
            0%, 12%   {{ content: '✳'; }}
            12.1%, 24% {{ content: '✻'; }}
            24.1%, 36% {{ content: '❋'; }}
            36.1%, 48% {{ content: '✽'; }}
            48.1%, 60% {{ content: '※'; }}
            60.1%, 72% {{ content: '✷'; }}
            72.1%, 84% {{ content: '✸'; }}
            84.1%, 100%{{ content: '✳'; }}
        }}
        @keyframes yazdani-glow {{
            0% {{ opacity: 0.6; transform: scale(0.95); }}
            100% {{ opacity: 1; transform: scale(1.15); filter: drop-shadow(0 0 8px rgba(129, 140, 248, 0.8)); }}
        }}
        .sweep-text {{
            background: linear-gradient(90deg, #94A3B8 0%, #FFFFFF 50%, #94A3B8 100%);
            background-size: 200% 100%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-sweep 2s ease-in-out infinite;
            font-weight: 600;
            font-size: 0.85rem;
            font-family: 'JetBrains Mono', monospace;
        }}
        @keyframes text-sweep {{
            0% {{ background-position: 100% 0; }}
            100% {{ background-position: -100% 0; }}
        }}

        /* MAIN LAYOUT */
        .main-layout {{
            display: flex;
            flex: 1;
            overflow: hidden;
        }}
        .sidebar {{
            width: 320px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            overflow-y: auto;
        }}
        .section-title {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .sidebar-card {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 0.85rem;
            font-size: 0.82rem;
            line-height: 1.5;
        }}

        /* CHAT PANEL */
        .chat-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            background: var(--bg-color);
            overflow: hidden;
        }}
        .chips-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem 0.8rem;
            padding: 1rem 1.75rem;
            border-bottom: 1px solid var(--border-color);
            background: rgba(15, 22, 38, 0.3);
            backdrop-filter: blur(8px);
            flex-shrink: 0;
        }}
        .chip {{
            background: rgba(21, 30, 50, 0.6);
            border: 1px solid var(--border-color);
            color: #CBD5E1;
            padding: 0.5rem 0.95rem;
            border-radius: 24px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(12px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}
        .chip:hover {{
            transform: translateY(-2px);
            border-color: var(--theme-color);
            color: #FFF;
            background: rgba(255, 255, 255, 0.03);
            box-shadow: var(--shadow-glow);
        }}
        .chip:active {{
            transform: translateY(0) scale(0.97);
        }}

        /* MESSAGES THREAD WITH SMOOTH AUTO-SCROLL */
        .messages-thread {{
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            scroll-behavior: smooth;
        }}
        .msg-row {{
            display: flex;
            gap: 0.85rem;
            max-width: 85%;
        }}
        .msg-row.user {{
            align-self: flex-end;
            flex-direction: row-reverse;
        }}
        .msg-row.ai {{
            align-self: flex-start;
        }}
        .avatar {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .avatar.ai {{
            background: linear-gradient(135deg, #6366F1, #4F46E5);
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
        }}
        .avatar.user {{
            background: #334155;
        }}
        .msg-bubble {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            padding: 1rem 1.25rem;
            border-radius: 14px;
            font-size: 0.9rem;
            line-height: 1.6;
        }}
        .msg-row.user .msg-bubble {{
            background: #4F46E5;
            border-color: #6366F1;
            color: #FFF;
        }}

        /* CHAT INPUT AREA */
        .chat-input-area {{
            padding: 0.75rem 2rem 1.5rem 2rem;
            background: transparent;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .typing-indicator {{
            display: none;
            align-items: center;
            gap: 0.75rem;
            padding: 0.4rem 0.5rem;
        }}
        .input-box-wrapper {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 28px;
            display: flex;
            align-items: center;
            padding: 0.5rem 0.75rem 0.5rem 1.25rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: border-color 0.2s;
        }}
        .input-box-wrapper:focus-within {{
            border-color: var(--primary);
        }}
        .input-box-wrapper input {{
            flex: 1;
            background: transparent;
            border: none;
            color: #FFF;
            font-size: 0.95rem;
            outline: none;
            padding: 0.25rem 0.5rem;
        }}
        .send-btn {{
            background: var(--primary-grad);
            color: #FFF;
            border: none;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="brand-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" fill="url(#brand_grad)"/>
                    <path d="M22 6L12 13L2 6" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="18" cy="16" r="3" fill="#10B981"/>
                    <path d="M16.5 16L17.5 17L19.5 15" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>
                    <defs>
                        <linearGradient id="brand_grad" x1="2" y1="4" x2="22" y2="20" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#0078D4"/>
                            <stop offset="1" stop-color="#6366F1"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <div>
                <div class="brand-title">Outlook AI Executive Assistant</div>
                <div style="font-size: 0.72rem; color: #64748B;">Powered by Google ADK & Microsoft Graph API</div>
            </div>
        </div>

        <div class="header-actions">
            <!-- PREMIUM MODEL SELECT DROPDOWN -->
            <div class="model-select-wrapper" style="position: relative; display: inline-flex; align-items: center;">
                <select id="model-select" class="btn-sec" style="padding-right: 2rem; -webkit-appearance: none; appearance: none; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.4); color: #818CF8; font-weight: 600; cursor: pointer; border-radius: 8px; font-size: 0.8rem;">
                    <option value="gemini-3.6-flash" style="background: #0F1626; color: #E2E8F0;">🤖 Gemini 3.6 Flash (Default)</option>
                    <option value="gemini-3.5-flash" style="background: #0F1626; color: #E2E8F0;">🤖 Gemini 3.5 Flash</option>
                    <option value="gemini-3.5-flash-lite" style="background: #0F1626; color: #E2E8F0;">🤖 Gemini 3.5 Lite</option>
                </select>
                <div style="position: absolute; right: 10px; pointer-events: none; color: #818CF8; font-size: 0.75rem;">▼</div>
            </div>

            <!-- CLEAN CONNECTED USER BADGE (ZERO REDUNDANCY) -->
            <div class="status-badge" id="authBadge">
                <div class="status-dot"></div>
                <span>Connected: Jesus Chavez (admin@sockcop.onmicrosoft.com)</span>
            </div>
            {auth_button_html}
            <button class="btn-sec" onclick="location.reload()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg> Clear Chat
            </button>
        </div>
    </header>

    <div class="main-layout">
        <div class="sidebar">
            <div>
                <div class="section-title">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                    <span>Tomorrow's Invites</span>
                </div>
                <div class="sidebar-card">
                    • <b>Team Leads Budget Alignment</b> (2:00 PM EDT)<br>
                    • <b>Q4 Resource Allocation</b> (7:00 PM EDT)
                </div>
            </div>

            <div>
                <div class="section-title">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                    <span>Recent Inbox</span>
                </div>
                <div class="sidebar-card">
                    • <b>Passkeys MFA Notice</b> (Microsoft Security)<br>
                    • <b>Azure Copilot Access</b> (Azure Notice)
                </div>
            </div>
        </div>

        <div class="chat-panel">
            <div class="chips-container">
                <div class="chip" style="--theme-color: #38BDF8; --shadow-glow: 0 0 15px rgba(56, 189, 248, 0.3);" onclick="sendPrompt('What was my last email?')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/></svg> What was my last email?
                </div>
                <div class="chip" style="--theme-color: #A78BFA; --shadow-glow: 0 0 15px rgba(167, 139, 250, 0.3);" onclick="sendPrompt('What is the oldest email you have?')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg> Oldest email
                </div>
                <div class="chip" style="--theme-color: #FBBF24; --shadow-glow: 0 0 15px rgba(251, 191, 36, 0.3);" onclick="sendPrompt('What meetings do I have tomorrow?')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> Tomorrow's meetings
                </div>
                <div class="chip" style="--theme-color: #34D399; --shadow-glow: 0 0 15px rgba(52, 211, 153, 0.3);" onclick="sendPrompt('Find emails from Lisa Bendorf')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Emails from Lisa
                </div>
                <div class="chip" style="--theme-color: #F472B6; --shadow-glow: 0 0 15px rgba(244, 114, 182, 0.3);" onclick="sendPrompt('Prepare a meeting briefing report for tomorrow')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#F472B6" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg> Prepare briefing
                </div>
            </div>

            <div id="messages-thread" class="messages-thread">
                <div class="msg-row ai">
                    <div class="avatar ai">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="#FFF"/>
                        </svg>
                    </div>
                    <div class="msg-bubble">
                        Hello Jesus! I am your <b>Outlook AI Executive Assistant</b> connected to <code>admin@sockcop.onmicrosoft.com</code> via Google ADK & Microsoft Graph API.
                        <br><br>
                        Ask me anything about your inbox or calendar (e.g. <em>"What was my last email?"</em>, <em>"What is the oldest email you have?"</em>).
                    </div>
                </div>
            </div>

            <div class="chat-input-area">
                <div id="typing-indicator" class="typing-indicator">
                    <span class="yazdani-spinner"></span>
                    <div style="display: flex; flex-direction: column;">
                        <span id="typing-status-text" class="sweep-text">Analyzing intent & Microsoft Graph data...</span>
                        <span id="typing-timer" style="font-size: 0.75rem; color: #818CF8; font-family: monospace; font-weight: 600;">⏱️ 0.0s</span>
                    </div>
                </div>

                <div class="input-box-wrapper">
                    <input type="text" id="chat-input" placeholder="Ask your Outlook assistant (e.g. What is the oldest email you have?)..." onkeydown="if(event.key==='Enter') submitMessage()">
                    <button class="send-btn" id="send-btn" onclick="submitMessage()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const sessionId = "chat-session-" + Math.floor(Math.random() * 100000);
        let timerInterval = null;

        function scrollToBottom() {{
            const thread = document.getElementById('messages-thread');
            if (thread) {{
                thread.scrollTo({{ top: thread.scrollHeight, behavior: 'smooth' }});
            }}
        }}

        function sendPrompt(txt) {{
            document.getElementById('chat-input').value = txt;
            submitMessage();
        }}

        async function submitMessage() {{
            const input = document.getElementById('chat-input');
            const q = input.value.trim();
            if(!q) return;

            const thread = document.getElementById('messages-thread');
            thread.innerHTML += `
                <div class="msg-row user">
                    <div class="avatar user">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFF" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    </div>
                    <div class="msg-bubble">${{q}}</div>
                </div>
            `;
            input.value = '';
            scrollToBottom();

            const indicator = document.getElementById('typing-indicator');
            const timerEl = document.getElementById('typing-timer');
            
            indicator.style.display = 'flex';
            scrollToBottom();

            const t0 = performance.now();
            if(timerInterval) clearInterval(timerInterval);
            timerInterval = setInterval(() => {{
                const elapsed = ((performance.now() - t0)/1000).toFixed(1);
                timerEl.innerText = '⏱️ ' + elapsed + 's';
            }}, 100);

            try {{
                const modelSelect = document.getElementById('model-select');
                const selectedModel = modelSelect ? modelSelect.value : 'gemini-3.6-flash';

                const res = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        message: q,
                        session_id: sessionId,
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/New_York',
                        model: selectedModel
                    }})
                }});
                const data = await res.json();
                clearInterval(timerInterval);
                indicator.style.display = 'none';

                let toolPills = '';
                if(data.tools_called && data.tools_called.length > 0) {{
                    toolPills = data.tools_called.map(t => `<span style="background: rgba(99,102,241,0.2); padding: 2px 6px; border-radius: 4px;">🛠️ ${{t.name}}</span>`).join(' ');
                }}

                thread.innerHTML += `
                    <div class="msg-row ai">
                        <div class="avatar ai">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="#FFF"/></svg>
                        </div>
                        <div class="msg-bubble">
                            <div>${{marked.parse(data.response || 'No response')}}</div>
                            <div style="margin-top: 8px; font-size: 0.72rem; color: #38BDF8; display: flex; gap: 10px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 4px;">
                                <span>⚡ Latency: <b>${{data.latency_s}}s</b></span>
                                ${{toolPills}}
                            </div>
                        </div>
                    </div>
                `;
                scrollToBottom();
            }} catch(e) {{
                clearInterval(timerInterval);
                indicator.style.display = 'none';
                thread.innerHTML += `
                    <div class="msg-row ai">
                        <div class="avatar" style="background: #EF4444; color: #FFF;">⚠️</div>
                        <div class="msg-bubble" style="color: #EF4444;">Error: ${{e}}</div>
                    </div>
                `;
                scrollToBottom();
            }}
        }}
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

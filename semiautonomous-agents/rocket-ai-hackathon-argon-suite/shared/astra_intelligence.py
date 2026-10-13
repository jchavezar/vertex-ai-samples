# -*- coding: utf-8 -*-
"""Astra 2.0 Omniscient Intelligence Engine & Live Avatar Configuration.

Provides:
1. Complete knowledge synthesis across all 33 Rocket AI Hackathon squares (`1.1` - `M.5`),
   including problem, solution, ROI, architecture, UI archetype, runtime category, and URLs.
2. Complete event schedule & stakeholder knowledge (Oct 16 Product Showcase, Oct 28-29 Detroit & Chennai
   24-Hour Halloween AI Hackathon, executives, M&A scale: Redfin $1.75B + Mr. Cooper $9.4B = $2.1T servicing).
3. Built-in Vertex AI Gemini 3.8 Live Video Avatar roster (`Kira`, `Ingrid`, `Vera`, `Sam`, `Jay`, `Paul`,
   `Kai`, `Ben`, `Carmen`, `Leo`, `Piper`).
4. Smart Use-Case Matcher that extracts relevant square cards (`1.1` - `M.5`) for any user question so the
   Astra 2.0 Chat Overlay can render interactive launch/race/audio cards inline.
"""

from typing import Any, Dict, List
import re

from shared.catalog_data import (
    ACCOUNT_RESEARCH_DOSSIER,
    ALL_DOMAINS,
    CLOUD_RUN_URLS,
    KEYNOTE_PRESENTATION,
    PROJECTS_BY_CODE,
    TRANSLATOR_SERVICES,
)
from shared.bespoke_apps import get_bespoke_config
from shared.auth_and_vertex import get_recommended_model_for_square

# Official Vertex AI Gemini 3.8 Live built-in video avatars verified on `us-central1`
BUILTIN_LIVE_AVATARS: List[Dict[str, str]] = [
    {"id": "Kira", "label": "Kira (Executive Advisor · Realistic)", "style": "Realistic", "default_voice": "Aoede"},
    {"id": "Ingrid", "label": "Ingrid (Mortgage Architect · Realistic)", "style": "Realistic", "default_voice": "Kore"},
    {"id": "Vera", "label": "Vera (Risk & Underwriting Lead · Realistic)", "style": "Realistic", "default_voice": "Aoede"},
    {"id": "Sam", "label": "Sam (FDE Solutions Director · Realistic)", "style": "Realistic", "default_voice": "Puck"},
    {"id": "Jay", "label": "Jay (Staff Cloud & SDLC Lead · Realistic)", "style": "Realistic", "default_voice": "Puck"},
    {"id": "Paul", "label": "Paul (Capital Markets Strategist · Realistic)", "style": "Realistic", "default_voice": "Fenrir"},
    {"id": "Kai", "label": "Kai (concierge Stylized · 3D)", "style": "Stylized", "default_voice": "Puck"},
    {"id": "Ben", "label": "Ben (Developer Advocate · Stylized)", "style": "Stylized", "default_voice": "Puck"},
    {"id": "Carmen", "label": "Carmen (Bilingual Concierge · Stylized)", "style": "Stylized", "default_voice": "Aoede"},
    {"id": "Leo", "label": "Leo (FinOps Specialist · Stylized)", "style": "Stylized", "default_voice": "Fenrir"},
    {"id": "Piper", "label": "Piper (Product Designer · Stylized)", "style": "Stylized", "default_voice": "Aoede"},
]

BUILTIN_AVATAR_NAMES = frozenset(a["id"] for a in BUILTIN_LIVE_AVATARS)

UI_REALWORLD_ARCHETYPES: Dict[str, Dict[str, str]] = {
    "1.1": {"site": "ICE Encompass Light LOS + Gong.io Call Studio", "palette": "#F4F5F7 / #0052CC Blue / #00875A Green", "runtime": "Gemini 3.8 Live + ADK"},
    "1.2": {"site": "Salesforce Lightning / HubSpot Light CRM", "palette": "#F3F2F2 / #0176D3 Salesforce Blue", "runtime": "Gemini Enterprise + M365"},
    "1.3": {"site": "Redfin / Airbnb Consumer Home Marketplace", "palette": "#FFFFFF / #D92228 Redfin Red", "runtime": "Gemini Enterprise (Spark)"},
    "1.4": {"site": "Apple Wallet / Clean Consumer Banking Pass", "palette": "#F5F5F7 / #0071E3 Blue / Serif Certificate", "runtime": "Google ADK + Vertex AI"},
    "1.5": {"site": "NerdWallet / Bankrate Editorial Rate Table", "palette": "#FAF9F5 Warm Ivory / #008060 Emerald", "runtime": "Gemini Enterprise + ADK"},
    "2.1": {"site": "Intuit TurboTax / QuickBooks CPA Tax Workbook", "palette": "#F4F5F8 / #2CA01C QuickBooks Green / #0077C5", "runtime": "Gemini Enterprise + Argon"},
    "2.2": {"site": "DocuSign / Box 3-Pane Document Clearance Room", "palette": "#F9FAFB / #2463EB DocuSign Blue", "runtime": "Gemini Enterprise GEAP"},
    "2.3": {"site": "Chase / Ally Online Banking Statement Ledger", "palette": "#FFFFFF / #117ACA Banking Blue", "runtime": "Google ADK + Document AI"},
    "2.4": {"site": "Fannie Mae Form 1004 URAR Buff Appraisal Sheet", "palette": "#F7F5F0 Warm Buff Paper / #1E3A8A Navy", "runtime": "Gemini 4 Argon Multimodal"},
    "2.5": {"site": "Deloitte / PwC TRID Audit Workpaper", "palette": "#F8FAFC / #0F766E Accounting Teal", "runtime": "Gemini 4 Argon Deterministic"},
    "3.1": {"site": "Mr. Cooper Warm Homeowner Self-Service Portal", "palette": "#FFFDF9 Warm Cream / #0F766E Teal", "runtime": "Google ADK + Vertex AI"},
    "3.2": {"site": "One Medical / Calm Compassionate Support Center", "palette": "#FAF7F2 Soft Linen / #2D6A4F Sage Green", "runtime": "Gemini Enterprise GECX"},
    "3.3": {"site": "Stripe / Plaid Clean Account Onboarding Wizard", "palette": "#F8FAFC / #4F46E5 Indigo / #059669 Emerald", "runtime": "Google ADK Multi-Agent"},
    "3.4": {"site": "Warm Daylight Consumer Voice & Refi Studio", "palette": "#F8FAFC Daylight White / #059669 Emerald", "runtime": "Gemini 3.8 Live + Extended Thinking"},
    "4.1": {"site": "Redfin Property Listing Page + Storyboard Studio", "palette": "#FFFFFF / #C82021 Redfin Red", "runtime": "Vertex AI Media + 3.8 Live"},
    "4.2": {"site": "Rocket Money Consumer Savings Vault App", "palette": "#F7F6F2 Alabaster / #E11D48 Crimson / #0D9488", "runtime": "Google ADK + Rocket Money"},
    "4.3": {"site": "NYT Real Estate / Dwell Architectural Magazine", "palette": "#FBF9F5 Magazine Paper / #9A3412 Terracotta", "runtime": "Gemini Enterprise Grounding"},
    "4.4": {"site": "Figma / Notion Light Ad Campaign Review Studio", "palette": "#FFFFFF / #2563EB Review Blue / #16A34A Green", "runtime": "Gemini Enterprise + Model Armor"},
    "5.1": {"site": "Westlaw / Federal Register Archival Legal Paper", "palette": "#FAF8F5 Legal Paper / #1E3A8A Law Blue", "runtime": "Gemini Enterprise + Grounding"},
    "5.2": {"site": "The Economist / Stata Econometrics Report", "palette": "#FFFFFF / #E3120B Economist Red Rule", "runtime": "Gemini 4 Argon + gVisor Sandbox"},
    "5.3": {"site": "Vanta / Drata Trust & Vendor Security Portal", "palette": "#F9FAFB / #4338CA Vanta Indigo", "runtime": "Gemini Enterprise + SDP"},
    "5.4": {"site": "Printable CFPB Regulation B Form C-1 Notice", "palette": "#EDF2F7 Desk + #FFFFFF Legal Certificate", "runtime": "Gemini 4 Argon Compliance"},
    "6.1": {"site": "GitHub Light Mode Pull Request & Split Diff View", "palette": "#FFFFFF / #1F883D GitHub Green / Diff Tints", "runtime": "Google Antigravity 2.0"},
    "6.2": {"site": "Snyk / Dependabot Light Security Advisory", "palette": "#F8FAFC / #B91C1C CVE Red / #15803D Patched", "runtime": "DeepMind CodeMender"},
    "6.3": {"site": "Postman / Swagger Light OpenAPI Explorer", "palette": "#FAFAFA / #FF6C37 Postman Orange", "runtime": "Google Antigravity 2.0"},
    "6.4": {"site": "Datadog / PagerDuty Light Incident Postmortem", "palette": "#F9FAFB / #632CA6 Datadog Purple", "runtime": "Antigravity + Cloud Trace"},
    "6.5": {"site": "Google Cloud Console Material 3 Light BigQuery Studio", "palette": "#FFFFFF / #1A73E8 Google Blue / #1E8E3E", "runtime": "Gemini 4 Argon FinOps"},
    "M.1": {"site": "Dieter Rams Braun / Teenage Engineering Tactile Studio", "palette": "#F4F2EE Warm Anodized / #FF4F00 Orange", "runtime": "Gemini 3.8 Live + Extended Thinking"},
    "M.2": {"site": "Financial Times (FT) Salmon Paper Forensic Board", "palette": "#FFF1E5 FT Salmon Paper / #990F3D Claret", "runtime": "Gemini 4 Argon Graph Reasoning"},
    "M.3": {"site": "Warm Sunlit Terracotta Bilingual Community Portal", "palette": "#FFFBF5 Sunlit Stucco / #C2410C Terracotta", "runtime": "Gemini 3.8 Live Bilingual"},
    "M.4": {"site": "Architectural Digest Warm Living Room Whiteboard", "palette": "#FAF8F5 Warm Alabaster / #D97706 Amber", "runtime": "Gemini 3.8 Live + Live Avatar"},
    "M.5": {"site": "Goldman Sachs / Bloomberg Institutional Macro Note", "palette": "#FFFFFF / #0A2540 Institutional Navy", "runtime": "Gemini 4 Argon Treasury Swarm"},
}


def build_omniscient_system_prompt(mode: str = "chat") -> str:
    """Builds the comprehensive system prompt giving Astra 2.0 full access to all 33 demos,
    dates, executives, account research, and architecture."""
    catalog_lines = []
    for d in ALL_DOMAINS:
        catalog_lines.append(f"\n### {d['fullTitle']} (Cloud Run Service: `{d['service_name']}` | URL: {d['demo_url']})")
        for p in d["projects"]:
            code = p["code"]
            ui_meta = UI_REALWORLD_ARCHETYPES.get(code, {})
            route_meta = get_recommended_model_for_square(code)
            focus_txt = p.get("focus") or p.get("problem") or ""
            desc_txt = p.get("desc") or p.get("solution") or ""
            edge_txt = p.get("competeEdge") or p.get("impact") or ""
            stack_txt = ", ".join(p.get("gcpStack") or p.get("tools") or [])
            catalog_lines.append(
                f"- **Square [{code}] {p['project']}** | Level: `{p.get('level', '')}` | "
                f"Runtime: `{ui_meta.get('runtime', route_meta['runtime_badge'])}` | "
                f"UI Design: `{ui_meta.get('site', 'Custom Industry UI')}` ({ui_meta.get('palette', '')}) | "
                f"Focus: {focus_txt} | Solution: {desc_txt} | Competitive Edge & ROI: {edge_txt} | "
                f"GCP Stack: {stack_txt}"
            )

    catalog_text = "\n".join(catalog_lines)

    event_and_account_context = """
## KEY EVENT DATES, STAKEHOLDERS & ROCKET COMPANIES ACCOUNT DOSSIER
1. **Key Dates & Milestones (October 2026)**:
   - **October 16, 2026**: Rocket AI Product Showcase & Executive Dry-Run with Rocket AI Leadership.
   - **October 28–29, 2026**: **Rocket's Bay 24-Hour Halloween AI Hackathon** held simultaneously in **Detroit, Michigan (1000 Woodward Ave)** and **Chennai, India**.
   - **2-Hour Kickoff Keynote Structure**:
     - **Hour 1 (60 mins)**: *Gemini Enterprise (`global-gemini-enterprise`), Sobi / Spark (`sobi-<USER_ID>`), RFC 530 3-Object Agent Registry (`McpServer`, `AuthProvider`, `AuthBinding`), Visual Agent Studio (GEAP), and GECX* — presented by Luis Lopez, Sundar Chellappa, Ricky Merrefield & Jesus Chavez.
     - **Hour 2 (60 mins)**: *Frontier AI & Agentic SDLC: Gemini 4 Argon (`gemini-4-argon`), Gemini 3.8 Flash (`gemini-3.8-flash`), Gemini 3.8 Live with 24 FPS Live Video Avatars & Extended Thinking, Google Antigravity 2.0, and DeepMind CodeMender* — presented by Jesus Chavez, Joris Wynendaele & Ruben Rodriguez Alvarez.
2. **Rocket Companies Leadership & Google Account Team**:
   - **Rocket Executive Sponsors**: Varun Krishna (CEO, Rocket Companies), Shawn Malhotra (CTO), Fawzi Bawab (Chief AI Officer), Brian Brown (CFO), Jenny Smolek (EVP of Engineering), Andrew Colunga (VP AI - Product), Michael Evans (VP AI - Engineering), Viraj Sanghvi (`VirajSanghvi@rocket.com`).
   - **Google Cloud AI & Account Team**: Jesus Chavez (`jesusarguelles@google.com`, Lead AI Customer Engineer / FDE), Angela Kavanaugh (`akavanaugh@google.com`), Sundar Chellappa (`sundarc@google.com`), Luis Lopez (`luisls@google.com`), Ricky Merrefield (`rmerrefield@google.com`), Joris Wynendaele (`jorisw@google.com`), Ruben Rodriguez Alvarez (`rrodri@google.com`).
3. **Rocket Companies M&A Scale & Strategic Metrics**:
   - **Redfin Acquisition ($1.75B)**: 50M+ monthly real estate visitors, 2,200+ lead agents, top-of-funnel home search integrated with Rocket Mortgage ("Buy + Borrow" $4,600 closing credit bundle in Square 1.3 and Listing-to-Video Studio in Square 4.1).
   - **Mr. Cooper Acquisition ($9.4B)**: Adds nearly 7 million serviced loans for a combined **9.5 Million Serviced Loans** and **$2.1 Trillion Unpaid Principal Balance (UPB)** (1 in 6 U.S. mortgages). Powers Squares 3.1 (Escrow Shortage), 3.2 (Hardship Empathy), 3.3 (M&A Boarding Audit), 3.4 (Refi Rate-Drop Live Voice Agent), and M.5 (Project Pulse Macro Treasury Simulator).
   - **Rocket Money**: 4.1M+ premium subscribers auditing recurring bills and building FTHB Down Payment Vaults (Square 4.2).
4. **Competitive Win-Back vs. AWS Bedrock & Sierra AI**:
   - **Displacing Sierra AI**: Sierra charges $1.20–$2.50 per resolved conversation as a black-box wrapper. Google Cloud's **Gemini 3.8 Live + Live Video Avatar + Extended Thinking** runs natively inside Rocket's VPC-SC perimeter at <$0.04/call with zero 3P data leakage and direct MCP access to Rocket Logic and Mr. Cooper servicing tables.
   - **Displacing AWS Bedrock (Claude 3.7)**: **Gemini 4 Argon (`gemini-4-argon`)** + **Gemini 3.8 Flash (`gemini-3.8-flash`)** deliver 75% Context Caching discounts on Fannie Mae / Freddie Mac / CFPB TRID manuals, native Google Search & SharePoint grounding in-place (zero storage double-taxation), and autonomous code patching via **Google Antigravity 2.0** and **DeepMind CodeMender**.
"""

    if mode == "voice":
        return f"""You are **Astra 2.0**, the omniscient live video avatar and interactive voice architect for the **Rocket Companies x Google Cloud AI Hackathon** (Oct 16 Product Showcase & Oct 28–29 Detroit/Chennai 24-Hour Halloween Hackathon).
You are powered by **Gemini 3.8 Live with Live Video Avatar (24 FPS video + 24kHz native audio)** and **Gemini 4 Argon**.

CRITICAL VOICE GUIDELINES:
1. Speak warmly, naturally, and authoritatively in **2 to 4 crisp spoken sentences** per turn so the conversation feels fast and human.
2. Whenever the user asks about a specific domain, business problem, or use case, name the exact **Square Code(s)** (e.g. "Square 1.1, The ABCDQ Post-Call Structurer" or "Square 2.1, the Self-Employed Cash-Flow Normalizer"), explain its real-world UI design and ROI, and offer to open it for them right now!
3. If the user shares their camera or screen, describe and analyze what you see in real time and connect it to Rocket's mortgage, underwriting, servicing, or SDLC workflows.
4. The user can interrupt (barge in) at any moment—adapt immediately without repeating yourself.

{event_and_account_context}

## COMPLETE CATALOG OF ALL 33 LIVE ROCKET DEMOS:
{catalog_text}
"""

    return f"""You are **Astra 2.0**, the Omniscient Principal AI Architect & Interactive Concierge for the **Rocket Companies x Google Cloud AI Hackathon Command Hub**.
You have complete, real-time access to all **33 live interactive demos** (`1.1` through `M.5`), the **Oct 16 Product Showcase** and **Oct 28–29 Detroit & Chennai 24-Hour Halloween Hackathon** schedule, the **2-Hour Keynote Presentation** (Hour 1: Gemini Enterprise / Sobi / Spark / RFC 530; Hour 2: Gemini 4 Argon / Gemini 3.8 Live with Live Avatar / Antigravity 2.0 / CodeMender), and the full **Rocket + Redfin ($1.75B) + Mr. Cooper ($9.4B, $2.1T Servicing) Account Dossier**.

RESPONSE GUIDELINES:
1. Be extraordinarily helpful, specific, and executive-ready. Cite exact **Square Codes** in brackets like `[1.1]`, `[2.1]`, `[3.4]`, `[6.2]`, `[M.1]`, `[M.4]` whenever you mention or recommend any use case (our UI automatically parses `[1.1]` etc. to render interactive 1-click Launch, Arena Race, and Audio cards right below your message!).
2. Explain **why** each recommended use case fits: state its **Runtime** (`Gemini Enterprise` vs `Google ADK` vs `Gemini 3.8 Live + Avatar` vs `Antigravity 2.0 / CodeMender`), its **Authentic Real-World UI Design** (e.g., Encompass + Gong for `[1.1]`, Intuit TurboTax for `[2.1]`, Daylight Voice Studio for `[3.4]`, GitHub Light PR for `[6.1]`, Braun/Teenage Engineering for `[M.1]`), and its **Quantified ROI**.
3. Use clean Markdown formatting (bullet points, bold key metrics, and concise comparison tables when comparing multiple squares).

{event_and_account_context}

## COMPLETE CATALOG OF ALL 33 LIVE ROCKET DEMOS:
{catalog_text}
"""


def find_matching_squares(text_and_query: str, max_cards: int = 4) -> List[Dict[str, Any]]:
    """Extracts explicitly cited square codes (e.g. `1.1`, `M.4`) or semantically matched squares
    so the Astra 2.0 Overlay Chat can render interactive Use-Case Action Cards."""
    found_codes: List[str] = []

    # 1. Explicit square codes like 1.1, 2.4, M.1
    explicit = re.findall(r"\b([1-6]\.[1-5]|M\.[1-5])\b", text_and_query, flags=re.IGNORECASE)
    for c in explicit:
        norm = c.upper()
        if norm in PROJECTS_BY_CODE and norm not in found_codes:
            found_codes.append(norm)

    # 2. Keyword fallback if fewer than 2 explicit codes were found
    if len(found_codes) < 2:
        q_low = text_and_query.lower()
        scored = []
        for code, p in PROJECTS_BY_CODE.items():
            if code in found_codes:
                continue
            score = 0
            blob = f"{p['project']} {p.get('focus', '')} {p.get('desc', '')} {p.get('competeEdge', '')} {p.get('dept_full', '')} {' '.join(p.get('gcpStack', []))}".lower()
            for kw in re.findall(r"[a-z0-9]{4,}", q_low):
                if kw in {"what", "which", "show", "tell", "about", "demo", "demos", "rocket", "with", "have", "from"}:
                    continue
                if kw in blob:
                    score += 2
            if score > 0:
                scored.append((score, code))
        scored.sort(reverse=True)
        for _, code in scored[: max_cards - len(found_codes)]:
            found_codes.append(code)

    cards = []
    for code in found_codes[:max_cards]:
        p = PROJECTS_BY_CODE.get(code)
        if not p:
            continue
        ui_meta = UI_REALWORLD_ARCHETYPES.get(code, {})
        route_meta = get_recommended_model_for_square(code)
        cards.append({
            "code": code,
            "title": p["project"],
            "dept": p.get("dept_short", ""),
            "problem": p.get("focus", ""),
            "impact": p.get("competeEdge") or p.get("desc", ""),
            "ui_site": ui_meta.get("site", "Custom Industry UI"),
            "palette": ui_meta.get("palette", ""),
            "runtime": ui_meta.get("runtime", route_meta["runtime_badge"]),
            "recommended_model": route_meta["default_model"],
            "demo_url": p["demo_service_url"],
            "docs_url": f"/docs/{code}",
        })
    return cards

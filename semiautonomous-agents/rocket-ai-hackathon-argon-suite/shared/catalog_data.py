# -*- coding: utf-8 -*-
"""Unified Catalog Data, 2-Hour Keynote Slides, Tool Translator, and Glossary for Rocket AI Hackathon."""

from shared.catalog_part1 import CLOUD_RUN_URLS, DOMAINS_PART1
from shared.catalog_part2 import ACCOUNT_RESEARCH_DOSSIER, DOMAINS_PART2

ALL_DOMAINS = DOMAINS_PART1 + DOMAINS_PART2

DOMAINS_BY_ID = {d["id"]: d for d in ALL_DOMAINS}

PROJECTS_BY_CODE = {}
for d in ALL_DOMAINS:
    for p in d["projects"]:
        p["dept_id"] = d["id"]
        p["dept_short"] = d["shortTitle"]
        p["dept_full"] = d["fullTitle"]
        p["demo_service_url"] = f"{d['demo_url']}/?case={p['code']}"
        p["docs_url"] = f"{CLOUD_RUN_URLS['portal']}/docs/{p['code']}"
        PROJECTS_BY_CODE[p["code"]] = p

KEYNOTE_PRESENTATION = {
    "hour1_gemini_enterprise": {
        "title": "Hour 1: Gemini Enterprise (Sobi / Spark, Agent Platform, Registry & GECX)",
        "duration": "60 Minutes • Live Architecture & Executive Walkthrough",
        "presenters": "Luis Lopez, Sundar Chellappa, Ricky Merrefield & Jesus Chavez",
        "slides": [
            {
                "time": "00:00 – 00:12",
                "title": "1. The Sea Change: From Passive Chat to Software-Generating Teammates",
                "subtitle": "Gemini Enterprise (`global-gemini-enterprise`) & Spark (`sobi-<USER_ID>`)",
                "bullets": [
                    "One Unified Prompt Box across Web (`gemini.google.com/work`), Desktop, Mobile, and Microsoft Teams/Outlook.",
                    "Spark is a persistent digital teammate that writes and runs Python/Bash inside isolated gVisor sandboxes to build dashboards, audit TRID disclosures, and analyze Redfin MLS spreadsheets.",
                    "Model Choice Built-In: Run workloads on Gemini 4 Argon (`gemini-4-argon`), Gemini 3.8 Flash, or Claude Opus/Sonnet 5.5 under a single Google Cloud enterprise contract and security perimeter."
                ],
                "demoRef": "1.3"
            },
            {
                "time": "00:12 – 00:25",
                "title": "2. Query-in-Place Enterprise Grounding & 3-Object Agent Registry",
                "subtitle": "Connecting O365 SharePoint, OneDrive, Encompass LOS, and BigQuery without Data Replication",
                "bullets": [
                    "Zero 'Storage Double Taxation': Query Rocket's SharePoint Online, Fannie/Freddie Selling Guides, and BigQuery Redfin/Mr. Cooper tables in-place.",
                    "RFC 530 3-Object Connector Architecture: `McpServer` (`agentregistry-<UUID>`), `AuthProvider` (`ge-auth-<FP64>`), and `AuthBinding` (`ge-bind-<FP64>`) preserve end-user 3LO Entra ID / O365 ACLs.",
                    "Centralized Governance: App Hub & Agent Registry (`ge-ai-app-*`) give Rocket Security a single pane of glass over every agent, tool, and MCP server."
                ],
                "demoRef": "2.1"
            },
            {
                "time": "00:25 – 00:40",
                "title": "3. Gemini Enterprise Agent Platform (GEAP) & Visual Agent Studio",
                "subtitle": "Low-Code Underwriting Workflows + Code-First ADK Multi-Agent Orchestration",
                "bullets": [
                    "Visual Agent Studio (L200) lets Rocket Operations build condition-clearing agents with `RUNTIME_STAGE_BLOCKING` CEL Human-in-the-Loop approval gates.",
                    "Agent Development Kit (ADK L300) orchestrates stateful multi-agent teams across Rocket Money, Redfin, and Mr. Cooper Servicing.",
                    "Model Armor + Cloud Sensitive Data Protection (SDP) enforces GLBA ethical walls, masking SSNs and bank account numbers inline."
                ],
                "demoRef": "2.2"
            },
            {
                "time": "00:40 – 01:00",
                "title": "4. Gemini Enterprise for CX (GECX) & Multimodal Live API (The Sierra AI Killer)",
                "subtitle": "Transforming Mr. Cooper Servicing, Escrow Shortages, Synopsis & Portfolio Recapture",
                "bullets": [
                    "Omnichannel GECX + Dialogflow CX handles high-volume Mr. Cooper escrow shortage journeys, official per-diem payoff quotes, and Form 1098 delivery.",
                    "CCAI Agent Assist upgrades Rocket Logic Synopsis from post-call batch summaries into real-time CFPB Regulation X loss-mitigation coaching.",
                    "Gemini Multimodal Live API delivers <200ms interruptible bidirectional voice for Refi Recapture—eliminating Sierra AI per-resolution fees."
                ],
                "demoRef": "3.4"
            }
        ]
    },
    "hour2_antigravity": {
        "title": "Hour 2: Google Antigravity 2.0, Sandboxed Code Execution, MCP & Gemini 4 Argon",
        "duration": "60 Minutes • Hands-On Builder & SDLC Deep Dive",
        "presenters": "Jesus Chavez, Joris Wynendaele & Google CE Mentors",
        "slides": [
            {
                "time": "01:00 – 01:15",
                "title": "1. Meet Google Antigravity 2.0: The Agent-First Development Platform",
                "subtitle": "Why Antigravity + Gemini 4 Argon Leaves Single-Threaded Claude Code Behind",
                "bullets": [
                    "Antigravity 2.0 Desktop IDE + `agy` CLI + Managed Agents API inside Gemini Enterprise.",
                    "Persistent Cloud Execution: Delegate an objective (Goal Mode), close your laptop, and let Antigravity subagents code, run browser tests, and verify builds in isolated gVisor sandboxes.",
                    "Powered by Gemini 4 Argon (`gemini-4-argon`) & Gemini 3.8 Flash: 2M context window, Context Caching, and OneQuota enterprise scale."
                ],
                "demoRef": "1.5"
            },
            {
                "time": "01:15 – 01:30",
                "title": "2. Model Context Protocol (MCP) & Cross-Funnel Subagent Orchestration",
                "subtitle": "Unifying Rocket Money -> Redfin -> Rocket Mortgage -> Rocket Close via MCP",
                "bullets": [
                    "Standardized MCP Servers expose Redfin Tour Webhooks, Rocket Money Goal Vaults, O365 Banker Calendars, and Rocket Pricing Engines safely.",
                    "Dynamic Python Workflows (`run_workflow` with `parallel()` and `pipeline()`) fan out across multiple subagents with strict JSON schema contracts.",
                    "Live Walkthrough: Building the Redfin-to-Rocket Cross-Funnel Campaign Bot (`4.5`) in 15 lines of Antigravity workflow code."
                ],
                "demoRef": "4.5"
            },
            {
                "time": "01:30 – 01:45",
                "title": "3. DeepMind CodeMender & The Autonomous AI Software Factory",
                "subtitle": "Zero-Touch Vulnerability Patching (`cm verify` / `cm fix`) & Legacy .NET Modernization",
                "bullets": [
                    "CodeMender traces OWASP CWE-89 SQLi and CWE-639 IDOR vulnerabilities across Rocket LOS APIs, reproduces exploits in a gVisor sandbox, and commits verified patches.",
                    "AI Software Factory Swarm (`workspace='share'`) converts a Product Requirements Document (PRD) into a tested FastAPI/.NET 9 Pull Request automatically.",
                    "Legacy C#/.NET Framework 4.8 WCF SOAP services refactored into containerized Cloud Run microservices in seconds."
                ],
                "demoRef": "6.1"
            },
            {
                "time": "01:45 – 02:00",
                "title": "4. Google CE Moonshots & Hackathon Kickoff Blueprint",
                "subtitle": "Project Siren, Spatial Close (3D Maps + Imagen 3), HiveMind Swarm & Air-Tight",
                "bullets": [
                    "How to clone any of the 33 live Cloud Run reference architectures using the Reproduction Blueprints on this portal.",
                    "Accessing your GCP Sandbox Project, Vertex AI `gemini-4-argon` & `gemini-3.8-flash` endpoints, and Antigravity MCP starter kits.",
                    "Judging Rubric for Track 1 (CX), Track 2 (Ops/Underwriting), Track 3 (Mr. Cooper Servicing), and Track 4 (Wildcard Moonshots)."
                ],
                "demoRef": "M.3"
            }
        ]
    }
}

TRANSLATOR_SERVICES = [
    {
        "service": "Vertex AI: Gemini 4 Argon (`gemini-4-argon`) & Gemini 3.8 Flash",
        "level": "L100–L300",
        "url": "https://cloud.google.com/vertex-ai",
        "oneLiner": "Google's newest frontier reasoning & coding model (`gemini-4-argon`) paired with ultra-fast `gemini-3.8-flash`, 2M context, Context Caching, and strict JSON schemas.",
        "useCase": "🚀 <strong>Core Reasoning, Pricing & Underwriting:</strong> Form 1084 Schedule C extraction, parallel function calling for rate quotes, and multi-document title/TRID auditing.",
        "chatgpt": "OpenAI GPT-4o / o3-mini API",
        "claude": "⭐ AWS Bedrock Claude 3.7 Sonnet / Opus",
        "sierra": "Underlying LLM in Sierra / ByFrost Gateway",
        "tags": ["chatgpt", "claude", "sierra"]
    },
    {
        "service": "Gemini Enterprise (Sobi / Spark Web App & Workplace Agents)",
        "level": "L100–L200",
        "url": "https://cloud.google.com/products/gemini-enterprise",
        "oneLiner": "Unified enterprise workspace (`/work`) with Spark digital teammate, sandboxed Python execution, and 3LO connectors to SharePoint, O365, and BigQuery.",
        "useCase": "⚡ <strong>Everyday Banker & Underwriter Productivity:</strong> Query FHA/VA/Conventional overlays in SharePoint, analyze Redfin MLS sheets, and generate banker battlecards.",
        "chatgpt": "ChatGPT Enterprise & Custom GPTs",
        "claude": "Claude for Enterprise & Claude Projects",
        "sierra": "Microsoft 365 Copilot / SharePoint Copilot",
        "tags": ["chatgpt", "claude"]
    },
    {
        "service": "Google Antigravity 2.0 (Agentic IDE, CLI, Swarm & Sandbox)",
        "level": "L300",
        "url": "https://antigravity.google",
        "oneLiner": "Agent-first IDE and cloud runtime with persistent multi-agent swarms (`workspace='share'`), isolated gVisor sandboxes, headless browser testing, and MCP.",
        "useCase": "💻 <strong>Full-Stack Engineering & Automation:</strong> Autonomous banker inbound triage (`1.5`), Redfin-to-Rocket MCP bot (`4.5`), and PRD-to-PR Software Factory (`6.2`).",
        "chatgpt": "OpenAI Codex CLI / Windsurf / Cursor",
        "claude": "⭐ Anthropic Claude Code CLI & MCP",
        "sierra": "GitHub Copilot Workspace",
        "tags": ["claude", "chatgpt"]
    },
    {
        "service": "Gemini Enterprise for CX (GECX), Dialogflow CX & CCAI Agent Assist",
        "level": "L100–L300",
        "url": "https://cloud.google.com/solutions/contact-center",
        "oneLiner": "Omnichannel customer care across web, mobile, and voice with deterministic compliance flows and real-time live specialist Agent Assist.",
        "useCase": "🎧 <strong>Mr. Cooper & Rocket Servicing:</strong> Automate annual escrow shortage resolution (`3.1`), per-diem payoff quotes (`3.2`), and live CFPB hardship coaching (`3.3`).",
        "chatgpt": "OpenAI Assistants API + 3P CCaaS",
        "claude": "AWS Connect + Bedrock Claude Agents",
        "sierra": "⭐ Sierra CX Agents & Conversational OS",
        "tags": ["sierra", "chatgpt", "claude"]
    },
    {
        "service": "Gemini Multimodal Live API (Bidirectional Audio/Video WebSockets)",
        "level": "L300",
        "url": "https://ai.google.dev/gemini-api/docs/live",
        "oneLiner": "Sub-200ms interruptible bidirectional voice & video streaming over WebSockets with live mid-sentence function calling.",
        "useCase": "🎙️ <strong>Portfolio Recapture & Voice Whisperer:</strong> Proactive Mr. Cooper refi recapture calls (`3.4`), Project Siren voice amortization (`M.1`), and Virtual Advisor (`M.4`).",
        "chatgpt": "OpenAI Realtime API",
        "claude": "— (No native audio-to-audio Live API; requires external STT/TTS)",
        "sierra": "⭐ Sierra Voice (Real-time phone CX agents)",
        "tags": ["sierra", "chatgpt"]
    },
    {
        "service": "Gemini Enterprise Agent Platform (GEAP), ADK & Agent Registry",
        "level": "L200–L300",
        "url": "https://cloud.google.com/products/gemini-enterprise-agent-platform",
        "oneLiner": "Visual Agent Studio (low-code), Agent Development Kit (code-first), and centralized Google Cloud Agent Registry (`McpServer`, `AuthProvider`, `AuthBinding`).",
        "useCase": "🛠️ <strong>Operations & Cross-Brand Orchestration:</strong> Bank statement large-deposit clearing (`2.2`) and Mr. Cooper + Redfin retention orchestrator (`3.5`).",
        "chatgpt": "OpenAI Agents SDK",
        "claude": "AWS Bedrock Agents & Flows",
        "sierra": "⭐ Sierra Agent Studio & Multi-Model Router",
        "tags": ["sierra", "chatgpt", "claude"]
    },
    {
        "service": "Google DeepMind CodeMender (Autonomous Security Patch Agent)",
        "level": "L300",
        "url": "https://deepmind.google/blog/introducing-codemender-an-ai-agent-for-code-security/",
        "oneLiner": "Autonomous vulnerability trace, exploit reproduction (`cm verify`), and code repair (`cm fix`) agent running inside isolated gVisor sandboxes.",
        "useCase": "🛡️ <strong>AppSec & SDLC Security:</strong> Automatically remediate SQLi, SSRF, and IDOR/BOLA vulnerabilities in Rocket LOS microservices (`6.1`).",
        "chatgpt": "OpenAI Code Interpreter Security Scripts",
        "claude": "Claude Code Security Review Loop",
        "sierra": "GitHub Copilot Autofix / Defender for Cloud",
        "tags": ["chatgpt", "claude"]
    },
    {
        "service": "Google Cloud Document AI (Mortgage & Lending Suite)",
        "level": "L200–L300",
        "url": "https://cloud.google.com/document-ai",
        "oneLiner": "Pre-trained lending OCR and structured entity extraction processors for W-2s, Paystubs, 1040s, Loan Estimates (LE), and Closing Disclosures (CD).",
        "useCase": "📂 <strong>Underwriting & TRID Compliance:</strong> W-2/Paystub 5% income variance check (`2.3`) and automated CFPB TRID 0%/10% tolerance cure checker (`5.3`).",
        "chatgpt": "GPT-4o Vision API (General OCR)",
        "claude": "AWS Textract + Claude Vision",
        "sierra": "Azure Document Intelligence",
        "tags": ["chatgpt", "claude"]
    },
    {
        "service": "Google Cloud Model Armor, Sensitive Data Protection & Vertex AI Eval",
        "level": "L100–L300",
        "url": "https://cloud.google.com/security-command-center/docs/model-armor-overview",
        "oneLiner": "Enterprise AI firewall for prompt-injection defense, deterministic GLBA PII/SSN masking, and ECOA Fair Lending counterfactual bias certification.",
        "useCase": "⚖️ <strong>Risk, Legal & Fair Lending:</strong> GLBA ethical walls (`5.2`) and 500-twin ECOA Regulation B Disparate Impact certification (`5.5`).",
        "chatgpt": "OpenAI Moderation API",
        "claude": "AWS Bedrock Guardrails",
        "sierra": "⭐ Sierra Guardrails & Auditing",
        "tags": ["sierra", "chatgpt", "claude"]
    },
    {
        "service": "NotebookLM Enterprise & Vertex AI Grounding",
        "level": "L100–L300",
        "url": "https://notebooklm.google/",
        "oneLiner": "Source-grounded synthesis over 1,400-page GSE selling guides, CFPB circulars, and Amrock title precedents with clickable paragraph citations.",
        "useCase": "📑 <strong>Underwriting, Title & Legal:</strong> Fannie/Freddie RSU income citations (`2.1`), Rocket Close title lien clearance (`2.5`), and CFPB RESPA audits (`5.1`).",
        "chatgpt": "ChatGPT Projects",
        "claude": "⭐ Claude Projects & Citations API",
        "sierra": "SharePoint RAG",
        "tags": ["claude", "chatgpt"]
    },
    {
        "service": "Gemini Omni, Veo 3.1 & Imagen 3 (Nano Banana 2)",
        "level": "L200–L300",
        "url": "https://deepmind.google/technologies/gemini-omni/",
        "oneLiner": "Conversational virtual staging, localized ad typography rendering, and multi-format 9:16 & 16:9 video tour production with SynthID.",
        "useCase": "🎨 <strong>Redfin & Rocket Growth Marketing:</strong> Virtual room staging (`4.2`), 15-sec vertical Reels home tours (`4.4`), and 3D Spatial Close (`M.2`).",
        "chatgpt": "DALL-E 3 / Sora",
        "claude": "AWS Bedrock Titan / Stability AI",
        "sierra": "Adobe Firefly / Microsoft Designer",
        "tags": ["chatgpt", "claude"]
    }
]

GLOSSARY_SERVICES = [
    {
        "name": "Gemini 4 Argon (`gemini-4-argon`)",
        "level": "L100 – L300",
        "desc1": "Google's frontier reasoning, coding, and multi-agent foundation model (Short-GA Oct 2026) deployed on Vertex AI Global Endpoint.",
        "desc2": "Powers complex Fannie Mae Form 1084 tax parsing, parallel pricing tool-calling, TRID auditing, and autonomous C#/.NET code modernization."
    },
    {
        "name": "Gemini 3.8 Flash (`gemini-3.8-flash`)",
        "level": "L100 – L300",
        "desc1": "Ultra-low-latency, high-efficiency agentic workhorse model delivering flagship intelligence at Flash speed and sub-second TTFT.",
        "desc2": "Ideal for high-concurrency Mr. Cooper servicing triage, parallel swarm workers, and real-time Contact Center Agent Assist."
    },
    {
        "name": "Gemini Enterprise (Sobi / Spark)",
        "level": "L100 – L200",
        "desc1": "Unified corporate AI platform (`global-gemini-enterprise`) featuring Spark (`sobi-<USER_ID>`), a 24/7 digital teammate with sandboxed Python execution.",
        "desc2": "Connects in-place to O365 SharePoint, Outlook, Teams, and BigQuery via RFC 530 3-object Agent Registry connectors (`McpServer`, `AuthProvider`, `AuthBinding`)."
    },
    {
        "name": "Google Antigravity 2.0 & MCP",
        "level": "L300",
        "desc1": "Agent-first development IDE, `agy` CLI, and cloud runtime with persistent multi-agent swarms, headless browser testing, and gVisor sandboxes.",
        "desc2": "Connects subagents to Redfin tour webhooks, Rocket Money savings vaults, and O365 calendars via Model Context Protocol (MCP)."
    },
    {
        "name": "GEAP, ADK & Agent Registry",
        "level": "L200 – L300",
        "desc1": "Gemini Enterprise Agent Platform combining visual Agent Studio (L200), code-first Agent Development Kit (L300), and Google Cloud Agent Registry.",
        "desc2": "Governs multi-agent A2A workflows with CEL Human-in-the-Loop blocking gates (`RUNTIME_STAGE_BLOCKING`) and enterprise telemetry."
    },
    {
        "name": "GECX, Dialogflow CX & Agent Assist",
        "level": "L100 – L300",
        "desc1": "Gemini Enterprise for Customer Experience powering deterministic servicing state machines, omnichannel self-service, and real-time call coaching.",
        "desc2": "Replaces Sierra AI and upgrades Rocket Logic Synopsis with live CFPB Regulation X loss-mitigation cards and 1-click CRM wrap-up."
    },
    {
        "name": "CodeMender Security Agent",
        "level": "L300",
        "desc1": "Autonomous code security agent powered by Google DeepMind and Gemini 4 Argon.",
        "desc2": "Traces OWASP vulnerabilities (SQLi, SSRF, IDOR), verifies exploits inside isolated gVisor containers (`cm verify`), and commits tested fixes (`cm fix`)."
    },
    {
        "name": "Document AI Lending Suite",
        "level": "L200 – L300",
        "desc1": "Specialized mortgage OCR and entity extraction processors for W-2s, Paystubs, 1040 Schedule C, Loan Estimates, and Closing Disclosures.",
        "desc2": "Automates 5% stated-vs-documented income variance checks and CFPB TRID 0%/10% fee tolerance audits prior to closing."
    },
    {
        "name": "Model Armor & Sensitive Data Protection",
        "level": "L100 – L300",
        "desc1": "Inline AI firewall inspecting prompts and outputs for prompt injection, jailbreaks, and GLBA Non-Public Personal Information (NPI).",
        "desc2": "Enforces ethical walls by cryptographically redacting SSNs, bank routing numbers, and tax data before cross-departmental agent calls."
    },
    {
        "name": "Gemini Multimodal Live API",
        "level": "L300",
        "desc1": "Bidirectional low-latency audio and video WebSocket streaming (`BidiGenerateContent`) with natural human barge-in.",
        "desc2": "Powers Conversational Rocket Recapture (`3.4`), Project Siren (`M.1`), and Project Mirror Virtual Advisor (`M.4`) in under 200ms."
    },
    {
        "name": "Gemini Omni, Veo 3.1 & Imagen 3",
        "level": "L200 – L300",
        "desc1": "Google DeepMind's multimodal creative suite for conversational virtual staging (Nano Banana 2) and 9:16 / 16:9 video tour generation.",
        "desc2": "Transforms empty Redfin listing photos into staged homes and social video ads with crisp rate typography and SynthID watermarks."
    },
    {
        "name": "NotebookLM Enterprise & Grounding",
        "level": "L100 – L300",
        "desc1": "Source-grounded research and RAG engine over Fannie Mae/Freddie Mac guides, CFPB circulars, and Rocket Close title precedents.",
        "desc2": "Eliminates hallucinations by anchoring every underwriting or compliance answer to clickable paragraph-level source citations."
    }
]

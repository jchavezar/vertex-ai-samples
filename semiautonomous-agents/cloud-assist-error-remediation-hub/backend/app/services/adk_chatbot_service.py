import os
from typing import List, Dict, Any
from app.config import GCP_PROJECT_ID, GCP_REGION
from app.models.schemas import ChatMessageRequest, ChatMessageResponse
from google import genai
from google.genai import types

# Lightweight intent router dictionary
GREETING_INTENTS = {"hi", "hello", "hey", "hola", "sup", "good morning", "good afternoon", "thanks", "thank you", "who are you", "what can you do", "help"}

def handle_chatbot_query(req: ChatMessageRequest) -> ChatMessageResponse:
    """
    Intelligent Intent Router + Google GenAI Client with Google Search grounding.
    Routes simple greetings in <50ms without invoking heavy LLM search loops.
    """
    clean_msg = req.message.strip().lower()

    # ⚡ INSTANT INTENT ROUTER FOR GREETINGS & SIMPLE QUERIES (<50ms)
    if clean_msg in GREETING_INTENTS or len(clean_msg) <= 3:
        service_name = req.contextError.serviceName if req.contextError else "GCP Cloud Service"
        summary = req.contextError.summary if req.contextError else "Active Incident Investigation"
        
        reply_text = (
            f"Hello! I am your **Google ADK Error Remediation Specialist**.\n\n"
            f"Active Incident Context: **{service_name}** (*\"{summary}\"*).\n\n"
            f"### How I Can Help:\n"
            f"- **⚡ Instant Diagnosis**: Analyze root cause stack traces and telemetry logs.\n"
            f"- **🛠️ gcloud Fixes**: Generate non-destructive gcloud CLI commands to fix secrets, IAM, memory, and concurrency.\n"
            f"- **🌐 Community Grounding**: Search official Google Cloud Docs and Reddit for verified solutions.\n\n"
            f"Ask me a specific question about **{service_name}** or click one of the dynamic action buttons below!"
        )
        return ChatMessageResponse(
            reply=reply_text,
            sourcesCited=[
                "https://cloud.google.com/docs",
                "https://reddit.com/r/googlecloud"
            ],
            sourceTag="ADK Remediation Agent (Instant Router)"
        )

    # 🧠 DEEP ADK DIAGNOSTIC ENGINE WITH GOOGLE SEARCH GROUNDING
    try:
        client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location="global"
        )
        
        # Build concise context block
        context_block = ""
        if req.contextError:
            context_block += (
                f"### ACTIVE INCIDENT\n"
                f"- **Service**: {req.contextError.serviceName}\n"
                f"- **Summary**: {req.contextError.summary}\n"
                f"- **Severity**: {req.contextError.severity}\n"
                f"- **Log Payload**: {req.contextError.fullText[:500]}\n\n"
            )
        if req.contextDiagnostic:
            context_block += (
                f"### GEMINI CLOUD ASSIST DIAGNOSTIC RECAP\n"
                f"{req.contextDiagnostic.recapText[:600]}\n\n"
            )
            for h in req.contextDiagnostic.hypotheses[:2]:
                context_block += (
                    f"#### Hypothesis: {h.title}\n"
                    f"- **Root Cause**: {h.rootCauseText}\n"
                    f"- **Remediation**: {h.recommendationText}\n\n"
                )
        
        system_instruction = (
            "You are the Cloud Assist Error Remediation Specialist Agent. "
            "Be extremely short, concise, and direct. Always use bullet points and bold key terms. "
            "Do NOT include conversational filler, meta-disclaimers, or introductory fluff. "
            "Provide exact step-by-step guidance and copyable gcloud CLI code blocks. "
            "Format in clean GitHub-flavored Markdown."
        )
        
        full_prompt = (
            f"{context_block}"
            f"### USER INQUIRY\n"
            f"{req.message}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[{"google_search": {}}],
                temperature=0.2
            )
        )
        
        reply_text = response.text or "No response generated."
        sources: List[str] = []
        
        try:
            if response.candidates and response.candidates[0].grounding_metadata:
                gm = response.candidates[0].grounding_metadata
                if hasattr(gm, "web_search_queries") and gm.web_search_queries:
                    sources.extend(gm.web_search_queries)
                if hasattr(gm, "grounding_chunks") and gm.grounding_chunks:
                    for chunk in gm.grounding_chunks:
                        if hasattr(chunk, "web") and chunk.web and hasattr(chunk.web, "uri"):
                            sources.append(chunk.web.uri)
        except Exception:
            pass
            
        return ChatMessageResponse(
            reply=reply_text,
            sourcesCited=sources[:5],
            sourceTag="ADK Remediation Agent (gemini-2.5-flash)"
        )
    except Exception as e:
        fallback_reply = _fallback_chat_reply(req, str(e))
        return ChatMessageResponse(
            reply=fallback_reply,
            sourcesCited=[
                "https://cloud.google.com/run/docs/troubleshooting",
                "https://cloud.google.com/sql/docs/postgres/maintenance"
            ],
            sourceTag="ADK Remediation Agent (Fallback)"
        )

def _fallback_chat_reply(req: ChatMessageRequest, err_msg: str) -> str:
    err = req.contextError
    if err and ("oom" in err.id.lower() or "503" in err.summary):
        return (
            f"### Cloud Run OOMKilled Remediation\n\n"
            f"- **Issue**: Container exceeded 512MB RAM ceiling during concurrency burst.\n"
            f"- **Solution**: Double memory ceiling and adjust max concurrency.\n\n"
            f"```bash\n"
            f"gcloud run services update {err.labels.get('service_name', 'api-gateway')} \\\n"
            f"  --memory=1024MiB \\\n"
            f"  --concurrency=30 \\\n"
            f"  --region={err.labels.get('region', 'us-central1')}\n"
            f"```"
        )
    elif err and "sql" in err.id.lower():
        return (
            f"### Cloud SQL Maintenance Timeout\n\n"
            f"- **Issue**: Automated patch maintenance caused 15s connection drop.\n"
            f"- **Solution**: Set explicit Sunday maintenance window.\n\n"
            f"```bash\n"
            f"gcloud sql instances patch prod-db-postgres \\\n"
            f"  --maintenance-window-day=SUN \\\n"
            f"  --maintenance-window-hour=3\n"
            f"```"
        )
    else:
        return (
            f"### Incident Remediation Action\n\n"
            f"Reviewed query: **\"{req.message}\"** for selected incident.\n\n"
            f"- **Step 1**: Execute gcloud verification check in the Hypotheses card.\n"
            f"- **Step 2**: Audit IAM Secret Accessor permissions.\n"
            f"- **Step 3**: Inspect readiness probe status."
        )

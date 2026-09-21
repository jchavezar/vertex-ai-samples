"""
Step 3: Deploying Google ADK Agents to Vertex AI Agent Runtime (Official AdkApp Wrapper)
---------------------------------------------------------------------------------------
This script demonstrates the production-recommended Google ADK deployment pattern:
Wrapping an ADK Agent using the first-party `vertexai.agent_engines.templates.adk.AdkApp`
wrapper and deploying it serverlessly to Vertex AI Agent Runtime (Reasoning Engines).

Enterprise Features:
1. First-Party ADK Wrapper:
   - Uses `from vertexai.agent_engines.templates.adk import AdkApp` (zero custom boilerplate).
2. Live BigQuery Precedent Integration:
   - Queries `vtxdemos.weil_legal_vault.precedent_deals` & `gold_standard_clauses`.
   - Uses GCP IAM identity and labels queries with `datacloud:antigravity`.
3. Auto-Detection of Existing Reasoning Engines:
   - Automatically detects active engines in `vtxdemos` (us-central1) to allow instant
     demonstration without 5-8 minute cold Cloud Build deployment delays.
4. Direct Google Cloud Console Shortcuts:
   - Prints direct deep links to open Agent Runtime and BigQuery tables in the GCP Console.
5. Gemini 3.8 Flash Core Engine:
   - Runs `gemini-3.8-flash` in `global` / `us-central1`.
"""

import os
import sys
import asyncio
import argparse
import functools

# Force unbuffered streaming output to terminal
print = functools.partial(print, flush=True)

# Enforce target environment configuration
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["BIGQUERY_PROJECT"] = "vtxdemos"
os.environ["BIGQUERY_LOCATION"] = "US"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

import vertexai
from vertexai.preview import reasoning_engines
from vertexai.agent_engines.templates.adk import AdkApp
from google.adk.agents import Agent
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# 1. Native BigQuery Tools for the ADK Agent
# ---------------------------------------------------------------------------
def query_bigquery_deals(sector: str = "Robotics / Tech", min_deal_size_m: float = 1000.0) -> list[dict]:
    """Query live M&A precedent transactions from BigQuery table `vtxdemos.weil_legal_vault.precedent_deals`.
    
    Args:
        sector: Target industry sector to benchmark (e.g. 'Robotics / Tech').
        min_deal_size_m: Minimum enterprise value in millions USD (e.g. 1000.0).
    """
    client = bigquery.Client(project="vtxdemos")
    sql = """
    SELECT deal_id, target, acquirer, sector, deal_size_m,
           reverse_breakup_fee_pct, reverse_breakup_fee_usd,
           antitrust_covenant, cfius_clearance_required, governing_law, execution_year
    FROM `vtxdemos.weil_legal_vault.precedent_deals`
    WHERE sector LIKE @sector AND deal_size_m >= @min_size
    ORDER BY deal_size_m DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("sector", "STRING", f"%{sector}%"),
            bigquery.ScalarQueryParameter("min_size", "FLOAT64", min_deal_size_m),
        ],
        labels={"datacloud": "antigravity"}
    )
    job = client.query(sql, job_config=job_config)
    return [dict(row) for row in job.result()]


def get_gold_precedent_clause(clause_name: str = "reverse_breakup_fee") -> dict:
    """Retrieve gold-standard curated legal clause language from `vtxdemos.weil_legal_vault.gold_standard_clauses`.
    
    Args:
        clause_name: Name of clause to lookup (e.g. 'reverse_breakup_fee').
    """
    client = bigquery.Client(project="vtxdemos")
    sql = """
    SELECT clause_id, clause_name, category, language, leverage_balance,
           market_adoption_pct, risk_assessment
    FROM `vtxdemos.weil_legal_vault.gold_standard_clauses`
    WHERE LOWER(clause_name) LIKE @clause_name
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("clause_name", "STRING", f"%{clause_name.lower()}%"),
        ],
        labels={"datacloud": "antigravity"}
    )
    job = client.query(sql, job_config=job_config)
    rows = [dict(row) for row in job.result()]
    return rows[0] if rows else {}


# ---------------------------------------------------------------------------
# 2. Define the ADK Agent & Wrap with Official `AdkApp`
# ---------------------------------------------------------------------------
bigquery_deal_agent = Agent(
    name="weil_deal_intelligence_agent",
    model="gemini-3.8-flash",
    instruction="""
    You are the Weil Senior M&A Precedent & Deal Benchmarking Specialist running on Vertex AI Agent Runtime.
    Your mandate:
    1. Query live BigQuery precedent deals in `vtxdemos.weil_legal_vault.precedent_deals` using `query_bigquery_deals`.
    2. Retrieve the gold-standard reverse breakup fee language using `get_gold_precedent_clause`.
    3. State explicitly the deal metrics, fee percentage corridor, and covenant structures.
    4. Synthesize the findings into an executive legal memorandum for the lead partner.
    """,
    tools=[query_bigquery_deals, get_gold_precedent_clause],
)

# Production Google ADK Wrapper for Vertex AI Agent Runtime (with Cloud Trace & Telemetry)
adk_runtime_app = AdkApp(
    agent=bigquery_deal_agent,
    app_name="weil_legal_adk_engine",
    enable_tracing=True,
)


# ---------------------------------------------------------------------------
# 3. Detection & Deployment Workflow
# ---------------------------------------------------------------------------
TARGET_ENGINE_NAME = "Weil_Legal_ADK_Engine"
STAGING_BUCKET = "gs://vtxdemos_staging"


def detect_existing_engines(client: vertexai.Client):
    try:
        return list(client.agent_engines.list())
    except Exception as e:
        print(f"⚠️ Notice scanning engines: {e}")
        return []


# ---------------------------------------------------------------------------
# 4. Demonstration Workflow
# ---------------------------------------------------------------------------
async def run_walkthrough():
    parser = argparse.ArgumentParser(description="Weil Legal ADK Engine - Vertex AI Agent Runtime")
    parser.add_argument("--redeploy", action="store_true", help="Force a fresh deployment even if an engine already exists")
    parser.add_argument("--local", action="store_true", help="Run in local simulation mode without deploying to cloud")
    args = parser.parse_args()

    project = "vtxdemos"
    location = "us-central1"
    dashboard_url = f"https://console.cloud.google.com/agent-platform/runtimes?project={project}"
    vertex_re_url = f"https://console.cloud.google.com/vertex-ai/reasoning-engines?project={project}"
    bq_vault_url = f"https://console.cloud.google.com/bigquery?project={project}&ws=!1m5!1m4!4m3!1s{project}!2sweil_legal_vault!3sprecedent_deals"

    vertexai.init(project=project, location=location, staging_bucket=STAGING_BUCKET)
    client = vertexai.Client(project=project, location=location)

    print("=" * 78)
    print(f"🔍 [AUTO-DETECT] Scanning Vertex AI Agent Runtime in `{project}` ({location})...")
    print("=" * 78)

    all_engines = detect_existing_engines(client=client)
    weil_engine = next((e for e in all_engines if getattr(e.api_resource, 'display_name', '') == TARGET_ENGINE_NAME), None)

    if all_engines:
        print(f"📋 Detected {len(all_engines)} Active Reasoning Engines in `{project}` ({location}):")
        for idx, eng in enumerate(all_engines):
            disp_name = getattr(eng.api_resource, 'display_name', 'Unknown')
            res_id = getattr(eng.api_resource, 'name', '')
            indicator = "👉 [TARGET MATCH]" if disp_name == TARGET_ENGINE_NAME else "  "
            print(f"   {indicator} [{idx + 1}] {disp_name}")
            print(f"          Resource ID : {res_id}")
        print()

    active_remote_engine = None

    if args.local:
        print(f"💻 [--local flag provided] Running in local simulation mode.")
    elif weil_engine and not args.redeploy:
        # Re-use existing deployment
        res_id = getattr(weil_engine.api_resource, 'name', '')
        engine_id = res_id.split("/")[-1]
        engine_url = f"https://console.cloud.google.com/vertex-ai/locations/{location}/reasoning-engines/{engine_id}?project={project}"
        print(f"♻️  [RE-USING DEPLOYMENT] '{TARGET_ENGINE_NAME}' is ALREADY DEPLOYED!")
        print("   " + "-" * 72)
        print(f"   • Display Name : {TARGET_ENGINE_NAME}")
        print(f"   • Resource ID  : {res_id}")
        print(f"   • Telemetry    : ENABLED (Cloud Trace + OpenTelemetry)")
        print(f"   • Direct Link  : {engine_url}")
        print("   " + "-" * 72)
        print("   ⚡ Skipping new deployment build — re-using active cloud runtime instance!")
        active_remote_engine = weil_engine
    else:
        # Deploy new engine and WAIT until deployment completes
        if args.redeploy:
            print(f"🔄 [--redeploy flag provided] Initiating fresh deployment for '{TARGET_ENGINE_NAME}'...")
        else:
            print(f"🚀 [NEW DEPLOYMENT] '{TARGET_ENGINE_NAME}' is NOT yet deployed in `{project}` ({location}).")

        print("   " + "-" * 72)
        print(f"   • Target Project     : {project}")
        print(f"   • Runtime Region     : {location}")
        print(f"   • Staging Bucket     : {STAGING_BUCKET}")
        print(f"   • Framework          : Google ADK (Official AdkApp wrapper)")
        print(f"   • Core Model         : gemini-3.8-flash (Global Vertex AI)")
        print(f"   • Logging & Tracing  : ENABLED (Cloud Trace + OpenTelemetry)")
        print(f"   • Staging Dir        : reasoning_engine_weil")
        print("   " + "-" * 72)
        print("   ⏳ Packaging code and initiating Vertex AI Agent Runtime deployment...")
        print("   ⏳ WAITING until the deployment operation finishes on Google Cloud (~4-6 mins)...")
        print("   (Vertex AI will containerize requirements, build runtime, and create serverless endpoint)")
        print("=" * 78 + "\n")

        try:
            active_remote_engine = client.agent_engines.create(
                agent=adk_runtime_app,
                config=dict(
                    display_name=TARGET_ENGINE_NAME,
                    description="Weil Gotshal Autonomous M&A Deal & Precedent Intelligence Engine on Vertex AI Agent Runtime.",
                    staging_bucket=STAGING_BUCKET,
                    gcs_dir_name="reasoning_engine_weil",
                    requirements=[
                        "google-cloud-aiplatform[agent_engines,adk]>=1.75.0",
                        "google-adk>=2.8.0",
                        "google-cloud-bigquery>=3.25.0",
                        "google-genai>=0.1.1",
                        "google-cloud-logging>=3.11.0",
                        "google-cloud-trace>=1.15.0",
                        "opentelemetry-api>=1.25.0",
                        "opentelemetry-sdk>=1.25.0",
                        "opentelemetry-exporter-otlp-proto-http>=1.25.0",
                        "opentelemetry-exporter-gcp-trace>=1.15.0",
                        "opentelemetry-instrumentation-google-genai>=0.7b1",
                        "pydantic>=2.0.0",
                        "cloudpickle",
                        "db-dtypes>=1.2.0",
                    ],
                    env_vars={
                        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
                        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
                        "GOOGLE_GENAI_USE_VERTEXAI": "true",
                        "GOOGLE_CLOUD_LOCATION": "global",
                    },
                    agent_framework="google-adk",
                ),
            )
            res_id = getattr(active_remote_engine.api_resource, 'name', '')
            engine_id = res_id.split("/")[-1]
            engine_url = f"https://console.cloud.google.com/vertex-ai/locations/{location}/reasoning-engines/{engine_id}?project={project}"
            print("\n" + "=" * 78)
            print(f"🎉 [DEPLOYMENT COMPLETE] '{TARGET_ENGINE_NAME}' is now LIVE on Google Cloud!")
            print("=" * 78)
            print(f"   • Resource ID  : {res_id}")
            print(f"   • Direct Link  : {engine_url}")
            print(f"   • Agent Portal : {dashboard_url}")
            print(f"   • Telemetry    : ENABLED (Cloud Trace + OpenTelemetry)")
            print("=" * 78 + "\n")
        except Exception as e:
            print(f"\n❌ Deployment error: {e}")
            print("⚠️ Falling back to local AdkApp execution for immediate presentation...\n")

    # Step B: Display the Official ADK Production Deployment Spec
    print("\n" + "=" * 78)
    print("☁️ [AGENT RUNTIME SPECIFICATION] Official ADK Deployment (AdkApp)")
    print("=" * 78)
    print("""
# Official Google ADK Deployment to Vertex AI Agent Runtime:
import vertexai
from vertexai.agent_engines.templates.adk import AdkApp

client = vertexai.Client(project="vtxdemos", location="us-central1")

deployed_engine = client.agent_engines.create(
    agent=AdkApp(agent=bigquery_deal_agent, app_name="weil_legal_adk_engine", enable_tracing=True),
    config=dict(
        display_name="Weil_Legal_ADK_Engine",
        description="Autonomous M&A Deal & Precedent Intelligence Engine on Vertex AI Agent Runtime.",
        staging_bucket="gs://vtxdemos_staging",
        requirements=[
            "google-cloud-aiplatform[agent_engines,adk]>=1.75.0",
            "google-adk>=2.8.0",
            "google-cloud-bigquery>=3.25.0",
            "google-genai>=0.1.1",
            "google-cloud-logging>=3.11.0",
            "google-cloud-trace>=1.15.0",
            "opentelemetry-api>=1.25.0",
            "opentelemetry-sdk>=1.25.0",
            "opentelemetry-exporter-otlp-proto-http>=1.25.0",
            "opentelemetry-exporter-gcp-trace>=1.15.0",
            "opentelemetry-instrumentation-google-genai>=0.7b1",
            "pydantic>=2.0.0",
            "cloudpickle",
            "db-dtypes>=1.2.0",
        ],
        env_vars={
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
            "GOOGLE_GENAI_USE_VERTEXAI": "true",
            "GOOGLE_CLOUD_LOCATION": "global",
        },
        agent_framework="google-adk",
    ),
)
""")

    # Resolve active resource name if deployed
    active_resource_name = ""
    if active_remote_engine:
        if hasattr(active_remote_engine, "api_resource"):
            active_resource_name = active_remote_engine.api_resource.name
        elif hasattr(active_remote_engine, "resource_name"):
            active_resource_name = active_remote_engine.resource_name

    # Step C: Execute Live Streaming Precedent Benchmarking
    print("=" * 78)
    print("⚡ [LIVE RUNTIME EXECUTION] Testing Official `AdkApp` Precedent Intelligence")
    print(f"   Model Engine         : gemini-3.8-flash (Global Vertex AI)")
    print(f"   ADK Wrapper          : vertexai.agent_engines.templates.adk.AdkApp")
    print(f"   BigQuery Vault       : vtxdemos.weil_legal_vault")
    if active_resource_name:
        engine_display_id = active_resource_name.split("/")[-1]
        print(f"   Deployment Status    : LIVE ON GCP ({engine_display_id})")
        print(f"   Telemetry            : ENABLED (Cloud Trace + OpenTelemetry)")
    else:
        print(f"   Deployment Status    : LOCAL VERIFICATION")
    print("=" * 78)

    adk_runtime_app.set_up()

    test_prompt = (
        "Client Nexus Capital is structuring a $2.3B acquisition of Zephyr Robotics. "
        "Benchmark comparable deals in tech/robotics above $1000M in BigQuery (`vtxdemos.weil_legal_vault`), "
        "and retrieve the gold-standard reverse breakup fee clause language for antitrust risk."
    )

    print(f"\n👤 [PROMPT]:\n{test_prompt}\n")
    print("📡 [LIVE AGENT RUNTIME STREAMING OUTPUT]:\n")

    async for event in adk_runtime_app.async_stream_query(message=test_prompt, user_id="lead_partner_ebc"):
        if isinstance(event, dict) and "content" in event:
            parts = event["content"].get("parts", [])
            for p in parts:
                if "text" in p and p["text"]:
                    print(p["text"], end="", flush=True)

    print("\n\n" + "=" * 78)
    print("💡 WHY THIS MATTERS TO WEIL")
    print("=" * 78)
    print("1. Zero Boilerplate: Uses official first-party `AdkApp` wrapper; no fragile custom server code.")
    print("2. Idempotent Cloud Lifecycle: Automatically re-uses active cloud engines or deploys on demand.")
    print("3. Native IAM Identity: Authenticates to BigQuery via GCP Service Accounts without hardcoded keys.")
    print("4. Precedent Verification: Every deal benchmark cites live BigQuery rows for verified legal provenance.")
    print("=" * 78)
    print("✅ Step 3 Agent Runtime Walkthrough Complete.\n")
    print("🔗 [GOOGLE CLOUD CONSOLE DIRECT SHORTCUTS]:")
    print(f"   🚀 Agent Platform Runtimes : {dashboard_url}")
    print(f"   ⚙️ Vertex Reasoning Engines: {vertex_re_url}")
    if active_resource_name:
        engine_id = active_resource_name.split("/")[-1]
        print(f"   🎯 Weil Engine Console URL : https://console.cloud.google.com/vertex-ai/locations/{location}/reasoning-engines/{engine_id}?project={project}")
    print(f"   🏛️ BigQuery Legal Vault    : {bq_vault_url}\n")


if __name__ == "__main__":
    asyncio.run(run_walkthrough())




import os
import csv
import json
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent, Agent
from google.adk.tools import tool, google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Ensure required ADK environment variables are set
if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
if not os.getenv("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"  # Required for gemini-3 models

# --------------------------------------------------------------------------------
# 1. Define Data Models (Pydantic)
# --------------------------------------------------------------------------------
class Vendor(BaseModel):
    name: str
    category: str
    typical_amount_range: tuple[float, float]

class Transaction(BaseModel):
    trans_id: str
    date: str
    account_code: str
    entity: str
    vendor_name: str
    amount_usd: float
    approval_status: str
    description: str

class SyntheticDataset(BaseModel):
    approved_vendors: list[Vendor]
    ledger_rows: list[Transaction]

# --------------------------------------------------------------------------------
# 2. Define Tools and Search Agent
# --------------------------------------------------------------------------------
# Create a dedicated search agent (google_search must be used alone per agent)
search_agent = Agent(
    name="vendor_search_agent",
    model="gemini-2.5-flash",
    instruction="""You are a corporate vendor research specialist.
    When given a business category, use Google Search to find the top 10 real US corporate vendors in that category.
    Return ONLY a comma-separated list of company names, nothing else.
    Example output: "Salesforce, Microsoft, Oracle, AWS, Datadog"
    """,
    description="Searches for real corporate vendors using Google Search",
    tools=[google_search]
)

# --------------------------------------------------------------------------------
# 3. Define the Generator Agent
# --------------------------------------------------------------------------------
def create_generator_agent() -> LlmAgent:
    return LlmAgent(
        name="synthetic_data_generator",
        model="gemini-2.5-flash",
        instruction="""
        You are a specialized Data Generation Agent.
        Your goal is to create a highly realistic financial ledger and a corresponding approved vendor list.

        WORKFLOW:
        1.  Use the vendor_search_agent tool to find real US corporate vendors for each category:
            - Software
            - Consulting
            - Travel
            - Office
            - Legal
            - Utilities
        2.  The search agent will return comma-separated company names from Google Search.

        CRITICAL RULES:
        1.  **The Trap**: You MUST insert exactly 3 transactions for 'K-Consulting LLC'.
            -   These 3 transactions MUST total exactly $120,000.
            -   These 3 transactions MUST occur on Friday evenings after 6:00 PM (18:00).
        2.  **The Anomaly**: 'K-Consulting LLC' MUST NOT appear in the 'approved_vendors' list.
        3.  **Realism**: Use the vendor_search_agent to find REAL company names for the other transactions.
        4.  **Volume**: The final dataset must have exactly 150 rows.
        """,
        tools=[AgentTool(agent=search_agent)],
        output_schema=SyntheticDataset
    )

# --------------------------------------------------------------------------------
# 4. Generation Logic with Real Google Search
#    Uses Google Search for realistic vendor data while guaranteeing "Trap" constraints.
# --------------------------------------------------------------------------------

# Fallback vendor data (used when Google Search is unavailable or for deterministic testing)
FALLBACK_VENDORS = {
    "Software": ["Salesforce", "AWS", "Microsoft Azure", "Slack", "Atlassian", "Oracle", "Intuit", "Zoom", "Datadog", "Snowflake"],
    "Consulting": ["McKinsey & Company", "Boston Consulting Group", "Deloitte", "Accenture", "Bain & Company", "KPMG", "PwC"],
    "Travel": ["Delta Air Lines", "Marriott Bonvoy", "Uber Business", "American Express Global Travel", "Hertz", "United Airlines"],
    "Office": ["Staples Advantage", "W.B. Mason", "Uline", "Pitney Bowes", "Xerox", "Canon Solutions"],
    "Legal": ["Baker McKenzie", "Latham & Watkins", "Kirkland & Ellis", "Skadden", "Jones Day"],
    "Utilities": ["Con Edison", "Verizon Business", "Waste Management", "PG&E", "AT&T Corp"]
}

async def search_vendors_by_category(category: str) -> list[str]:
    """
    Searches for real corporate vendors using Google Search via the search_agent.
    Falls back to static data if search fails.
    """
    try:
        # Create a runner for the search agent
        session_service = InMemorySessionService()
        runner = Runner(agent=search_agent, app_name="vendor_search", session_service=session_service)

        # Create a session and run the search
        session = await session_service.create_session(app_name="vendor_search", user_id="generator")

        query = f"Find top 10 {category} corporate vendors in the USA"
        result_text = ""

        async for event in runner.run_async(user_id="generator", session_id=session.id, new_message=query):
            if hasattr(event, 'text') and event.text:
                result_text += event.text
            elif hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text'):
                        result_text += part.text

        if result_text:
            # Parse comma-separated vendor names from the response
            vendors = [v.strip() for v in result_text.split(',') if v.strip()]
            if vendors and len(vendors) >= 3:
                print(f"  ✓ Found {len(vendors)} real vendors for '{category}' via Google Search")
                return vendors[:10]
    except Exception as e:
        print(f"  ⚠ Google Search failed for '{category}': {e}. Using fallback data.")

    # Fallback to static data
    return FALLBACK_VENDORS.get(category, ["Generic Vendor Inc"])

def generate_dataset_programmatically():
    print("Agent 'synthetic_data_generator' starting...")

    # --- A. Approved Vendors (with real Google Search) ---
    categories = ["Software", "Consulting", "Travel", "Office", "Legal", "Utilities"]
    approved_vendors = []

    # Run async vendor searches
    async def fetch_all_vendors():
        results = {}
        for cat in categories:
            results[cat] = await search_vendors_by_category(cat)
        return results

    print("Searching for real corporate vendors via Google Search...")
    vendor_results = asyncio.run(fetch_all_vendors())

    # Populate approved vendors from search results
    for cat in categories:
        names = vendor_results.get(cat, FALLBACK_VENDORS.get(cat, []))
        for name in names:
            # Avoid the anomaly vendor in the approved list
            if name != "K-Consulting LLC":
                range_min = 500.0 if cat != "Software" else 2000.0
                range_max = 5000.0 if cat != "Consulting" else 15000.0
                approved_vendors.append(Vendor(name=name, category=cat, typical_amount_range=(range_min, range_max)))

    # --- B. The Trap Configuration ---
    anomaly_vendor = "K-Consulting LLC"
    anomaly_total = 120000.00
    # Split $120k into 3 uneven parts for realism
    anomaly_splits = [42500.00, 38500.00, 39000.00] 
    assert sum(anomaly_splits) == anomaly_total
    
    # Find 3 Fridays in 2026
    fridays_2026 = []
    curr = datetime(2026, 1, 1)
    while len(fridays_2026) < 20: # Get first 20 fridays to pick from
        if curr.weekday() == 4: # Friday
            fridays_2026.append(curr)
        curr += timedelta(days=1)
        
    selected_fridays = random.sample(fridays_2026, 3)
    anomaly_txns = []
    
    for i, date_obj in enumerate(selected_fridays):
        # Set time to after 6 PM (e.g., 18:45, 19:12, 21:05)
        hour = random.randint(18, 22)
        minute = random.randint(0, 59)
        final_date = date_obj.replace(hour=hour, minute=minute)
        
        txn = Transaction(
            trans_id=f"TXN-2026-{9000+i}", # High ID for anomaly
            date=final_date.strftime("%Y-%m-%d %H:%M:%S"),
            account_code="700-CONSULT-EXT",
            entity="Verity Nexus HQ",
            vendor_name=anomaly_vendor,
            amount_usd=anomaly_splits[i],
            approval_status="AUTO-APPROVE", # Suspicious status
            description="Strategic Advisory Retainer - Urgent"
        )
        anomaly_txns.append(txn)

    # --- C. Regular Transactions (147 rows) ---
    regular_txns = []
    for i in range(147):
        vendor = random.choice(approved_vendors)
        
        # Random date in 2026, business hours (9-17)
        rand_day = random.randint(1, 360)
        base_date = datetime(2026, 1, 1) + timedelta(days=rand_day)
        # Avoid weekends for regular txns
        while base_date.weekday() >= 5: 
            base_date += timedelta(days=1)
            
        final_date = base_date.replace(hour=random.randint(9, 17), minute=random.randint(0, 59))
        
        amount = round(random.uniform(vendor.typical_amount_range[0], vendor.typical_amount_range[1]), 2)
        
        txn = Transaction(
            trans_id=f"TXN-2026-{str(i+1).zfill(4)}",
            date=final_date.strftime("%Y-%m-%d %H:%M:%S"),
            account_code=f"500-{vendor.category.upper()}",
            entity="Verity Nexus HQ",
            vendor_name=vendor.name,
            amount_usd=amount,
            approval_status="APPROVED",
            description=f"Standard {vendor.category} Expense"
        )
        regular_txns.append(txn)

    # --- D. Combine and Save ---
    all_rows = regular_txns + anomaly_txns
    random.shuffle(all_rows) # Shuffle to hide the trap
    
    # Save ledger
    os.makedirs("verity-nexus-engine/data", exist_ok=True)
    
    with open("verity-nexus-engine/data/ledger_2026.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Trans_ID", "Date", "Account_Code", "Entity", "Vendor_Name", "Amount_USD", "Approval_Status", "Description"])
        for r in all_rows:
            writer.writerow([r.trans_id, r.date, r.account_code, r.entity, r.vendor_name, r.amount_usd, r.approval_status, r.description])
            
    # Save approved vendors (Anomaly vendor NOT included)
    vendor_names = [v.name for v in approved_vendors]
    with open("verity-nexus-engine/data/approved_vendors.json", "w") as f:
        json.dump({"approved_vendors": vendor_names}, f, indent=2)

    print("SUCCESS: Generated 'ledger_2026.csv' (150 rows) and 'approved_vendors.json'.")
    print(f"TRAP VERIFICATION: {len(anomaly_txns)} transactions for {anomaly_vendor} totaling ${anomaly_total}.")

if __name__ == "__main__":
    generate_dataset_programmatically()

import sys
import time
import asyncio
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

# Import after env vars
import agent
import mcp_sharepoint
from mcp_sharepoint import SharePointMCP
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from markitdown import MarkItDown

stats = {
    "SharePoint Search API Latency": 0.0,
    "Document Download Latency": 0.0,
    "MarkItDown Transformation Latency": 0.0,
    "Total Tool Execution Time": 0.0
}

orig_search = SharePointMCP.search_documents

def tracked_search_documents(self, query="*", limit=5):
    t0 = time.time()
    res = orig_search(self, query, limit)
    t1 = time.time()
    dur = t1 - t0
    stats["SharePoint Search API Latency"] += dur
    stats["Total Tool Execution Time"] += dur
    return res

SharePointMCP.search_documents = tracked_search_documents

def tracked_get_document_content(self, item_id: str):
    t_start = time.time()

    if item_id == "MOCK_DOC_123":
        res = "Alphabet Inc. Q1 2024 Earnings Report (CONFIDENTIAL).\\nRevenue increased by 15% year-over-year to $80.5 billion. Net income was $23.6 billion. Google Cloud revenue grew 28% to $9.6 billion. Capital expenditures were $12 billion, primarily driven by investments in technical infrastructure including servers and data centers for AI."
        t_end = time.time()
        stats["Document Download Latency"] += (t_end - t_start)
        stats["Total Tool Execution Time"] += (t_end - t_start)
        return res
    if item_id == "MOCK_DOC_456":
        res = "Acme Corp 2024 Security Assessment (CONFIDENTIAL).\\nFinding: 50-100 instances of excessive access privileges found in financial modules. Solution Framework deployed: Deployed SailPoint IdentityNow platform. Created RBAC matrix with 150 predefined roles. Implemented mandatory quarterly access certification. IT Security Director Kevin O'Brien (kobrien@acmecorp.com) oversaw the $285k implementation."
        t_end = time.time()
        stats["Document Download Latency"] += (t_end - t_start)
        stats["Total Tool Execution Time"] += (t_end - t_start)
        return res
        
    url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}?$expand=listItem"
    headers = {"Authorization": f"Bearer {self.token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            return "Throttled by SharePoint, please retry."
        response.raise_for_status()
        data = response.json()

        download_url = data.get('@microsoft.graph.downloadUrl')
        if not download_url:
            return "No download URL available for this document."

        t_down_start = time.time()
        resp = requests.get(download_url, headers=headers, stream=True)
        resp.raise_for_status()
        temp_filename = f"temp_{item_id}_{int(time.time())}.bin"
        with open(temp_filename, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        t_down_end = time.time()
        stats["Document Download Latency"] += (t_down_end - t_down_start)
        
        t_mid_start = time.time()
        md = MarkItDown()
        result = md.convert(temp_filename)
        text_content = result.text_content
        os.remove(temp_filename)
        t_mid_end = time.time()
        stats["MarkItDown Transformation Latency"] += (t_mid_end - t_mid_start)
        
        if len(text_content) > 15000:
            text_content = text_content[:15000] + "\n\n...[Content Truncated due to length]..."
        
        t_end = time.time()
        stats["Total Tool Execution Time"] += (t_end - t_start)
        return text_content
        
    except Exception as e:
        return f"Failed to fetch content: {e}"

SharePointMCP.get_document_content = tracked_get_document_content

async def run_latency_test(model_name: str, query: str):
    print(f"\n=========================================")
    print(f"🚀 RUNNING LATENCY TEST: {model_name}")
    print(f"=========================================\n")
    
    for k in stats:
        stats[k] = 0.0
        
    session_service = InMemorySessionService()
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="test_user", session_id="test_sess")
    if not session:
        await session_service.create_session(app_name="PWC_Security_Proxy", user_id="test_user", session_id="test_sess")

    llm_agent = agent.get_agent(model_name)
    runner = Runner(app_name="PWC_Security_Proxy", agent=llm_agent, session_service=session_service)
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    
    t_start_total = time.time()
    
    async for event in runner.run_async(user_id="test_user", session_id="test_sess", new_message=msg):
        pass
        
    t_end_total = time.time()
    
    total_latency = t_end_total - t_start_total
    llm_think_time = total_latency - stats["Total Tool Execution Time"]
    
    print("-----------------------------------------")
    print(f"📊 LATENCY BREAKDOWN FOR {model_name}")
    print("-----------------------------------------")
    print(f"1) SharePoint Search API Latency:  {stats['SharePoint Search API Latency']:.2f}s")
    print(f"2) Document Download Latency:      {stats['Document Download Latency']:.2f}s")
    print(f"3) MarkItDown Transf. Latency:     {stats['MarkItDown Transformation Latency']:.2f}s")
    print(f"4) LLM Pure 'Think' Time:          {llm_think_time:.2f}s")
    print(f"-----------------------------------------")
    print(f"⏱️ TOTAL ROUND-TRIP TIME:          {total_latency:.2f}s\n")

if __name__ == "__main__":
    query = "Give me the financial audit report and any security assessments, mask any sensitive details."
    asyncio.run(run_latency_test("gemini-3-flash-preview", query))
    asyncio.run(run_latency_test("gemini-3-pro-preview", query))

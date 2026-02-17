import time
import asyncio
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

class LLMTurnProfiler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.turns = []
        self.current_start = None
        self.current_turn_number = 1

    def emit(self, record):
        msg = self.format(record)
        if "Sending out request" in msg:
            self.current_start = time.time()
        elif "Response received from the model" in msg:
            if self.current_start is not None:
                duration = time.time() - self.current_start
                self.turns.append({
                    "turn": self.current_turn_number,
                    "duration": duration
                })
                self.current_turn_number += 1
                self.current_start = None

llm_profiler = LLMTurnProfiler()
# Get the root logger or the specific genai logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(llm_profiler)

import agent
import mcp_sharepoint
from mcp_sharepoint import SharePointMCP
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

tool_stats = {
    "SharePoint Search API Tool": 0.0,
    "Document Download & OCR Parsing Tool": 0.0,
}

orig_search = SharePointMCP.search_documents
orig_get = SharePointMCP.get_document_content

def tracked_search_documents(self, query="*", limit=5):
    t0 = time.time()
    res = orig_search(self, query, limit)
    t1 = time.time()
    tool_stats["SharePoint Search API Tool"] += (t1 - t0)
    return res

def tracked_get_document_content(self, item_id: str):
    t0 = time.time()
    res = orig_get(self, item_id)
    t1 = time.time()
    tool_stats["Document Download & OCR Parsing Tool"] += (t1 - t0)
    return res

SharePointMCP.search_documents = tracked_search_documents
SharePointMCP.get_document_content = tracked_get_document_content

async def run_deep_profile(model_name: str, query: str):
    llm_profiler.turns = []
    llm_profiler.current_turn_number = 1
    for k in tool_stats:
        tool_stats[k] = 0.0
        
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="PWC_Security_Proxy", user_id="test_user", session_id="test_sess")

    llm_agent = agent.get_agent(model_name)
    runner = Runner(app_name="PWC_Security_Proxy", agent=llm_agent, session_service=session_service)
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    
    t_start = time.time()
    print(f"\n=========================================")
    print(f"🔬 INITIALIZING DEEP TRACE: {model_name}")
    print(f"=========================================\n")
    
    async for event in runner.run_async(user_id="test_user", session_id="test_sess", new_message=msg):
        pass
        
    t_end = time.time()
    total_time = t_end - t_start
    
    print("-----------------------------------------")
    print(f"📊 DEEP TRACE BREAKDOWN FOR {model_name}")
    print("-----------------------------------------")
    
    total_llm_time = 0.0
    for t in llm_profiler.turns:
        print(f"[LLM Agentic Turn {t['turn']}] Network & Inference Latency: {t['duration']:.2f}s")
        total_llm_time += t['duration']
        
    print("\n[Tool Executions]")
    for tool, dur in tool_stats.items():
        print(f" -> {tool}: {dur:.4f}s")
        
    overhead = total_time - total_llm_time - sum(tool_stats.values())
    print(f"\n[Framework/SDK Sync Overhead]: {overhead:.2f}s")
    
    print("-----------------------------------------")
    print(f"⏱️ TOTAL ROUND-TRIP TIME: {total_time:.2f}s")
    print("-----------------------------------------\n")

if __name__ == "__main__":
    query = "Find the financial audit report and masking sensitive details."
    # Suppress verbose genai logs for clean console
    logging.getLogger("google.genai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # We will temporarily enable genai INFO logging just for our handler
    genai_logger = logging.getLogger("google.genai")
    genai_logger.setLevel(logging.INFO)
    genai_logger.propagate = False
    genai_logger.addHandler(llm_profiler)
    
    asyncio.run(run_deep_profile("gemini-3-flash-preview", query))
    asyncio.run(run_deep_profile("gemini-3-pro-preview", query))

"""
Performance profiling script for ADK agent - with multiple thinking levels.
"""
from __future__ import annotations

import asyncio
import os
import time
import sys
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part, GenerateContentConfig, ThinkingConfig, ThinkingLevel
from agent import root_agent

APP_NAME = "adk-drive-ae"
USER_ID = "profile-test"

async def profile_query(query: str, token: str, label: str) -> dict:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    
    start_time = time.time()
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={
            "drive_access_token": token,
            "temp:drive_access_token": token,
        },
    )
    session_init_time = time.time() - start_time
    
    content = Content(parts=[Part(text=query)], role="user")
    
    first_token_time = None
    stream_start = time.time()
    total_tokens = 0
    thoughts_tokens = 0
    text_tokens = 0
    
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content
    ):
        if first_token_time is None:
            first_token_time = time.time() - stream_start
            
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    if getattr(part, "thought", False):
                        thoughts_tokens += len(part.text.split())
                    else:
                        text_tokens += len(part.text.split())
                    total_tokens += len(part.text.split())
                    
    total_time = time.time() - stream_start
    return {
        "label": label,
        "session_init_time": session_init_time,
        "first_token_time": first_token_time,
        "total_time": total_time,
        "total_tokens": total_tokens,
        "thoughts_tokens": thoughts_tokens,
        "text_tokens": text_tokens,
    }

async def main():
    token = os.environ.get("DRIVE_ACCESS_TOKEN")
    if not token:
        try:
            import subprocess
            proc = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
            if proc.returncode == 0:
                token = proc.stdout.strip()
                os.environ["DRIVE_ACCESS_TOKEN"] = token
                print("Obtained token from gcloud.")
        except Exception:
            pass
            
    if not token:
        token = "dummy_token"
        print("Using dummy_token.")
        
    orig_config = root_agent.generate_content_config
    
    # 1. HIGH
    root_agent.generate_content_config = GenerateContentConfig(
        thinking_config=ThinkingConfig(
            include_thoughts=True,
            thinking_level=ThinkingLevel.HIGH,
        )
    )
    print("--- Phase 1: ThinkingLevel.HIGH ---")
    res_high = await profile_query("Hello, who are you and what can you do?", token, "HIGH")
    print(f"Results: {res_high}\n")
    
    # 2. MINIMAL
    root_agent.generate_content_config = GenerateContentConfig(
        thinking_config=ThinkingConfig(
            include_thoughts=True,
            thinking_level=ThinkingLevel.MINIMAL,
        )
    )
    print("--- Phase 2: ThinkingLevel.MINIMAL ---")
    res_min = await profile_query("Hello, who are you and what can you do?", token, "MINIMAL")
    print(f"Results: {res_min}\n")
    
    # 3. None (Disabled)
    root_agent.generate_content_config = None
    print("--- Phase 3: Thinking Disabled (None) ---")
    res_none = await profile_query("Hello, who are you and what can you do?", token, "None")
    print(f"Results: {res_none}\n")
    
    # Restore config
    root_agent.generate_content_config = orig_config

if __name__ == "__main__":
    asyncio.run(main())

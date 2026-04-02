import asyncio
import os

from dotenv import load_dotenv
load_dotenv()  # loads GOOGLE_GENAI_USE_VERTEXAI, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION from .env

from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

async def main():
    agent = LlmAgent(
        name="script_writer",
        model="gemini-2.5-flash",
        instruction="You are a bash script writer. Write a simple bash script that echoes 'Hello from ADK generated script!'. Do not include any markdown backticks, just output the raw code starting with #!/bin/bash"
    )
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app",
        user_id="user_1",
        session_id="session_1"
    )
    runner = Runner(
        agent=agent,
        app_name="app",
        session_service=session_service
    )
    
    content = types.Content(role='user', parts=[types.Part(text="Create the bash script now.")])
    
    events = runner.run_async(user_id="user_1", session_id="session_1", new_message=content)
    
    script_text = ""
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            script_text = event.content.parts[0].text
            break
            
    # Strip markdown fences if the model added them anyway
    if script_text.strip().startswith("```"):
        lines = script_text.strip().splitlines()
        script_text = "\n".join(lines[1:-1])

    print("Agent finished generating script. Content:")
    print("--------------------------------------------------")
    print(script_text)
    print("--------------------------------------------------")
    
    if script_text:
        script_path = "generated_script.sh"
        with open(script_path, "w") as f:
            f.write(script_text.strip() + "\n")
        os.chmod(script_path, 0o755)
        print(f"Saved into {script_path} and made executable.")
        
        # Test executing it
        print("Executing generated script:")
        print(">>>")
        os.system(f"./{script_path}")
        print("<<<")

if __name__ == "__main__":
    asyncio.run(main())

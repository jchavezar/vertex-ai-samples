import os
import sys
import time
from dotenv import load_dotenv
from google import genai

# Load project environment credentials
# (Ensure override is active so it grabs project variables from the env file)
load_dotenv(dotenv_path="../.env", override=True)
load_dotenv(dotenv_path=".env", override=True)

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "254356041555")
use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True") == "True"

print("=====================================================================")
print(f"Project context: {project_id} | Using Vertex AI: {use_vertex}")
print("=====================================================================")

# Set default command or capture from command line arguments
cmd_to_run = sys.argv[1] if len(sys.argv) > 1 else "gcloud projects get-iam-policy vtxdemos"

print(f"Preparing to execute command: '{cmd_to_run}' inside remote container...")

# Initialize Client
client = genai.Client(
    vertexai=use_vertex,
    project=project_id,
    location="global"
)

prompt = (
    "You are a test subagent verifying terminal command execution inside a secure container.\n"
    f"Run this command: '{cmd_to_run}'\n"
    "Report the output."
)

try:
    print("\n[1/3] Provisioning secure remote Linux sandbox container on Vertex AI...")
    interaction = client.interactions.create(
        agent="antigravity-preview-05-2026",
        input=prompt,
        environment="remote",
        background=True,
        timeout=300.0
    )
    print(f"Created interaction. ID: {interaction.id} | Status: {interaction.status}")
    
    print("\n[2/3] Polling sandbox status (updates every 5 seconds)...")
    attempts = 0
    while interaction.status == "in_progress" and attempts < 60:
        time.sleep(5)
        interaction = client.interactions.get(id=interaction.id)
        attempts += 1
        print(f"  Check {attempts}: status = {interaction.status}")
        
    print(f"\n[3/3] Interaction complete. Final Status: {interaction.status}")
    
    # Parse function execution step
    print("\nParsing tool output steps from API response:")
    func_calls = {}
    if hasattr(interaction, 'steps') and interaction.steps:
        for idx, step in enumerate(interaction.steps):
            if step.type == "function_call" and step.name == "run_command":
                try:
                    args = step.arguments.model_dump() if hasattr(step.arguments, 'model_dump') else step.arguments
                except Exception:
                    args = getattr(step, 'arguments', {})
                func_calls[step.id] = args
            elif step.type == "function_result" and step.name == "run_command":
                call_id = step.call_id
                args = func_calls.get(call_id, {})
                cmd_line = args.get("CommandLine", "unknown")
                
                res_val = {}
                if step.result:
                    try:
                        res_val = step.result.model_dump()
                    except Exception:
                        try:
                            res_val = step.result.dict()
                        except Exception:
                            res_val = getattr(step, 'result', {})
                            
                exit_code = res_val.get("ExitCode", 0)
                output_raw = res_val.get("Output", "")
                
                print("-" * 60)
                print(f"Executed: $ {cmd_line}")
                print(f"Exit Code: {exit_code}")
                print("-" * 60)
                print("Console STDOUT/STDERR Stream:")
                print(output_raw)
                print("-" * 60)
                
    if getattr(interaction, 'output_text', None):
        print(f"\nAgent Final Summary:\n{interaction.output_text}")
        
except Exception as e:
    print(f"\nExecution Failed: {e}")

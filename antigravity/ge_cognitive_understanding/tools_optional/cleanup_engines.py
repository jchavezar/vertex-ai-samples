import os
import google.auth
from google.cloud import aiplatform
import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = os.getenv("PROJECT_ID", "vtxdemos")
LOCATION = os.getenv("LOCATION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)

def cleanup_agents():
    print(f"Listing agents in {PROJECT_ID}/{LOCATION}...")
    agents = reasoning_engines.ReasoningEngine.list()
    
    deleted_count = 0
    request_keep = "5073323073485445106" # We verified this one is valid in GE. 
    # But wait, GE Agent ID != Reasoning Engine ID. 
    # Subagent said "Active Agent... UID: 7510397791965806592". 
    # The GE Agent ID is 5073323073485445106.
    
    keep_id = "7510397791965806592" 

    for agent in agents:
        try:
            name = agent.resource_name
            uid = name.split("/")[-1]
            display_name = getattr(agent, "display_name", "")
            
            if display_name == "GEMINIPayloadInterceptor" and uid != keep_id:
                print(f"Deleting redundant agent: {name} ({display_name})")
                agent.delete()
                deleted_count += 1
            else:
                print(f"Skipping: {name} ({display_name})")
                
        except Exception as e:
            print(f"Error processing {agent.resource_name}: {e}")

    print(f"Cleanup complete. Deleted {deleted_count} agents.")

if __name__ == "__main__":
    cleanup_agents()

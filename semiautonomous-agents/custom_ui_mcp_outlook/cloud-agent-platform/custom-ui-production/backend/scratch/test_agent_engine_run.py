import os
import google.auth
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env", override=True)
load_dotenv(override=True)

os.environ['GOOGLE_CLOUD_PROJECT'] = '254356041555'
os.environ['PROJECT_ID'] = '254356041555'

import vertexai
# Import agent_engines directly from vertexai namespace
from vertexai import agent_engines

credentials, project = google.auth.default()
vertexai.init(project="254356041555", location="us-central1")

token = os.environ.get("MS_GRAPH_TOKEN")
if not token:
    print("Warning: MS_GRAPH_TOKEN not in env.")

try:
    print("Connecting to outlook-mcp-agent-identity using agent_engines namespace...")
    remote_agent = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368")
    
    user_id = "admin@sockcop.onmicrosoft.com"
    print(f"Creating session for {user_id}...")
    session = remote_agent.create_session(user_id=user_id)
    print("Session created. ID:", session.get("id"))
    
    query = "what was my oldest email?"
    print(f"Streaming query: '{query}'...")
    
    events = remote_agent.stream_query(
        user_id=user_id,
        session_id=session.get("id"),
        message=query
    )
    
    print("\n--- Agent Stream Start ---")
    for event in events:
        print("Event:", event)
    print("--- Agent Stream End ---\n")
    
except Exception as e:
    print("Failed executing agent query stream:", e)

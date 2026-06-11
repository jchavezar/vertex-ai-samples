import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env", override=True)

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "7757233204599193600"
PROJECT_NUMBER = "254356041555"
SESSION_ID = "7908638223486681088"

vertexai.init(project=PROJECT_ID, location=LOCATION)

resource_name = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

print(f"Getting engine: {resource_name}")
try:
    engine = agent_engines.get(resource_name)
    
    print(f"Getting session: {SESSION_ID}")
    session = engine.get_session(user_id="test_user", session_id=SESSION_ID)
    print(f"Session: {session}")
    
    print("\nListing session events...")
    # Some SDKs might have list_session_events or it might be in the session object
    if hasattr(engine, 'list_session_events'):
        events = engine.list_session_events(user_id="test_user", session_id=SESSION_ID)
        print(f"Events: {events}")
    else:
        print("Engine object does not have list_session_events method.")
        
except Exception as e:
    print(f"Failed: {e}")

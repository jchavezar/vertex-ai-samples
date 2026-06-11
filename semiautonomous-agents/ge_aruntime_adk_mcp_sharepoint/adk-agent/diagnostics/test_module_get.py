import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env", override=True)

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "7757233204599193600"
PROJECT_NUMBER = "254356041555"

vertexai.init(project=PROJECT_ID, location=LOCATION)

resource_name = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

print(f"Getting engine: {resource_name}")
try:
    engine = agent_engines.get(resource_name)
    print(f"Type of engine: {type(engine)}")
    
    print("Creating session...")
    session = engine.create_session(user_id="test_user")
    print(f"Session created: {session}")
    session_id = session.id if hasattr(session, 'id') else session.get('id')
    print(f"Session ID: {session_id}")
    
    print("\nTrying to stream_query with session...")
    # Let's see if it works
    for event in engine.stream_query(
        user_id="test_user",
        session_id=session_id,
        message="Who is Jennifer Walsh?",
    ):
        print(f"Event: {event}")
except Exception as e:
    print(f"Failed: {e}")

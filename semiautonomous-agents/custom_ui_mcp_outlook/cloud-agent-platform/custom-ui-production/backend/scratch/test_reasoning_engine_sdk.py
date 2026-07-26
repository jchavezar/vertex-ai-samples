import google.auth
from vertexai.preview.reasoning_engines import ReasoningEngine

credentials, project = google.auth.default()

try:
    print("Initializing reasoning engine connection...")
    engine = ReasoningEngine("projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368")
    print("Success!")
    
    # Try calling create_session with user_id
    user_id = "admin@sockcop.onmicrosoft.com"
    print(f"Creating session for {user_id}...")
    session_res = engine.create_session(user_id=user_id)
    print("Session created successfully! Details:")
    print(session_res)
    print("Session type:", type(session_res))
    print("Session methods:", [m for m in dir(session_res) if not m.startswith("_")])
    
except Exception as e:
    print("Failed to query reasoning engine directly:", e)

import vertexai
from vertexai import agent_engines
import os
from dotenv import load_dotenv

load_dotenv(override=True)
vertexai.init(project=os.environ['GOOGLE_CLOUD_PROJECT'], location=os.environ.get('DEPLOY_LOCATION', 'us-central1'))
engine = agent_engines.get(os.environ['AGENT_ENGINE_RESOURCE'])

print("Creating session...")
sess = engine.create_session(user_id='test_state_delta', state={'my_var': 'initial'})
sid = sess.get('id') if isinstance(sess, dict) else sess.id
print("Session ID:", sid)
print("Session Initial State:", sess.get('state') if isinstance(sess, dict) else sess.state)

print("\nRunning stream_query with state_delta to update my_var and add new_key...")
events = []
try:
    # We pass state_delta as a kwarg to stream_query!
    for event in engine.stream_query(
        user_id='test_state_delta', 
        session_id=sid, 
        message='Hi', 
        state_delta={'my_var': 'updated_via_delta', 'new_key': 'hello_from_client'}
    ):
        events.append(event)
    print("Stream query completed successfully!")
except Exception as e:
    print("Stream query failed:", e)

print("\nFetching session to verify if state was updated by the delta...")
try:
    sess_fetched = engine.get_session(user_id='test_state_delta', session_id=sid)
    print("Fetched State:", sess_fetched.get('state') if isinstance(sess_fetched, dict) else sess_fetched.state)
except Exception as e:
    print("Failed to fetch session:", e)

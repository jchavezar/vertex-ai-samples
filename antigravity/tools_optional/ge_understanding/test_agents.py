import vertexai
from vertexai.preview import reasoning_engines
import json

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

INTERCEPTOR_ID = "projects/254356041555/locations/us-central1/reasoningEngines/2018117308899131392"
CONTEXT_DEMO_ID = "projects/254356041555/locations/us-central1/reasoningEngines/8084466006967189504"

def test_interceptor():
    print(f"\n--- Testing Interceptor: {INTERCEPTOR_ID} ---")
    try:
        remote_agent = reasoning_engines.ReasoningEngine(INTERCEPTOR_ID)
        # The interceptor expects 'request_json' in the payload if queried via SDK .query()
        # because the internal query method calls streaming_agent_run_with_events
        # Actually in my 'deploy_interceptor.py' I defined:
        # def query(self, payload: dict) -> str:
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": "Hello Interceptor"}]}]
        }
        response = remote_agent.query(payload=payload)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Interceptor Test Failed: {e}")

def test_context_demo():
    print(f"\n--- Testing Context Demo: {CONTEXT_DEMO_ID} ---")
    try:
        remote_agent = reasoning_engines.ReasoningEngine(CONTEXT_DEMO_ID)
        # def query(self, prompt: str = "", **kwargs) -> dict:
        response = remote_agent.query(prompt="Who am I?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Context Demo Test Failed: {e}")

if __name__ == "__main__":
    test_interceptor()
    test_context_demo()

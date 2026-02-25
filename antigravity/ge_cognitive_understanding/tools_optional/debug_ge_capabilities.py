
from vertexai.preview import reasoning_engines
import vertexai
import inspect

PROJECT_ID = "254356041555"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://sockcop-staging-bucket"
ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/6960440767449923584"

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

def inspect_engine():
    try:
        remote_agent = reasoning_engines.ReasoningEngine(ENGINE_ID)
        print(f"Successfully loaded agent: {ENGINE_ID}")
        print(f"Dir(remote_agent): {dir(remote_agent)}")
        
        # Check for query/stream methods
        if hasattr(remote_agent, 'query'):
            print("Has 'query' method")
            print(f"Query Signature: {inspect.signature(remote_agent.query)}")
            
        if hasattr(remote_agent, 'stream_query'):
            print("Has 'stream_query' method")
        elif hasattr(remote_agent, 'stream'):
            print("Has 'stream' method")
            
    except Exception as e:
        print(f"Error inspecting engine: {e}")

if __name__ == "__main__":
    inspect_engine()

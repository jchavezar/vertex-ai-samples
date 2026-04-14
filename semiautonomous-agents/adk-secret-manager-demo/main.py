from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.cloud import secretmanager
import os
import asyncio

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Secret Manager client
secret_client = secretmanager.SecretManagerServiceClient()

def get_secret(secret_id: str) -> str:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return "DEMO_SECRET_VALUE_FALLBACK"
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    try:
        response = secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret: {e}")
        return f"Error: {e}"

def secure_data_fetch(query: str) -> str:
    """Fetches sensitive data using a secret API key from Secret Manager."""
    # Fetch secret
    secret_val = get_secret("demo-api-key")
    return f"Fetched data for '{query}' using secret API key (val length: {len(secret_val)})."

# Define Agent
agent = LlmAgent(
    name="secret_agent",
    model="gemini-2.5-flash",
    instruction="You are a secure data assistant. Use the tool to fetch data when asked about sensitive information.",
    tools=[secure_data_fetch]
)

runner = InMemoryRunner(agent=agent, app_name="secret_demo_app")

@app.post("/chat")
async def chat(message: str):
    async def event_generator():
        user_id = "user_123"
        session_id = "session_456"
        
        try:
            await runner.session_service.create_session(
                app_name="secret_demo_app",
                user_id=user_id,
                session_id=session_id
            )
        except Exception as e:
            print(f"Session exists or error: {e}")
            
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=message)])
            ):
                # Check if event has content parts
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and event.content.parts:
                    text = event.content.parts[0].text
                    if text:
                        yield f"data: {text}\n\n"
                
                # Also yield final response signal if needed, or just let it end.
                if event.is_final_response():
                     yield "data: [DONE]\n\n"
                     
        except Exception as e:
            yield f"data: Error: {e}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # Use port 8001 to avoid conflict with gemma-stratos backend
    uvicorn.run(app, host="0.0.0.0", port=8001)

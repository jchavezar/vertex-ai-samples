import asyncio
from google.adk.services.vertex_ai_session import VertexAiSessionService
from vertexai import init

async def test():
    init(project="vtxdemos", location="global")
    svc = VertexAiSessionService(reasoning_engine_id="8424072895690342400") # Sample ID, just to test class loading
    try:
        sess = await svc.create_session(app_name="test_app", user_id="default_user", session_id="testsessionid123")
        print("Success:", sess.id)
    except Exception as e:
        print("Failed create:", e)

asyncio.run(test())

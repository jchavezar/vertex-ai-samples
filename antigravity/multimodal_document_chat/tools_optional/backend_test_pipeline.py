import asyncio
import os
import vertexai
from pipeline.agents import process_document_pipeline, _create_page_extractor
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION")
)

async def main():
    service = InMemorySessionService()
    try:
        with open("/usr/local/google/home/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/multimodal_document_chat/docs/Sample-ISS-Ch10-Sample-Industry 1.pdf", "rb") as f:
            pdf_bytes = f.read()

        chunk = {"pdf_bytes": pdf_bytes, "start_page": 1}
        agent = _create_page_extractor(chunk, 1)
        
        session_id = "test_sess"
        await service.create_session(user_id="system", session_id=session_id, app_name="test", state={})
        
        runner = Runner(agent=agent, session_service=service, app_name="test")
        content = types.Content(role="user", parts=[types.Part.from_text(text="Extract entities from this page.")])
        
        async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
             if event.is_final_response():
                  print("Final Event Parts:", event.content.parts)
        
        sess = await service.get_session(user_id="system", session_id=session_id, app_name="test")
        print("SESS STATE:", sess.state)
        print("SESS MESSAGES:", sess.messages)
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

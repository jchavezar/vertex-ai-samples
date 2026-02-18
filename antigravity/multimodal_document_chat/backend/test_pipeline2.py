import asyncio
import os
import vertexai
from pipeline.agents import _create_page_extractor, _process_single_page
from google.adk.auth.session_service import FileUserSessionService
from google.genai import types

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION")
)

async def main():
    service = FileUserSessionService()
    try:
        with open("/usr/local/google/home/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/docs/Sample-ISS-Ch10-Sample-Industry 1.pdf", "rb") as f:
            pdf_bytes = f.read()

        chunk = {"pdf_bytes": pdf_bytes, "start_page": 1}
        agent = _create_page_extractor(chunk, 1)
        
        session_id = "test_sess"
        res = await _process_single_page(agent, service, "test", session_id, asyncio.Semaphore(1))
        
        print(f"Entities found: {len(res)}")
        for r in res:
             print("page_num:", r.page_number)
             for e in r.entities:
                  print(" - ", e.content_description[:50])
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

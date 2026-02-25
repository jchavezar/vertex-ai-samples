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
        # Use a local test.pdf if present, otherwise generate a dummy for testing
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "test.pdf")
        
        if not os.path.exists(pdf_path):
            print("No test.pdf found, creating a fictional dummy...")
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 21 >>\nstream\nBT /F1 12 Tf 100 700 Td (Fictional Data) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n285\n%%EOF\n")
        
        with open(pdf_path, "rb") as f:
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

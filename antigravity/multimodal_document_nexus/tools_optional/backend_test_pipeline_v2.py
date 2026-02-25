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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "sample_fictional.pdf")
        
        # Create it if it doesn't exist
        if not os.path.exists(pdf_path):
             with open(pdf_path, "wb") as f:
                 f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 21 >>\nstream\nBT /F1 12 Tf 100 700 Td (Fictional Data) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n285\n%%EOF\n")

        with open(pdf_path, "rb") as f:
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

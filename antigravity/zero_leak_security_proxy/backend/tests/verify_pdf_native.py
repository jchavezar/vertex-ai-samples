
import os
import base64
from google.genai import Client
from google.genai import types
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

def verify_pdf_native():
    client = Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    
    # Path to a sample PDF
    pdf_path = "/usr/local/google/home/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/zero_leak_security_proxy/docs/08_HR_Compensation_Analysis_FY2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    print(f"Reading PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    prompt = "Analyze this PDF visually. List the key sections and any specific tables or charts you see. Then, suggest 3 professional modifications to the 'Compensation' section while preserving the existing corporate tone."
    
    # In google-genai, we pass bytes or URIs
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                prompt
            ]
        )
        print("\n=== GEMINI NATIVE PDF RESPONSE ===\n")
        print(response.text)
    except Exception as e:
        print(f"Error during PDF generation: {e}")

if __name__ == "__main__":
    verify_pdf_native()

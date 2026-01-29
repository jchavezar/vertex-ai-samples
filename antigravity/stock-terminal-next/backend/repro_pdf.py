import os
import base64
from google.genai import Client, types
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

def test_raw_pdf():
    client = Client(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        vertexai=True
    )
    pdf_path = "factset_10k_sample.pdf"
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    print(f"File size: {len(pdf_bytes)}")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                        types.Part.from_text(text="What is this document about?")
                    ]
                )
            ]
        )
        print("Response successful!")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_pdf()

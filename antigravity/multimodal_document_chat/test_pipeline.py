import requests
import uuid

def test_pipeline():
    # Make sure to place a sample pdf at 'sample.pdf' for this script to run accurately
    url = "http://localhost:8001/chat"
    session_id = str(uuid.uuid4())
    
    # Create a dummy PDF if none exists
    with open("sample.pdf", "wb") as f:
        # Just write some placeholder text, pypdf2 might complain but we'll see
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 21 >>\nstream\nBT /F1 12 Tf 100 700 Td (Hello World) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n285\n%%EOF\n")

    
    print("Testing pipeline...")
    with open("sample.pdf", "rb") as pdf_file:
        files = {"files": ("sample.pdf", pdf_file, "application/pdf")}
        data = {
            "message": "Summarize this document based on the specific tables in the text.",
            "session_id": session_id
        }
        
        response = requests.post(url, data=data, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("Response:", result.get("response"))
            print("Pipeline Data Entities:", len(result.get("pipeline_data", [])))
            for entity in result.get("pipeline_data", []):
                print(f" - [{entity['entity_type']}] {entity['content_description'][:50]}")
        else:
            print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    test_pipeline()

import requests
import json
import base64

def test_pdf_chat():
    url = "http://localhost:8001/chat"
    
    pdf_path = "factset_10k_sample.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    payload = {
        "messages": [{"role": "user", "content": "What is this document about?"}],
        "sessionId": "test_pdf_session",
        "model": "gemini-2.5-flash",
        "file": f"data:application/pdf;base64,{pdf_b64}"
    }
    
    print("\n--- TESTING PDF ---")
    print("Sending request with PDF...")
    try:
        response = requests.post(url, json=payload, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Stream received:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('0:'):
                        text = json.loads(decoded_line[2:])
                        print(text, end="", flush=True)
            print("\nVerification successful!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

def test_img_chat():
    url = "http://localhost:8001/chat"
    
    image_path = "test_image.png"
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
    
    payload = {
        "messages": [{"role": "user", "content": "What is in this image?"}],
        "sessionId": "test_img_session",
        "model": "gemini-2.5-flash",
        "file": f"data:image/png;base64,{img_b64}"
    }
    
    print("\n--- TESTING IMAGE ---")
    print("Sending request with Image...")
    try:
        response = requests.post(url, json=payload, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Stream received:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('0:'):
                        text = json.loads(decoded_line[2:])
                        print(text, end="", flush=True)
            print("\nVerification successful!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_pdf_chat()
    test_img_chat()

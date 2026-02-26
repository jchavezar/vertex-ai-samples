import requests
import json

def test_chat():
    url = "http://localhost:8005/api/chat"
    payload = {
        "messages": [
            {"role": "user", "content": "Perform a forensic audit on the Q4 transaction set. Focus on high-value outliers."}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, stream=True)
        print(f"Status Code: {response.status_code}")
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received: {decoded_line}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()

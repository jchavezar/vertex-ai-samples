import requests
import json
import sys

def test_youtube_chat():
    url = "http://localhost:8001/chat"
    
    # Using a technical YouTube URL (NVIDIA Blackwell architecture)
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    payload = {
        "messages": [{"role": "user", "content": "What is in this video? Summary in 2 lines."}],
        "sessionId": "verify_youtube_session",
        "model": "gemini-2.5-flash",
        "youtubeUrl": youtube_url
    }
    
    print(f"--- TESTING YOUTUBE CHAT ---")
    print(f"URL: {youtube_url}")
    
    try:
        response = requests.post(url, json=payload, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Stream output:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # Look for text protocol (0:...)
                    if decoded_line.startswith('0:'):
                        try:
                            text = json.loads(decoded_line[2:])
                            print(text, end="", flush=True)
                        except:
                            pass
            print("\nDone.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_youtube_chat()

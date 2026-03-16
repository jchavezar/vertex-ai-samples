import uvicorn
from main import app
import threading
import time
import requests
import json

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="error")

def run_test():
    time.sleep(3)
    try:
        url = "http://localhost:8002/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer mock_token"
        }
        data = {
            "messages": [{"role": "user", "content": "What is the latest news on SpaceX? Use the google search tool."}]
        }
        print("Sending request to server...")
        response = requests.post(url, headers=headers, json=data, stream=True)
        print(f"Status: {response.status_code}")
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
    except Exception as e:
        print(f"Test error: {e}")
    
    # Send kill signal to our own process
    import os
    import signal
    os.kill(os.getpid(), signal.SIGINT)

if __name__ == "__main__":
    t = threading.Thread(target=run_test)
    t.start()
    run_server()

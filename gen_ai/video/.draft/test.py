import time
import threading
from flask import Flask, request

app = Flask(__name__)

def ack_immediately(request):
  # do something with the request
  time.sleep(100)
  # ack the request
  return 'ack'

@app.route('/', methods=['POST'])
def index():
  # get the request
  data = request.get_json()
  # ack the request immediately
  thread = threading.Thread(target=ack_immediately, kwargs={"post_data": data})
  thread.start
  # return a response
  return {"message": "Accepted"}, 200

if __name__ == "__main__":
    # Dev only: run "python main.py" and open http://localhost:8080
    app.run(host="localhost", port=8080, debug=True)

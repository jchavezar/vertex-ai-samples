import os
import vertexai
from dotenv import load_dotenv
from agent import video_expert_agent
from vertexai.agent_engines import AdkApp
from vertexai.preview.reasoning_engines.utils import _get_registered_operations

load_dotenv(os.path.expanduser("~/.env"))
vertexai.init(project=os.getenv("PROJECT_ID", "vtxdemos"), location="us-central1")

app = AdkApp(agent=video_expert_agent)
methods = _get_registered_operations(app)
print("Registered Methods:", methods)
for m in methods:
    print(getattr(app, m))

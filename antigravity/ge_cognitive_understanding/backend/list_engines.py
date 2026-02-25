import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env")

import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(project=os.getenv("PROJECT_ID"), location=os.getenv("LOCATION", "us-central1"))
engines = reasoning_engines.ReasoningEngine.list()
for e in engines:
    print(f"{e.resource_name} - {getattr(e, 'display_name', 'Unknown')}")

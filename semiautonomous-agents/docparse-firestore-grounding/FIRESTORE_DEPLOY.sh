#!/usr/bin/env bash
# Run this in Cloud Shell
cd ~/cloudshell_open/vertex-ai-samples/semiautonomous-agents/docparse-firestore-grounding

# Ensure we're using gcloud user credentials
gcloud auth application-default login --no-launch-browser 2>/dev/null || true

pip install uv --quiet
uv run --with "google-cloud-aiplatform[adk,agent_engines]" \
  --with google-cloud-firestore \
  --with google-genai \
  --with requests \
  python3 -c "
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.')))
from firestore_agent import root_agent

vertexai.init(project='vtxdemos', location='us-central1', staging_bucket='gs://vtxdemos-staging-agent-engine')

app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
remote = agent_engines.create(
    agent_engine=app,
    display_name='docparse-firestore',
    description='Firestore + PDF grounding',
    requirements=['google-cloud-aiplatform[adk,agent_engines]', 'google-cloud-firestore', 'google-genai', 'requests'],
    extra_packages=['firestore_agent'],
    env_vars={'GOOGLE_CLOUD_LOCATION': 'global', 'GOOGLE_GENAI_USE_VERTEXAI': 'true', 'GOOGLE_CLOUD_PROJECT': 'sharepoint-wif', 'FIRESTORE_COLLECTION': 'docparse_chunks', 'AGENT_MODEL': 'gemini-2.5-flash', 'AGENT_TOP_K': '20'})

print(f'\n✅ Deployed: {remote.resource_name}')
"

#%%
import vertexai
from agent import root_agent
from vertexai import agent_engines

vertexai.init(project="vtxdemos",staging_bucket="gs://vtxdemos-staging")

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-genai",
        "google-cloud-aiplatform[agent_engines]"
    ]
)

#%%
from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
session = app.create_session(user_id="u_123")

for event in app.stream_query(
        user_id="u_123",
        session_id=session.id,
        message="how are you bro?",
):
    print(event)


#%%

import vertexai
import os
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from dotenv import load_dotenv


GOOGLE_CLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GOOGLE_CLOUD_LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
STAGING_BUCKET = f"gs://{GOOGLE_CLOUD_PROJECT}-agent-engine-deploy"
AGENT_DISPLAY_NAME="Currency Analyst"

vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

#app.register_operations()

agent_config =  {
    "agent_engine" : app,
    "display_name" : AGENT_DISPLAY_NAME,
    "requirements" : [
        "google-genai",
        "google-cloud-aiplatform[agent_engines,adk]",
    ],
    "extra_packages" : [
        "agent.py",
    ],
}

existing_agents=list(agent_engines.list(filter='display_name="Currency Analyst"'))

if existing_agents:
    print(f"Number of existing agents found for {AGENT_DISPLAY_NAME}:" + str(len(list(existing_agents))))


if existing_agents:
    #update the existing agent
    remote_app = existing_agents[0].update(**agent_config)
else:
    #create a new agent
    remote_app = agent_engines.create(**agent_config)

#%%

import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)
engines = reasoning_engines.ReasoningEngine.list()
engine = reasoning_engines.ReasoningEngine(engines[0].resource_name)
session = engine.create_session(user_id="jesus",session_id="session1")

#%%
from google.genai import types
output = engine.streaming_agent_run_with_events(
    session_id="session1",
    message=types.Content(
        parts=[types.Part(text="hey how are you?")],
        role="user",
    ).model_dump_json(),
)

#%%

agent_context = '{"message":{"role":"user","parts":[{"text":"Hey how are you?"}]},"events":[{"content":{"role":"user","parts":[{"text":"how were you built ?"}]},"author":"AgentSpace_root_agent"},{"content":{"role":"model","parts":[{"functionCall":{"name":"agentspaceak","args":{"question":"How were you built?"},"id":"14076651604820872102"}}]},"invocation_id":"14076651604820871801","author":"AgentSpace_root_agent","id":"14076651604820872102"}]}'


for response in engine.streaming_agent_run_with_events(agent_context):
    for event in response.events:
        print(event.content.parts[0].text)
# for event in engine.streaming_agent_run_with_events(
#         session_id="session1",
#         message=types.Content(
#             parts=[types.Part(text="hey how are you?")],
#             role="user",
#         ).model_dump_json(),
# ):
    print(event)

#%%
engine = reasoning_engines.ReasoningEngine("projects/254356041555/locations/us-central1/reasoningEngines/8662471573107638272")
output = engine.agent_run(
    session_id="session1",
    message=types.Content(
        parts=[types.Part(text="How are you?")],
        role="user",
    ).model_dump_json(),
)

#%%
import vertexai
from vertexai import agent_engines

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)
ae = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/7904037248360775680")

for responses in ae.streaming_agent_run_with_events(request_json="how are you?"):
    print(responses)
    for event in responses["events"]:
        print(event)
        print(event["content"]["parts"][0]["text"])



#%%
agent_engines.delete(resource_name="projects/254356041555/locations/us-central1/reasoningEngines/7904037248360775680", force=True)
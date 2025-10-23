#%%
import asyncio
import os
import vertexai
from google.genai import types
from vertexai.preview.reasoning_engines import A2aAgent
from agent import qna_agent
from agent_card import qna_agent_card
from agent_executor import QnAAgentExecutor

#%%
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
BUCKET_NAME = "vtxdemos-staging"
BUCKET_URI = f"gs://{BUCKET_NAME}"

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET_URI)

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=types.HttpOptions(
        api_version="v1beta1", base_url=f"https://{LOCATION}-aiplatform.googleapis.com/"
    ),
)


a2a_agent = A2aAgent(agent_card=qna_agent_card, agent_executor_builder=QnAAgentExecutor)
a2a_agent.set_up()

#%%
remote_a2a_agent = client.agent_engines.create(
    # The actual agent to deploy
    agent=a2a_agent,
    config={
        # Display name shown in the console
        "display_name": a2a_agent.agent_card.name,
        # Description for documentation
        "description": a2a_agent.agent_card.description,
        # Python dependencies needed in Agent Engine
        "requirements": [
            "google-cloud-aiplatform[agent_engines,adk]>=1.112.0",
            "a2a-sdk >= 0.3.4",
        ],
        "extra_packages": [
            "agent_executor.py",
            "agent.py",
            "agent_card.py",
            "utils.py",
        ],
        "source_directory": ".",
        # Http options
        "http_options": {
            "base_url": f"https://{LOCATION}-aiplatform.googleapis.com",
            "api_version": "v1beta1",
        },
        # Staging bucket
        "staging_bucket": BUCKET_URI,
    },
)

#%%
async def send_message():
    # remote_a2a_agent = [agent.resource_name for agent in client.agent_engines.list(filter='display_name="Q&A Agent"')]
    # remote_a2a_agent = client.agent_engines.get(remote_a2a_agent[0])
    remote_a2a_agent_resource_name = remote_a2a_agent.resource_name
    config = {"http_options": {"base_url": f"https://{LOCATION}-aiplatform.googleapis.com"}}

    remote_agent = client.agent_engines.get(
        name=remote_a2a_agent_resource_name,
        config=config,
    )

    remote_a2a_agent_card = await remote_agent.handle_authenticated_agent_card()
    print(f"Agent: {remote_a2a_agent_card.name}")
    print(f"URL: {remote_a2a_agent_card.url}")
    print(f"Skills: {[s.description for s in remote_a2a_agent_card.skills]}")
    print(f"Examples: {[s.examples for s in remote_a2a_agent_card.skills][0]}")

    # Create a message
    message_data = {
        # Unique ID for this message (for tracking)
        "messageId": f"msg-{os.urandom(8).hex()}",
        # Role identifies the sender (user vs agent)
        "role": "user",
        # The actual message content
        # Parts can include text, files, or structured data
        "parts": [{"kind": "text", "text": "What is the capital of Italy?"}],
    }

    # Invoke the agent
    response = await remote_agent.on_message_send(**message_data)
    print(response)

    for chunk in response:
        print(chunk[0].artifacts[0].parts[0])
        print(type(chunk[0].artifacts[0].parts[0]))
        print(chunk[0].artifacts[0].parts[0].root.text)


asyncio.run(send_message())
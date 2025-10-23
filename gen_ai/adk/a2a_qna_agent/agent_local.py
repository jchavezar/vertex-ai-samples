import os
import vertexai
from google.genai import types
from vertexai.preview.reasoning_engines import A2aAgent
from pprint import pprint
from IPython.display import Markdown, display
import asyncio
import time

from agent_card import qna_agent_card
from agent_executor import QnAAgentExecutor
from utils import build_get_request, build_post_request

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

async def main():
    a2a_agent = A2aAgent(agent_card=qna_agent_card, agent_executor_builder=QnAAgentExecutor)
    a2a_agent.set_up()

    print("--- Testing Agent Card ---" )
    request = build_get_request(None)
    response = await a2a_agent.handle_authenticated_agent_card(
        request=request, context=None
    )
    pprint(response)

    print("\n--- Sending Query ---" )
    message_data = {
        "message": {
            "messageId": f"msg-{os.urandom(8).hex()}",
            "content": [{"text": "What is the capital of France?"}],
            "role": "ROLE_USER",
        },
    }
    request = build_post_request(message_data)
    response = await a2a_agent.on_message_send(request=request, context=None)
    pprint(response)

    task_id = response["task"]["id"]
    print(f"The Task ID is: {task_id}")

    print("\n--- Getting Response (Polling) --- ")
    while True:
        task_data = {"id": task_id}
        request = build_get_request(task_data)
        response = await a2a_agent.on_get_task(request=request, context=None)
        pprint(response)

        state = response["status"]["state"]
        if state in ["TASK_STATE_COMPLETED", "TASK_STATE_FAILED"]:
            print(f"Task finished with state: {state}")
            if state == "TASK_STATE_COMPLETED":
                if "artifacts" in response:
                    for artifact in response["artifacts"]:
                        if artifact["parts"] and "text" in artifact["parts"][0]:
                            print(f"**Answer**:\n {artifact['parts'][0]['text']}")
                        else:
                            print("Could not extract text from artifact parts.")
                else:
                    print("'artifacts' key not found in the completed response.")
            else:
                print("Task failed.")
            break
        print("Task not yet completed, waiting...")
        await asyncio.sleep(1) # Use asyncio.sleep for async context
if __name__ == "__main__":
    asyncio.run(main())

#%%
import logging
import asyncio
from vertexai import agent_engines
import vertexai
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("google.api_core.bidi").setLevel(logging.DEBUG)
logging.getLogger("google.auth.transport.grpc").setLevel(logging.DEBUG)
from google.api_core import exceptions as gcp_exceptions


vertexai.init(project="vtxdemos", location="us-central1")

agent_engine_display_name = "image_object_detector"
agent_resource_name = [agent.resource_name for agent in agent_engines.list(filter=f'display_name={agent_engine_display_name}')][0]
deployed_agent = agent_engines.get(agent_resource_name)
print(deployed_agent)

print(agent_resource_name)

async def send_message(prompt: str):
    print("enter async call")
    stream = deployed_agent.async_stream_query(
        message=prompt,
        user_id="jesus13",
    )
    try:
        # Force the stream to try and get the first item
        first_event = await stream.__anext__()

        # If the first event succeeds, print it and continue the loop
        print("-" * 80)
        print(first_event)
        print("-" * 80)

        async for event in stream:
            print("-" * 80)
            print(event)
            print("-" * 80)

    except gcp_exceptions.GoogleAPICallError as e:
        # This catches common exceptions like PermissionDenied, NotFound, etc.
        print("Caught GoogleAPICallError (Permissions/Status Check):")
        print(f"Status Code: {e.code}")
        print(f"Details: {e.details}")
        print(e)
    except Exception as e:
        # General fallback exception
        print("Caught General Exception:")
        print(repr(e)) # Use repr() to get a more detailed representation
        print(e)

asyncio.run(send_message("What do you see?"))

#%%

async def try_message(prompt: str):
    events = []
    async for event in deployed_agent.async_stream_query(
            user_id="u_123",
            session_id="2324",
            message=prompt,
    ):
        events.append(event)

    # The full event stream shows the agent's thought process
    print("--- Full Event Stream ---")
    for event in events:
        print(event)

    # For quick tests, you can extract just the final text response
    final_text_responses = [
        e for e in events
        if e.get("content", {}).get("parts", [{}])[0].get("text")
           and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
    ]
    if final_text_responses:
        print("\n--- Final Response ---")
        print(final_text_responses[0]["content"]["parts"][0]["text"])

asyncio.run(try_message("What do you see?"))
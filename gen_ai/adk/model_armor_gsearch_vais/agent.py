import asyncio
import os
import json
import logging
from google.genai import types
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.cloud import modelarmor_v1
from google.adk.tools import ToolContext
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID

# Initialize session_service once globally to persist state across generate_content calls
global_session_service = InMemorySessionService()

async def setup_session_and_runner(agent):
    session = await global_session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    if session:
        print(f"Retrieved existing session: {SESSION_ID}")
    else:
        session = await global_session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        print(f"Created new session: {SESSION_ID}")

    runner = Runner(agent=agent, app_name=APP_NAME, session_service=global_session_service)
    return session, runner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project = "vtxdemos"
location = "us-central1"

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = project
os.environ["GOOGLE_CLOUD_LOCATION"] = location

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

def guardrail_check_tool(prompt: str, tool_context: ToolContext) -> str:
    """
    Checks the prompt for PII using Model Armor and updates session state.
    Returns a simple string indicating PII detection status (e.g., "PII_DETECTED" or "NO_PII_DETECTED").
    """
    logging.info("[Callback] Guardrail check tool called with prompt: %s", prompt)
    session_state = tool_context.state

    # Store the initial user query ONLY if we are not currently awaiting PII confirmation.
    if not session_state.get("awaiting_pii_confirmation"):
        session_state["initial_user_query"] = prompt
        logger.info(f"Stored initial user query for new flow: {session_state['initial_user_query']}")
    else:
        logger.info(f"Skipping initial_user_query storage, awaiting PII confirmation. Current prompt: '{prompt}'")

    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt

    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project}/locations/us/templates/model-armor-demo",
        user_prompt_data=user_prompt_data,
    )

    logger.info("[Callback] Calling Model Armor sanitize_user_prompt...")
    response = client.sanitize_user_prompt(request=request)

    pii_found = False
    sdp_filter_result = response.sanitization_result.filter_results.get("sdp")
    if sdp_filter_result and sdp_filter_result.sdp_filter_result.deidentify_result:
        # Correctly check the deidentify_result's match_state for PII
        if sdp_filter_result.sdp_filter_result.deidentify_result.match_state.name == "MATCH_FOUND":
            pii_found = True

    # Return a simple string for the LLM to process
    if pii_found:
        logger.info(f"PII detected by Model Armor for '{prompt}': True")
        return "PII_DETECTED"
    else:
        logger.info(f"PII detected by Model Armor for '{prompt}': False")
        return "NO_PII_DETECTED"

guardrail_agent = LlmAgent(
    name="guardrail_check",
    description="This is a global checker tool to detect PII",
    instruction="""Use the tool to check if the prompt/original_query has PII. Return "PII_DETECTED" if PII is found, otherwise return "NO_PII_DETECTED".""",
    model="gemini-2.0-flash-001",
    tools=[guardrail_check_tool]
)

google_search_agent = LlmAgent(
    name="internet_search",
    description="This is a tool for surfacing information from the internet",
    instruction="""
    Use google_search to get information. The query for the search tool should come from `session_state['initial_user_query']`
    which contains the original user request. Provide a concise summary of the search results.
    """,
    model="gemini-2.0-flash-001",
    tools=[google_search]
)

root_agent = LlmAgent(
    name="init_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a query validation and fulfillment agent. Your main goal is to fulfill user queries after a PII check.

    **Workflow Steps (Strict Order):**

    1.  **Check for Pending PII Confirmation:**
        *   Examine `session_state['awaiting_pii_confirmation']`.
        *   If `session_state['awaiting_pii_confirmation']` is `True` (meaning you previously asked for user confirmation regarding PII):
            *   The user's current input is a response to the PII warning.
            *   If the user's current input (case-insensitive) is 'yes':
                *   Respond to the user: 'Okay, I will proceed to use other relevant agents to fulfill the original query.'
                *   **Crucially, retrieve the original query that triggered the PII warning from `session_state['initial_user_query']`.**
                *   Then, immediately call the `internet_search` tool with the content of `session_state['initial_user_query']` to fulfill the request.
                *   After successfully executing the search, clear the PII state by setting `session_state['awaiting_pii_confirmation'] = False` and `session_state['initial_user_query'] = None`.
            *   Else if the user's current input (case-insensitive) is 'no':
                *   Respond to the user: 'Understood. The query will not be processed.'
                *   Clear the PII state by setting `session_state['awaiting_pii_confirmation'] = False` and `session_state['initial_user_query'] = None`.
            *   Else (if the user's input is neither 'yes' nor 'no' when PII confirmation is awaited):
                *   Respond to the user: 'Please respond with "yes" or "no" to continue or cancel the query processing.'
            *   **IMPORTANT**: In this specific state (awaiting PII confirmation), do NOT proceed to step 2 or call `guardrail_check` on the current user input ("yes" or "no"). Your task is only to process the confirmation.

    2.  **Process a New Query (No PII Confirmation Pending):**
        *   If `session_state['awaiting_pii_confirmation']` is `False` or not set (meaning this is a new, unconfirmed query):
            *   Call the `guardrail_check` tool with the *entire current user input*.
            *   **Based on the exact string output from the `guardrail_check` tool:**
            *   If the tool's output is exactly 'PII_DETECTED':
                *   Respond to the user: 'Your query has PII. Do you want to continue?'
                *   Set `session_state['awaiting_pii_confirmation'] = True`.
                *   **DO NOT proceed with internet search yet; wait for user confirmation.**
            *   Else if the tool's output is exactly 'NO_PII_DETECTED':
                *   Respond to the user: 'No PII detected. Proceeding with your request.'
                *   Retrieve the original query from `session_state['initial_user_query']` (which `guardrail_check` tool would have already stored).
                *   Immediately call the `internet_search` tool with the content of `session_state['initial_user_query']`.
                *   After fulfilling, clear the PII state by setting `session_state['awaiting_pii_confirmation'] = False` and `session_state['initial_user_query'] = None`.
            *   Else (unexpected tool output):
                *   Respond to the user: 'An unexpected error occurred during PII check. Please try again.'

    Always ensure clear and concise communication with the user at each step.
    """,
    tools=[AgentTool(guardrail_agent), AgentTool(google_search_agent)],
)

async def generate_content(prompt: str):
    session, runner = await setup_session_and_runner(root_agent)

    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = None
    async for event in events:
        print(event)
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    return final_response

# To test the flow:
# async def main():
#     print("--- Turn 1: PII Query ---")
#     await generate_content("Hi my ssn is 453-55-3049 search for information on internet")
#     print("\n--- Turn 2: PII Confirmation (yes) ---")
#     await generate_content("yes")
#     print("\n--- Turn 3: PII Confirmation (no) ---")
#     await generate_content("no")
#     print("\n--- Turn 4: Invalid PII Confirmation ---")
#     await generate_content("what?")
#     print("\n--- Turn 5: Non-PII Query ---")
#     await generate_content("what is the capital of France?")

# if __name__ == "__main__":
#     asyncio.run(main())
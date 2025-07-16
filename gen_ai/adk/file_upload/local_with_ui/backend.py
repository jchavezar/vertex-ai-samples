import logging
from dotenv import load_dotenv
load_dotenv()
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import mimetypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID


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

root_agent=Agent(
    name="root_agent",
    model="gemini-1.5-flash",
    description="Your and AGI",
    instruction="Answer any question"
)

async def generate_content(prompt: str, file_path: str = None):
    session, runner = await setup_session_and_runner(root_agent)

    parts = [types.Part(text=prompt)]
    if file_path:
        print("capicy")
        print(file_path)
        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"  # Default MIME type if detection fails

        with open(file_path, "rb") as f:
            file_data = f.read()
        # Upload the file to the Files API

        # Add the file to the parts list for the prompt
        parts.append(
            types.Part.from_bytes(data=file_data, mime_type=mime_type)
        )
    content = types.Content(role='user', parts=parts)
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = None
    async for event in events:
        print(event)
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    return final_response
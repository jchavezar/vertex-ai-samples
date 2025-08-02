import base64
import io
import sys
import pandas as pd
from io import BytesIO
from google.genai import types
from google.adk.events import Event
from typing import AsyncGenerator
from google.adk.events import Event
from typing_extensions import override
from google.adk.agents import Agent, BaseAgent
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext

afc_limits = types.AutomaticFunctionCallingConfig(maximum_remote_calls=20)
content_config = types.GenerateContentConfig(
    automatic_function_calling=afc_limits,
)

async def extract_data_callback(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
):
    # If the request comes from Agentspace the file attached in the payload is wrapped as an artifact.
    artifacts_in_context = await callback_context._invocation_context.artifact_service.list_artifact_keys(
        app_name=callback_context._invocation_context.app_name,
        user_id=callback_context._invocation_context.user_id,
        session_id=callback_context._invocation_context.session.id,
    )
    # If the request comes locally any file attached is considered inside of the llm_request.
    artifacts_in_request = [True for content in llm_request.contents if content.role == 'user' for part in content.parts if not part.text]
    callback_context.state["artifacts_in_context_names"] = artifacts_in_context

    # As an Artifact
    if len(artifacts_in_context) > 0:
        for artifact in artifacts_in_context:
            print("uno", file=sys.stdout)
            _artifact = await callback_context.load_artifact(artifact)
            print("dos", file=sys.stdout)
            if _artifact["inlineData"]["mimeType"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                print("tres", file=sys.stdout)
                decoded_data = base64.b64decode(_artifact["inlineData"]["data"])
                excel_file_object = io.BytesIO(decoded_data)
                print("cuatro", file=sys.stdout)
                print(excel_file_object)
                try:
                    df = pd.read_excel(excel_file_object)
                    print("cinco", file=sys.stdout)
                    markdown_table = df.to_markdown(index=False)
                    print("seis", file=sys.stdout)
                    print(markdown_table)
                    llm_request.contents[0].parts.append(types.Part.from_text(text=f"Document {artifact}: {markdown_table}"))
                except Exception as excel_read_err:
                    return LlmResponse(
                        content=types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"There was an error: {excel_read_err}")]
                        )
                    )

        return None

    # As an LLMRequest
    elif len(artifacts_in_request) > 0:
        callback_context.state["artifacts_in_request"] = artifacts_in_request
        for content_num, content in enumerate(llm_request.contents):
            if content.role == 'user':
                for part_num, part in enumerate(content.parts):
                    if part.text:
                        continue
                    elif part.inline_data and part.inline_data.data:
                        if part.inline_data.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                            decoded_data = BytesIO(part.inline_data.data)
                            try:
                                df = pd.read_excel(decoded_data)
                                markdown_table = df.to_markdown(index=False)
                                llm_request.contents[content_num].parts[part_num] = types.Part.from_text(text=markdown_table)
                            except Exception as excel_read_err:
                                return LlmResponse(
                                    content=types.Content(
                                        role="user",
                                        parts=[types.Part(text=f"Error processing Excel file: {excel_read_err}")],
                                    )
                                )
        return None

    #%% Primary Instruction if a Document has not been uploaded yet.
    else:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"Hello! This is a file analyzer, add your xlsx first (only Excel is supported)")],
            )
        )


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a AGI",
    instruction="""
    Respond Any question.
    """,
    before_model_callback=extract_data_callback,
)

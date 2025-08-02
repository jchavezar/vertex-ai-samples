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

async def extract_data_callback(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
):
    artifacts_in_context = await callback_context._invocation_context.artifact_service.list_artifact_keys(
        app_name=callback_context._invocation_context.app_name,
        user_id=callback_context._invocation_context.user_id,
        session_id=callback_context._invocation_context.session.id,
    )
    artifacts_in_request = [True for content in llm_request.contents if content.role == 'user' for part in content.parts if not part.text]

    print(llm_request)
    if len(artifacts_in_context) > 0:
        callback_context.state["artifacts_in_context_names"] = artifacts_in_context
        return None
    elif len(artifacts_in_request) > 0:
        markdowns = []
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
    else:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"Hello! This is a file analyzer, add your xlsx first (only Excel is supported)")],
            )
        )


#     for artifact in artifacts_in_request:
    #         excel_file_object = io.BytesIO(artifact.part.inline_data.data)
    #         try:
    #             df = pd.read_excel(excel_file_object)
    #             markdown_table = df.to_markdown(index=False)
    #             for llm_request in llm_request.contents:
    #             markdowns.append(markdown_table)
    #         except Exception as excel_read_err:
    #             return f"Error processing Excel file: {excel_read_err}"
    #     return None
    # else:
    #     return LlmResponse(
    #         content=types.Content(
    #             role="model",
    #             parts=[types.Part(text=f"Hello! This is a file analyzer, add your xlsx first (only Excel is supported)")],
    #         )
    #     )


async def read_file(tool_context: ToolContext):
    artifacts_in_context_names = tool_context.state.get("artifacts_in_context_names", [])
    artifacts_in_request = tool_context.state.get("artifacts_in_request", [])
    print("$"*80)
    print(artifacts_in_request)
    markdowns = []
    if artifacts_in_context_names:
        for artifact in artifacts_in_context_names:
            _artifact = await tool_context.load_artifact(artifact)
            if _artifact["inlineData"]["mimeType"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                decoded_data = base64.b64decode(_artifact["inlineData"]["data"])
                excel_file_object = io.BytesIO(decoded_data)
                try:
                    df = pd.read_excel(excel_file_object)
                    markdown_table = df.to_markdown(index=False)
                    markdowns.append(markdown_table)
                except Exception as excel_read_err:
                    return f"Error processing Excel file: {excel_read_err}"
            else:
                return "The file is not Excel format."

    elif artifacts_in_request:
        for artifact in artifacts_in_request:
            excel_file_object = io.BytesIO(artifact.part.inline_data.data)
            try:
                df = pd.read_excel(excel_file_object)
                markdown_table = df.to_markdown(index=False)
                markdowns.append(markdown_table)
            except Exception as excel_read_err:
                return f"Error processing Excel file: {excel_read_err}"

    return markdowns
    #
    # try:
    #     artifacts = await tool_context.list_artifacts()
    #     print("new", file=sys.stdout)
    #     print(artifacts)
    #     artifact = await tool_context.load_artifact(filename=artifacts[-1])
    #     print("from read_file", file=sys.stdout)
    #     print(artifact, file=sys.stdout)
    #     if artifact["inlineData"]["mimeType"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
    #         print("before decode", file=sys.stdout)
    #         decoded_data = base64.b64decode(artifact["inlineData"]["data"])
    #         print(decoded_data, file=sys.stdout)
    #         print("-"*80, file=sys.stdout)
    #         excel_file_object = io.BytesIO(decoded_data)
    #         print(excel_file_object, file=sys.stdout)
    #         print("#"*80)
    #         try:
    #             # THIS IS THE CRITICAL LINE THAT NEEDS OPENPYXL
    #             df = pd.read_excel(excel_file_object)
    #             print("working - pandas read successful!", file=sys.stdout) # Clarified message
    #             markdown_table = df.to_markdown(index=False)
    #             return markdown_table
    #         except Exception as excel_read_err:
    #             print(f"ERROR reading Excel file with pandas in tool: {excel_read_err}", file=sys.stdout)
    #             return f"Error processing Excel file: {excel_read_err}. Please ensure it's a valid .xlsx file and required libraries are installed."
    # except Exception as e:
    #     return f"There was an error reading the file: {e}"



root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a AGI",
    instruction="""
    Use your `read_file` tool to read the file and use it as a context.

    Respond Any question
    """,
    before_model_callback=extract_data_callback,
    tools=[read_file]
)

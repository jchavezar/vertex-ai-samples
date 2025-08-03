import base64
import io
import sys
import pandas as pd
from io import BytesIO
from google.genai import types
from google.adk.agents import Agent
from google.adk.models import LlmRequest, LlmResponse
from google.adk.agents.callback_context import CallbackContext

afc_limits = types.AutomaticFunctionCallingConfig(maximum_remote_calls=20)
content_config = types.GenerateContentConfig(
    automatic_function_calling=afc_limits,
)

async def extract_data_callback(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
):
    processed_excel_markdown = callback_context.state.get("processed_excel_markdown")
    handled_excel_in_this_turn = False

    artifacts_in_context = await callback_context._invocation_context.artifact_service.list_artifact_keys(
        app_name=callback_context._invocation_context.app_name,
        user_id=callback_context._invocation_context.user_id,
        session_id=callback_context._invocation_context.session.id,
    )
    callback_context.state["artifacts_in_context_names"] = artifacts_in_context

    if len(artifacts_in_context) > 0:
        for num, artifact_key in enumerate(artifacts_in_context):
            if callback_context.state.get(f"markdown_from_artifact_{artifact_key}"):
                markdown_table = callback_context.state[f"markdown_from_artifact_{artifact_key}"]
                for content_idx, content in enumerate(llm_request.contents):
                    if content.role == 'user':
                        for part_idx, part in enumerate(content.parts):
                            if part.inline_data and part.inline_data.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                if part.inline_data.display_name == artifact_key or (artifact_key in part.inline_data.display_name):
                                    llm_request.contents[content_idx].parts[part_idx] = types.Part.from_text(text=f"Document {artifact_key}: {markdown_table}")
                                    handled_excel_in_this_turn = True
                                    break
                        if handled_excel_in_this_turn:
                            break
                continue

            _artifact = await callback_context.load_artifact(artifact_key)
            if _artifact["inlineData"]["mimeType"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                decoded_data = base64.b64decode(_artifact["inlineData"]["data"])
                excel_file_object = io.BytesIO(decoded_data)
                try:
                    df = pd.read_excel(excel_file_object)
                    markdown_table = df.to_markdown(index=False)
                    callback_context.state[f"markdown_from_artifact_{artifact_key}"] = markdown_table
                    callback_context.state["processed_excel_markdown"] = markdown_table
                    handled_excel_in_this_turn = True

                    for content_idx, content in enumerate(llm_request.contents):
                        if content.role == 'user':
                            for part_idx, part in enumerate(content.parts):
                                if part.inline_data and part.inline_data.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                    if part.inline_data.display_name == artifact_key or (artifact_key in part.inline_data.display_name):
                                        llm_request.contents[content_idx].parts[part_idx] = types.Part.from_text(text=f"Document {artifact_key}: {markdown_table}")
                                        break
                            if handled_excel_in_this_turn:
                                break

                except Exception as excel_read_err:
                    return LlmResponse(
                        content=types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"Error processing artifact {artifact_key}: {excel_read_err}")]
                        )
                    )
        if handled_excel_in_this_turn:
            return None

    for content_num, content in enumerate(llm_request.contents):
        if content.role == 'user':
            for part_num, part in enumerate(content.parts):
                if part.inline_data and part.inline_data.data:
                    if part.inline_data.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        if processed_excel_markdown:
                            llm_request.contents[content_num].parts[part_num] = types.Part.from_text(text=processed_excel_markdown)
                            handled_excel_in_this_turn = True
                        else:
                            decoded_data = BytesIO(part.inline_data.data)
                            try:
                                df = pd.read_excel(decoded_data)
                                markdown_table = df.to_markdown(index=False)
                                callback_context.state["processed_excel_markdown"] = markdown_table
                                handled_excel_in_this_turn = True
                                llm_request.contents[content_num].parts[part_num] = types.Part.from_text(text=markdown_table)
                            except Exception as excel_read_err:
                                return LlmResponse(
                                    content=types.Content(
                                        role="user",
                                        parts=[types.Part(text=f"Error processing Excel file: {excel_read_err}")],
                                    )
                                )
                        break
            if handled_excel_in_this_turn:
                break

    if handled_excel_in_this_turn:
        return None

    if not processed_excel_markdown and not handled_excel_in_this_turn:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"Hello! This is a file analyzer, add your xlsx first (only Excel is supported)")],
            )
        )

    return None


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a AGI",
    instruction="""
    Respond Any question.
    """,
    before_model_callback=extract_data_callback,
)
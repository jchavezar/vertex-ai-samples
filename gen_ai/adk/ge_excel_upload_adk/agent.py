import base64
import sys
from io import BytesIO
from google.genai import types
from markitdown import MarkItDown
from google.adk.agents import Agent
from google.adk.models import LlmRequest, LlmResponse
from google.adk.agents.callback_context import CallbackContext
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

afc_limits = types.AutomaticFunctionCallingConfig(maximum_remote_calls=20)
content_config = types.GenerateContentConfig(
    automatic_function_calling=afc_limits,
)

md = MarkItDown()

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
                excel_file_object = BytesIO(decoded_data)
                try:
                    result = md.convert(excel_file_object)
                    callback_context.state[f"markdown_from_artifact_{artifact_key}"] = result.text_content
                    callback_context.state["processed_excel_markdown"] = result.text_content
                    handled_excel_in_this_turn = True

                    for content_idx, content in enumerate(llm_request.contents):
                        if content.role == 'user':
                            for part_idx, part in enumerate(content.parts):
                                if part.inline_data and part.inline_data.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                    if part.inline_data.display_name == artifact_key or (artifact_key in part.inline_data.display_name):
                                        llm_request.contents[content_idx].parts[part_idx] = types.Part.from_text(text=f"Document {artifact_key}: This is the content of the uploaded Excel file:\n{result.text_content}")
                                        break
                                else:
                                    llm_request.contents[content_idx].parts.append(types.Part.from_text(text=f"Document {artifact_key}: This is the content of the uploaded Excel file:\n{result.text_content}"))
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
            else:
                print("Not an excel artifact", file=sys.stdout)
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
                                result = md.convert(decoded_data)
                                callback_context.state["processed_excel_markdown"] = result.text_content
                                handled_excel_in_this_turn = True
                                llm_request.contents[content_num].parts[part_num] = types.Part.from_text(text=f"This is the content of the uploaded Excel file:\n{result.text_content}")
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
    You main task is to analyze or do whatever is being asked about a file (xlsx) that is being uploaded,
    you have callback function that transforms the excel (xlsx) into markdown and store it in session as `processed_excel_markdown`
    use that as a content of the file and answer any question about it. 
    """,
    before_model_callback=extract_data_callback,
)
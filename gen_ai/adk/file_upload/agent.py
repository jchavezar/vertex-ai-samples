# from google.adk.tools import FunctionTool
# from google.adk.agents import Agent
# from google.genai import types
# from google.adk.tools.tool_context import ToolContext
# from google.adk.agents.callback_context import CallbackContext
#
# async def augment_data(tool_context: ToolContext):
#     """
#
#     :param extraction_data: full data extracted as it is from the file
#     :return:
#     """
#     print("#"*80)
#     print(tool_context)
#     try:
#         available_files = await tool_context.list_artifacts()
#         print(available_files)
#         te = await tool_context.load_artifact(filename=available_files[0])
#         print(te)
#     except Exception as e:
#         te = e
#     return f"data is {te}"
#
# # async def secondary_action(tool_context: ToolContext):
# #     try:
# #         available_files = await tool_context.list_artifacts()
# #         te = await tool_context.load_artifact(filename=available_files[0])
# #         print(te)
# #         return te
# #
# #     except Exception as e:
# #         available_files = e
# #     print("#"*80)
# #     print(available_files)
# #     return str(available_files)
#
# root_agent = Agent(
#     name="DataAugmenterAgent",
#     description="You are an AI Assistant answer any question",
#     model="gemini-2.0-flash-001",
#     instruction="""
#     You are receiving a file (if you dont have it ask for it) and your task is to extract everything from it as it is, if it contains
#     images, annotate them (describe as deeply as possible) and use your tool `augment_data` to add a string.
#
#     Respond with the entire string output of your tool
#         """,
#     tools=[FunctionTool(func=augment_data)],
# )


# from google.adk.tools import FunctionTool
# from google.adk.agents import Agent
# from google.genai import types
# from google.adk.tools.tool_context import ToolContext
# from google.adk.agents.callback_context import CallbackContext
#
# # --- Cloud Trace Integration ---
# from opentelemetry import trace
# from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor
# from openinference.instrumentation.langchain import LangChainInstrumentor # Even if not using LangChain directly, this can help capture some ops
# import google.cloud.trace_v2 as cloud_trace_v2
# import google.auth
# import os # To get project ID from environment variables
#
# def setup_cloud_trace(tool_context: ToolContext):
#     """Initializes OpenTelemetry for Google Cloud Trace."""
#     project_id = "vtxdemos"
#     credentials, _ = google.auth.default()
#     trace.set_tracer_provider(TracerProvider())
#     cloud_trace_exporter = CloudTraceSpanExporter(
#         project_id=project_id,
#         client=cloud_trace_v2.TraceServiceClient(
#             credentials=credentials.with_quota_project(project_id),
#         ),
#     )
#     trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(cloud_trace_exporter))
#     # Instrument common libraries that OpenInference supports.
#     # While your tool isn't a LangChain chain directly, this might still capture some underlying operations.
#     LangChainInstrumentor().instrument()
#     print("Cloud Trace instrumentation initialized.")
#     print(tool_context)
#     print(dir(tool_context))
#
# # Call the setup function at the beginning of your script
# # Replace 'your-gcp-project-id' with your actual GCP project ID,
# # or better, get it from an environment variable.
# PROJECT_ID = "vtxdemos"
# setup_cloud_trace(PROJECT_ID)
# # --- End Cloud Trace Integration ---
#
# async def augment_data(tool_context: ToolContext):
#     """
#     :param extraction_data: full data extracted as it is from the file
#     :return:
#     """
#     # Use the current tracer to create a span for this function
#     tracer = trace.get_tracer(__name__)
#     with tracer.start_as_current_span("augment_data_execution") as span:
#         print("#"*80)
#         span.add_event("Starting augment_data function") # Log an event within the span
#         print(tool_context)
#         try:
#             available_files = await tool_context.list_artifacts()
#             print(available_files)
#             span.set_attribute("available_files_count", len(available_files)) # Add an attribute to the span
#             te = await tool_context.load_artifact(filename=available_files[0])
#             print(te)
#             span.add_event(f"Loaded artifact: {available_files[0]}")
#         except Exception as e:
#             te = e
#             span.set_status(trace.Status(trace.StatusCode.ERROR, description=str(e))) # Set span status to ERROR on exception
#             span.record_exception(e) # Record the exception in the span
#
#         result_string = f"data is {te}"
#         span.set_attribute("result_data_summary", result_string[:100]) # Add summary of result
#         span.add_event("Finished augment_data function")
#         return result_string
#
# root_agent = Agent(
#     name="DataAugmenterAgent",
#     description="You are an AI Assistant answer any question",
#     model="gemini-2.0-flash-001",
#     instruction="""
#     User your tool to answer any question
#         """,
#     tools=[FunctionTool(func=augment_data)],
# )
#%%
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="Answer any question, ALWAYS use your artifacts from load_artifacts tool",
    tools=[load_artifacts],
)

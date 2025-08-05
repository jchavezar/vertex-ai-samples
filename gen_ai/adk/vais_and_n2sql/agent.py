import json
import sys

import google.auth
from typing_extensions import override
from google.genai import types
from google.adk.agents import Agent
from google.adk.models import LlmRequest
from google.adk.tools.bigquery.config import WriteMode
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.planners import BuiltInPlanner
from vais_and_n2sql.sql_schema import api_schema
from vais_and_n2sql.prompt import instruction_prompt_ds_v1
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.load_artifacts_tool import LoadArtifactsTool

from google.adk.tools.bigquery.config import BigQueryToolConfig

afc_limits = types.AutomaticFunctionCallingConfig(maximum_remote_calls=20)
content_config = types.GenerateContentConfig(
    automatic_function_calling=afc_limits,
)

my_planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)


bigquery_toolset = BigQueryToolset(
    bigquery_tool_config=tool_config
)

bigquery_agent = Agent(
    name="bigquery_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        " SQL queries."
    ),
    instruction=f"""
        You are a data science agent with access to several BigQuery tools
        Make use of those tools to answer root_agent questions.
        Use this table: vtxdemos.demos.fintech_data,
        
        this is the schema:
        {api_schema}
    """,
    tools=[bigquery_toolset]
)

code_agent = Agent(
    name="code_agent",
    model="gemini-2.5-flash",
    instruction=instruction_prompt_ds_v1,
    code_executor=VertexAiCodeExecutor(
        resource_name="projects/254356041555/locations/us-central1/extensions/1642756408682217472",
        optimize_data_file=True,
        stateful=True,
    ),
)

# async def after_function(
#         callback_context: CallbackContext,
# ):
#     llm_request: LlmRequest = callback_context._invocation_context.llm_request
#     artifacts = await callback_context.list_artifacts()
#     print(artifacts)
#     print(artifacts)
#     print(artifacts)
#     print(artifacts)
#     print(artifacts)
#     if len(artifacts) > 0:
#         if llm_request.contents and llm_request.contents[-1].parts:
#             for item in artifacts:
#                 artifact = await callback_context.load_artifact(item)
#                 print(artifact)
#                 llm_request.contents.append(
#                     types.Content(
#                         role='user',
#                         parts=[
#                             artifact,
#                         ],
#                     )
#                 )


class CustomLoadArtifactsTool(LoadArtifactsTool):
    @override
    async def _append_artifacts_to_llm_request(
            self, *, tool_context: ToolContext, llm_request: LlmRequest
    ):
        artifact_names = await tool_context.list_artifacts()
        if not artifact_names:
            return

        # Tell the model about the available artifacts.
        llm_request.append_instructions([f"""You have a list of artifacts:
  {json.dumps(artifact_names)}

  When the user asks questions about any of the artifacts, you should call the
  `load_artifacts` function to load the artifact. Do not generate any text other
  than the function call.
  """])

        # Attach the content of the artifacts if the model requests them.
        # This only adds the content to the model request, instead of the session.
        if llm_request.contents and llm_request.contents[-1].parts:
            function_response = llm_request.contents[-1].parts[0].function_response
            if function_response and function_response.name == 'load_artifacts':
                if function_response.response:
                    artifact_names = function_response.response['artifact_names']
                    for artifact_name in artifact_names:
                        artifact = await tool_context.load_artifact(artifact_name)
                    print(artifact, file=sys.stdout)
                    if artifact is not None:
                        llm_request.contents.append(
                            types.Content(
                                role='user',
                                parts=[
                                    types.Part.from_text(
                                        text=f'Artifact {artifact_name} is:'
                                    ),
                                    artifact,
                                ],
                            )
                        )
load_artifacts = CustomLoadArtifactsTool()

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are AGI",
    instruction="""
    Use bigquery_agent tool as grounding to any inquiry about fintech related.
    Use code_agent tool as method to create charts.
    After code_agent *ALWAYS* Use the tool `load_artifacts` tool to display all artifacts created in the current user session.
    With that respond any question.
    """,
    planner=my_planner,
    tools=[AgentTool(bigquery_agent), AgentTool(code_agent), load_artifacts],
    # after_agent_callback=after_function
)
import json
import logging
import os
import sys

from dotenv import load_dotenv
load_dotenv(verbose=True)
from google import genai
from google.genai import types
from typing import override, AsyncGenerator
from google.adk.agents import LlmAgent, BaseAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from google.cloud import bigquery
from google.adk.tools import function_tool
from google.adk.tools.url_context_tool import url_context as adk_url_context_tool
from google.adk.planners import built_in_planner
from .prompts import sql_query_prompt

bq_client = bigquery.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT")
)

gem_client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1"
)

def bigquery_call(sql_query: str):
    print(sql_query)
    df = bq_client.query_and_wait(sql_query).to_dataframe()
    print(df.head(10))
    df.to_csv("gs://vtxdemos-datasets-public/large-date/data.csv", index=False)
    return {"data": df.to_markdown(), "rows": len(df), "data_link_uri": "https://storage.googleapis.com/vtxdemos-datasets-public/large-date/data.csv"}


class CustomAgent(BaseAgent):
    sql_generator_agent: LlmAgent
    sql_executor_agent: LlmAgent

    def __int__(
            self,
            name: str,
            sql_generator_agent: LlmAgent,
            sql_executor_agent: LlmAgent,

    ):

        super().__init__(
            name=name,
            sql_generator_agent=sql_generator_agent,
            sql_executor_agent=sql_executor_agent,
        )

    @override
    async def _run_async_impl(
      self, ctx: InvocationContext
  ) -> AsyncGenerator[Event, None]:

        print("$"*80)
        print(ctx.session.events)
        print("--------")

        for event in ctx.session.events:
            if event.content.role == "user":
                ctx.session.state["original_query"] = event.content.parts[0].text


        logger.info(f"[{self.name}] Starting Analysis workflow.")
        async for event in self.sql_generator_agent.run_async(ctx):
            yield event

        sql_query = ctx.session.state.get("sql_query", None).replace("```sql", "").replace("```", "")
        print(f"SQL_QUERY: {sql_query}")

        async for event in self.sql_executor_agent.run_async(ctx):

            should_terminate = False
            for part in event.content.parts:
                if part.function_response:

                    response_data = part.function_response.response

                    state_changes = {
                        "data_link_uri": response_data.get("data_link_uri"),
                        "rows": response_data.get("rows")
                    }

                    markdown_data = response_data.get("data", "No data returned.")
                    artifact_delta = {
                        "query_results_markdown": types.Part(text=markdown_data)
                    }

                    ctx.session.state.update(state_changes)
                    if event.actions:
                        event.actions.state_delta.update(state_changes)
                        event.actions.artifact_delta.update(artifact_delta)

                    if response_data.get("rows") > 100:
                        should_terminate = True
            yield event

            if should_terminate:
                yield Event(author=self.name, content=types.Content(parts=[types.Part(text="The result is too large to display, but I have saved it.")]))

sql_generator_agent = LlmAgent(
    name="sql_generator_agent",
    model="gemini-2.5-flash",
    description="You are an SQL AI Expert",
    instruction=sql_query_prompt,
    tools=[adk_url_context_tool],
    output_key='sql_query',
)

sql_executor_agent = LlmAgent(
    name="sql_executor_agent",
    model="gemini-2.5-flash-lite",
    instruction="""
    Run the {{sql_query}} using your tool `bigquery_call`
    and respond the with the results the {{original_query}}
    
    Besides your respond, share the `data_link_uri` and number of `rows`.
    """,
    tools=[function_tool.FunctionTool(bigquery_call)]
)



orchestrator_agent = LlmAgent(
    name="sql_executer_agent",
    model="gemini-2.5-flash",
    description="You are an Agentic Orchestrator",
    instruction=
    """
     Analyze the query and use your next agent to gather information.
     
    """,
    tools=[function_tool.FunctionTool(bigquery_call)],
    planner=built_in_planner.BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0
        )
    )
)


root_agent = CustomAgent(
    name="root_agent",
    sql_generator_agent=sql_generator_agent,
    sql_executor_agent=sql_executor_agent,
)

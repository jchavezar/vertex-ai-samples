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
from google.adk.events import Event, EventActions
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
    tool_calling_agent: LlmAgent

    def __init__(
            self,
            name: str,
            sql_generator_agent: LlmAgent,
            tool_calling_agent: LlmAgent,
    ):
        super().__init__(
            name=name,
            sql_generator_agent=sql_generator_agent,
            tool_calling_agent=tool_calling_agent,
        )

    @override
    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        for event in ctx.session.events:
            if event.content.role == "user":
                ctx.session.state["original_query"] = event.content.parts[0].text

        logger.info(f"[{self.name}] Running SQL Generator.")
        async for event in self.sql_generator_agent.run_async(ctx):
            yield event

        logger.info(f"[{self.name}] Running Tool-Calling Agent.")
        response_data = None
        async for event in self.tool_calling_agent.run_async(ctx):
            yield event
            for part in event.content.parts:
                if part.function_response:
                    response_data = part.function_response.response

        if not response_data:
            yield Event(author=self.name, content=types.Content(parts=[types.Part(text="Sorry, I could not retrieve data.")]))
            return

        state_changes = {
            "data_link_uri": response_data.get("data_link_uri"),
            "rows": response_data.get("rows")
        }
        markdown_data = response_data.get("data", "No data returned.")
        num_rows = response_data.get("rows", 0)

        final_text_response = (
            f"I found {num_rows} results and have saved the full data as an artifact."
        )

        yield Event(
            author=self.name,
            content=types.Content(parts=[
                # Part at index 0: The text message for the chat UI
                types.Part(text=final_text_response),
                # Part at index 1: The data for the artifact
                types.Part(text=markdown_data)
            ]),
            actions=EventActions(
                state_delta=state_changes,
                # "query_results" points to the content part at index 1
                artifact_delta={"query_results": 1}
            )
        )

sql_generator_agent = LlmAgent(
    name="sql_generator_agent",
    model="gemini-2.5-flash",
    instruction=sql_query_prompt,
    output_key='sql_query',
)

tool_calling_agent = LlmAgent(
    name="tool_calling_agent",
    model="gemini-2.5-flash-lite",
    instruction="You must call the `bigquery_call` tool using the `sql_query` from the context. Do not add any other text or summary.",
    tools=[function_tool.FunctionTool(bigquery_call)]
)

root_agent = CustomAgent(
    name="root_agent",
    sql_generator_agent=sql_generator_agent,
    tool_calling_agent=tool_calling_agent,
)
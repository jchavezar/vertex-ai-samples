import logging
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)
from google import genai
from google.genai import types
from typing import override, AsyncGenerator
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from google.cloud import bigquery
from google.adk.tools import function_tool
from google.adk.tools.url_context_tool import url_context as adk_url_context_tool
from google.adk.planners import built_in_planner

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
    sql_query_checker_agent: LlmAgent
    sql_executer_agent: LlmAgent

    def __int__(
            self,
            name: str,
            sql_generator_agent: LlmAgent,
            sql_query_checker_agent: LlmAgent,
            sql_executer_agent: LlmAgent,

    ):
        super().__init__(
            name=name,
            sql_generator_agent=sql_generator_agent,
            sql_query_checker_agent=sql_query_checker_agent,
            sql_executer_agent=sql_executer_agent,
        )

    @override
    async def _run_async_impl(
      self, ctx: InvocationContext
  ) -> AsyncGenerator[Event, None]:

        logger.info(f"Agent: {self.name} starting a thread...")
        async for event in self.sql_generator_agent.run_async(ctx):
            yield event

        sql_query = ctx.session.state.get("sql_query")

        if sql_query:
            async for event in self.sql_query_checker_agent.run_async(ctx):
                logger.info(f"Agent: {self.name} Executing sql_query_checker_agent...")
                logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event

        curated_sql_query = ctx.session.state.get("curated_sql_query")

        if curated_sql_query:
            async for event in self.sql_executer_agent.run_async(ctx):
                logger.info(f"Agent: {self.name} Executing sql_executer_agent...")
                logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event



sql_generator_agent = LlmAgent(
    name="sql_generator_agent",
    model="gemini-2.5-flash-lite",
    description="You are an SQL AI Expert",
    instruction="""
    Objective:
        Generate SQL query for BigQuery
    
    Dataset_id.Table_id: 
        vtxdemos.demos_us.reviews_synthetic_data_1
        
    
    Schema:
        responseid: (STRING) Unique identifier for the NPS response.
        nps_nps_group: (STRING) NPS group (e.g., Promoter, Passive, Detractor).
        nps: (INTEGER) NPS score as a string (e.g., '10', '6').
        company_name: (STRING) Name of the company associated with the feedback.
        division: (STRING) Division within the company (e.g., S&P Global Market Intelligence).
        consolidateregion: (STRING) Consolidated geographical region (e.g., EMEA, LATAM, APAC). Convert 'NaN' or '(Blank)' from raw data to an empty string '' in the JSON.
        date_iso: (DATE) Date of the feedback in 'YYYY-MM-DD' format to be compatible with BigQuery's DATE type. (DATA YEAR 2025)
        strategic_company: (STRING) Indicates if the company is strategic. 'Yes' from raw data remains 'Yes'. Convert 'NaN' from raw data to an empty string '' in the JSON.
        nps_verbatim_combine: (STRING) Combined verbatim feedback from the NPS response. Convert 'NaN' from raw data to an empty string '' in the JSON.
        mistake_applied: (BOOLEAN) Indicates if a mistake was applied to this feedback. Convert 'Yes' from raw data to true, and 'NaN' to false in the JSON.
    """,
    output_key='sql_query'
)

sql_query_checker_agent = LlmAgent(
    name="sql_query_checker_agent",
    model="gemini-2.5-flash",
    description="You are a sql query syntax AI validator.",
    instruction=
    """
        ## Context:
        Please access and use the content from the following URLs to inform your response:
        - https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
        - https://cloud.google.com/bigquery/docs

        Your task is to validate and correct BigQuery Standard SQL queries based on the information from these URLs.

        **Instructions:**
        1.  **Validate Syntax Only**: Use the web page content to check for syntactical correctness (e.g., keywords, function syntax, clause structure).
        *   **Ignore Values**: Do not validate column names, `dataset.table` IDs, or specific data values; focus solely on the SQL syntax.
        2.  **Correct if Necessary**: If the SQL query has syntax errors, correct it according to the documentation. When correcting, **reuse all original values** (e.g., column names, table names, literal strings/numbers).
        3.  **Return Original**: If the SQL query is syntactically correct, return the *original query* without any changes.

        ## Query:
        original_query: {{sql_query}}

        **Output:**
        Provide ONLY the raw SQL query string (curated_sql_query).
        Absolutely no explanations, no introductory text, no conversational remarks, and no markdown code blocks.
        The output must be *only* the SQL query, and nothing else.
        
        Tell me where you find the content to validate.
    """,
    output_key='curated_sql_query',
    tools=[adk_url_context_tool],
    planner=built_in_planner.BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0
        )
    )
)

sql_executer_agent = LlmAgent(
    name="sql_executer_agent",
    model="gemini-2.5-flash",
    description="You are an Agentic Orchestrator",
    instruction=
    """
     Use your {{curated_sql_query}} for your `bigquery_call` tool.
     
     From the tool response:
     
     **IF** the number of rows is more than 1000 **THEN** Agreggate the data, do a summary and tell so, expose the
     data_link_uri and the number of rows.
     
     **ELSE** just respond the query.
     
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
    sql_query_checker_agent=sql_query_checker_agent,
    sql_executer_agent=sql_executer_agent,
)

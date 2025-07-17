import google.auth
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.bigquery.config import WriteMode
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.code_executors import BuiltInCodeExecutor
from vais_and_n2sql.prompt import instruction_prompt_ds_v1
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery import BigQueryCredentialsConfig

application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

bigquery_agent = Agent(
    name="bigquery_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        " SQL queries."
    ),
    instruction="""
        You are a data science agent with access to several BigQuery tools
        Make use of those tools to answer root_agent questions.
        Use this table: vtxdemos.demos.fintech_data
    """,
    tools=[bigquery_toolset]
)

code_agent = Agent(
    name="code_agent",
    model="gemini-2.5-flash",
    instruction=instruction_prompt_ds_v1,
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are AGI",
    instruction="""
    Use bigquery_agent tool as grounding to any inquiry about fintech related.
    Use code_agent tool as method to create charts.
    With that respond any question.
    """,
    tools=[AgentTool(bigquery_agent), AgentTool(code_agent)],
)
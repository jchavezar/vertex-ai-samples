import os
from google.adk.agents import Agent
from google.adk.tools import agent_tool
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.tools import google_search
from google.adk.tools.bigquery import BigQueryToolset
import google.auth
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.tools.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode

CREDENTIALS_TYPE = None
internal_doc_datastore_id = f"projects/{os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")}/locations/global/collections/default_collection/dataStores/rag-esg-advisory-dataset"

rag_tool = VertexAiSearchTool(
    data_store_id=internal_doc_datastore_id
)

internet_search_tool = google_search

## MCP Toolkit - BigQuery

tool_config = BigQueryToolConfig(write_mode=WriteMode.ALLOWED)
if CREDENTIALS_TYPE == AuthCredentialTypes.OAUTH2:
    # Initiaze the tools to do interactive OAuth
    credentials_config = BigQueryCredentialsConfig(
        client_id=os.getenv("OAUTH_CLIENT_ID"),
        client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
    )
elif CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
    # Initialize the tools to use the credentials in the service account key.
    creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
    credentials_config = BigQueryCredentialsConfig(credentials=creds)
else:
    # Initialize the tools to use the application default credentials.
    application_default_credentials, _ = google.auth.default()
    credentials_config = BigQueryCredentialsConfig(
        credentials=application_default_credentials
    )

bigquery_toolset = BigQueryToolset(credentials_config=credentials_config,   tool_filter=[
    'list_dataset_ids',
    'get_dataset_info',
    'list_table_ids',
    'get_table_info',
    'execute_sql',
])

# End of MCP Toolkit - BigQuery

rag_agent_tool = Agent(
    name="rag_agent_tool",
    model="gemini-2.5-flash-lite",
    instruction="""
    Use your tool to get ESG internal information.
    Extract as many as you can.
    """,
    tools=[rag_tool]
)

internet_search_agent_tool = Agent(
    name="internet_search_agent_tool",
    model="gemini-2.5-flash-lite",
    instruction="""
    Use your tool to get public information.
    Extract as many as you can.
    """,
    tools=[google_search]
)

bigquery_agent_tool = Agent(
    name="bigquery_agent_tool",
    model="gemini-2.5-flash",
    description="Agent that answers questions about BigQuery data by executing SQL",
    instruction="""
    You are a data analysis agent with access to several BigQuery tools. Make use of those
    tools to answer the user's question.
    
    Always use (do not ask for project, dataset or table id):
    - project_id: vtxdemos 
    - dataset_id: esg_demo_data
    - table_id: esg_procurement_master,
    - schema: Transaction_ID, Supplier_Name, Product_Name, Total_Cost_USD, Purchase_Date, S_Labor_Compliance, E_Carbon_Scope3, G_Board_Diversity
    
    """,
    tools=[bigquery_toolset]
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are an ESG Advisory Agent",
    instruction="""
    Your tool 'rag_agent_tool', has access to 3 documents:
    
    -Doc1: Sustainable Procurement Policy (DSPP-v2.1) to detect ESG Policies like Governance
    and minimum ESG compliance thresholds.
    -Doc2: Risk Assessment: Which creates a plausible, specific red flag for a product category and ties it to 
    real-world geography.
    -Doc3: Environmental Benchmark: Which Sets clear, measurable procurement rules based on ESG scores.
    
    Your tool 'internet_search_agent_tool' is used to validate and contextualize internal ESG scores (risk calibration).
    - Public independent rating (e.g. SP Global score of 46).
    - Public Labor_Audit_Compliance_rate (public data).
    - Provide environmental benchmarking for a solution. Public information about carbon footprint.
    
    Your tool 'bigquery_agent_tool' is for any question related to bigquery datasets / ESG purchases...
    
    Answer any question based on that.
    """,
    tools=[agent_tool.AgentTool(rag_agent_tool), agent_tool.AgentTool(internet_search_agent_tool), agent_tool.AgentTool(bigquery_agent_tool)]
)
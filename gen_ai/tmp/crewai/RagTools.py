
import asyncio
from utils.k import *
from langchain.tools import tool
from utils import vector_database
from vertexai.language_models import TextEmbeddingModel
from utils.video.credentials import *

from langchain.tools import tool

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_tax_lang",
    "database_password": DATABASE_PASSWORD, #utils.video.credentials
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
vector_database_client = vector_database.Client(variables)

@tool("tax_search_tool")
def rag_tool(action_input: str) -> str:
    """
    A tool to gather tax information from internal documents (retrieval agumented generation: rag).
    The format/schema of your rag output should be field_in /s(space) section /n(breakline) amount, for example:
    Gross receipts or sales 1a
    14,000.
    
    Parameters:
    - query: the query used to search through the rag internal documents system.
    - rag_schema: the schema required by the rag internal system.
    
    Returns:
    - result: a string with all the text related with the query.
    
    """
    print("""\n\nValidating Information with the following input...\n\n""" + action_input)
    
    print(action_input)
    query, rag_schema_1, rag_schema_2 = action_input.split(",")
    rag_schema = rag_schema_1 + "," + rag_schema_2
    
    result = None
    try:
        query = model_emb.get_embeddings([query])[0].values
        result = asyncio.run(vector_database_client.query(query, rag_schema))
    except:
        return "There is no information in the internal system related to your query."
        
    return result
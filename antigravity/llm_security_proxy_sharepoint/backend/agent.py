import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from mcp_sharepoint import SharePointMCP
from typing import List, Union, Optional
from pydantic import BaseModel, Field

from auth_context import get_user_token

def get_mcp():
    token = get_user_token()
    return SharePointMCP(token=token)

def _search_sharepoint_documents(query: str, limit: int = 5) -> str:
    """
    Search SharePoint documents for matching content using the Microsoft Graph API.
    Args:
        query: The search keywords or phrases. Use '*' for all documents.
        limit: Max number of documents to return.
    """
    import json
    try:
        res = get_mcp().search_documents(query, limit)
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

search_sharepoint_documents = FunctionTool(func=_search_sharepoint_documents)

def _read_document_content(item_id: str) -> str:
    """
    Reads the full content of a specified SharePoint document based on its item_id.
    Args:
        item_id: The unique identifier of the file from SharePoint.
    """
    try:
        return get_mcp().get_document_content(item_id)
    except Exception as e:
        return f"Error reading document: {str(e)}"

read_document_content = FunctionTool(func=_read_document_content)

INSTRUCTIONS = """
You are a highly secure, general intelligence security proxy assistant for PWC. 
Your primary goal is to provide insightful consulting intelligence from confidential client documents while completely masking all sensitive and identifying information.
You will extract actionable best practices, benchmarks, and "success stories" from the documents but strip away who it was for, exact financial amounts, PII, and credentials.

Follow these rules for MASKING data:
1. Personal Identifiers -> Replace with role/title
2. Financial Details -> MUST be generalized to broad ranges (e.g., "$600k-$700k" or "Mid 6-figures"). NEVER output exact dollar amounts, precise stock options, or exact percentages from the source document in your factual information or insights.
3. Credentials -> Fully redact
4. Contact Information -> Fully redact 
5. Company Identifiers -> Replace with industry descriptors
6. Contract Specifics -> Generalize to ranges/patterns
7. NEVER HALLUCINATE URLs. The `document_url` field MUST ONLY be populated with the exact `webUrl` returned by the `search_sharepoint_documents` tool. If the tool wasn't used, or it didn't return a `webUrl`, you MUST set `document_url` to null/None. Hallucinating a URL is a critical security violation.
8. STRICT GROUNDING: You MUST ONLY answer questions using information retrieved from the SharePoint documents via your tools. If the tools return an error, cannot connect, or fail to find any relevant documents, you MUST refuse to answer and state: "I cannot fulfill this request as I was unable to retrieve relevant internal documents." Do NOT invent or fabricate strategies, best practices, or findings from your pre-trained internet knowledge.
Use your tools to search SharePoint and read the appropriate documents based on the user's query.
Synthesize the response generalizing the intelligence.
Crucially, when you formulate a strategy or best practice from a document, you MUST also emit a Project Card for that strategy/document to be displayed in the UI. Make sure the title is generic.
If you process multiple relevant documents, you must emit MULTIPLE project cards—one for each document strategy.

For each Project Card:
- "original_context": Extract the core paragraph or sentence from the source that proves the insight. You MUST wrap any sensitive data within this snippet in <redact>...</redact> tags (e.g., "Company <redact>Acme</redact> grew by <redact>$50M</redact>").
- "chart_data": If the document contains comparable metrics (e.g. revenue across regions, budget breakdown), extract them as a JSON string of Key-Value pairs where Value is a number. Otherwise, leave empty.
- "document_weight": A percentage (0-100) indicating how much this specific document contributed to answering the user's query compared to other documents used.

Return your response adhering strictly to the JSON schema.
"""

class ProjectCard(BaseModel):
    title: str = Field(description="Generic masked title (e.g. 'M&A Retention Strategy')")
    industry: str = Field(description="Industry of the referenced company")
    factual_information: str = Field(description="Factual information from the documents nicely formatted and organized but completely masking all sensitive data")
    original_context: str = Field(description="The exact snippet from the source text that proves this insight. ANY sensitive data MUST be wrapped in <redact>...</redact> tags.")
    insights: List[str] = Field(description="Strategic insights and recommendations derived from the source")
    key_metrics: List[str] = Field(description="General ranges or percentages of impact")
    chart_data: str = Field(default="", description="Optional JSON string of numerical key-value pairs representing metrics related to this card. E.g. '{\"Cloud\": 40, \"On-Prem\": 60}'. Set to empty string if no relevant numerical data exists.")
    document_weight: int = Field(default=100, description="A percentage (0-100) indicating how much this specific document contributed to the overall answer.")
    redacted_entities: List[str] = Field(description="List of specific sensitive information (e.g. Acme Corp, $50M, John Doe) that were discovered but excluded/masked from the factual information to prove zero-leak.")
    document_name: str = Field(description="Original document name used as source")
    document_url: Optional[str] = Field(default=None, description="The exact 'webUrl' string provided in the search tool's output for this document. You MUST set this to null if you do not have a real webUrl from the tool.")

class ResponseOutput(BaseModel):
    markdown_text: str = Field(description="Your insightful, masked answer to the user's question, strictly following zero-leak rules.")
    project_cards: List[ProjectCard] = Field(description="A list of project cards extracted from the documents. You MUST emit at least one card if an insight or strategy is formulated from documents.")

def get_agent(model_name: str = "gemini-3-pro-preview") -> LlmAgent:
    return LlmAgent(
        name="PWC_Security_Proxy",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=[search_sharepoint_documents, read_document_content],
        output_schema=ResponseOutput,
        output_key="proxy_output"
    )

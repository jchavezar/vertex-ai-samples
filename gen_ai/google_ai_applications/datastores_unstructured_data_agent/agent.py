import json
import vertexai
from google.genai import types
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.protobuf.json_format import MessageToDict
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from datastores_unstructured_data.prompts import system_instruction
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project = "jesusarguelles-sandbox"
location = "global"
vertexai_search_engine_name = "deloitte_metadata"
vertexai.init(project=project)

client_options = ClientOptions(
    api_endpoint=f"{location}-discoveryengine.googleapis.com"
)
client = discoveryengine.SearchServiceClient(client_options=client_options)
serving_config = f"projects/{project}/locations/{location}/collections/default_collection/engines/{vertexai_search_engine_name}/servingConfigs/default_config"

def retrieval(prompt: str, category: str):
    """
    This function calls discovery engine as rag for local files grounding.
    :param prompt: the query.
    :param category: category to filter.
    :return: str
    """
    logger.info("[Retrieval] Starting")
    logger.info("-"*80)
    logger.info(f"Category:\n {category}")
    logger.info(f"Prompt:\n {prompt}")
    logger.info("-"*80)
    request = discoveryengine.SearchRequest(
        query=prompt,
        filter=f"category: ANY(\"{category}\")",
        serving_config=serving_config,
        query_expansion_spec={
            "condition": discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        },
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_segment_count=5,
                return_extractive_segment_score=True,
                num_previous_segments=2,
                num_next_segments=2
            ),
        )
    )

    page_result = client.search(request)

    markdown_output = []

    documents = [MessageToDict(i.document._pb) for i in page_result]

    parsed_doc = []

    for content in documents:
        content_list = []
        annotations_list = []
        if "extractive_segments" in content["derivedStructData"]:
            for segment in content["derivedStructData"]["extractive_segments"]:
                if "content" in segment:
                    content_list.append(segment["content"])
                if "annotationContent" in segment:
                    annotations_list.append(segment["annotationContent"])
        parsed_doc.append(
            {"doc_id": content["name"], "content": content_list, "annotations": annotations_list}
        )
    re = json.dumps(parsed_doc)
    logger.info(f"category:\n {category}")
    logger.info(f"Retrieval Chunks:\n {re}")
    logger.info("-"*80)

    return re

my_planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

root_agent = Agent(
    name="expert_agent",
    model="gemini-2.0-flash-001",
    description="You are an Agent with local grounding ready to answer any question.",
    global_instruction=system_instruction,
    instruction="""
    Use your tool to extract any relevant information to answer your question:
    Instructions:
    Your tools needs a prompt/query to extract the information and category (network, management, marketing, code) pick
    one based on the intent.
    Give me the details of your grounding in the response. And a brief Explanation of your conclusions
    """,
    tools=[retrieval],
)
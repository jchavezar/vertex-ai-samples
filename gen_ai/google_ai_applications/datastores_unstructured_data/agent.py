import json

import vertexai
from google.adk.agents import Agent
from google.protobuf.json_format import MessageToDict
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
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
    print(prompt)
    print(category)
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

    # for response in page_result:
    #     document = response.document
    #
    #     markdown_output.append(f"## Document ID: {document.id}")
    #     markdown_output.append(f"**Title:** {document.struct_data['title']}")
    #     markdown_output.append(f"**Link:** {document.derived_struct_data['link']}")
    #
    #     if document.derived_struct_data and 'extractive_segments' in document.derived_struct_data:
    #         extractive_segments_list = document.derived_struct_data['extractive_segments']
    #         markdown_output.append("\n### Extracted Segments:")
    #         for i, segment in enumerate(extractive_segments_list):
    #             markdown_output.append(f"#### Segment {i+1}:")
    #
    #             if "content" in segment:
    #                 markdown_output.append(f"**Content:**\n```text\n{segment['content']}\n```")
    #             else:
    #                 markdown_output.append("**Content:** Not available")
    #
    #             if "relevanceScore" in segment:
    #                 markdown_output.append(f"**Relevance Score:** {segment['relevanceScore']}")
    #             else:
    #                 markdown_output.append("**Relevance Score:** Not available")
    #
    #             if "page_span" in segment and segment["page_span"]:
    #                 page_start = segment["page_span"].get("page_start", 0)
    #                 page_end = segment["page_span"].get("page_end", 0)
    #                 markdown_output.append(f"**Page Span:** {int(page_start)} - {int(page_end)}")
    #             else:
    #                 markdown_output.append("**Page Span:** Not available")
    #
    #             if "id" in segment:
    #                 markdown_output.append(f"**Segment ID:** {segment['id']}")
    #             else:
    #                 markdown_output.append("**Segment ID:** Not available")
    #
    #             # Accessing previous and next segments
    #             if "previous_segments" in segment and segment["previous_segments"]:
    #                 markdown_output.append("**Previous Segments:**")
    #                 for j, ps in enumerate(segment["previous_segments"]):
    #                     if "content" in ps:
    #                         markdown_output.append(f"  - **Prev Segment {j+1} Content:**\n```text\n{ps['content']}\n```")
    #                     else:
    #                         markdown_output.append(f"  - **Prev Segment {j+1} Content:** Not available")
    #
    #             if "next_segments" in segment and segment["next_segments"]:
    #                 markdown_output.append("**Next Segments:**")
    #                 for j, ns in enumerate(segment["next_segments"]):
    #                     if "content" in ns:
    #                         markdown_output.append(f"  - **Next Segment {j+1} Content:**\n```text\n{ns['content']}\n```")
    #                     else:
    #                         markdown_output.append(f"  - **Next Segment {j+1} Content:** Not available")
    #
    #             markdown_output.append("---")
    #
    #     if response.model_scores and 'relevance_score' in response.model_scores:
    #         markdown_output.append(f"**Document Relevance Score:** {response.model_scores['relevance_score'].values[0]}")
    #
    #     markdown_output.append("=" * 50)

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
    print(parsed_doc)
    for i in parsed_doc:
        print(i["doc_id"])
        print("-"*80)
        print("annotations")
        print(i["annotations"])
    re = json.dumps(parsed_doc)
    logger.info(f"category:\n {category}")
    logger.info(f"Markdown:\n {re}")

    return re

root_agent = Agent(
    name="expert_agent",
    model="gemini-2.0-flash-001",
    description="You are an Agent with local grounding ready to answer any question.",
    instruction="""
    Use your tool to extract any relevant information to answer your question:
    Instructions:
    Your tools needs a prompt/query to extract the information and category (network, management, marketing, code) pick
    one based on the intent.
    Give me the details of your grounding in the response.
    """,
    tools=[retrieval]
)
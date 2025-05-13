#%%
import vertexai
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

project = "jesusarguelles-sandbox"
location = "global"
vertexai_search_engine_name = "deloitte_metadata"
vertexai.init(project=project)

client_options = ClientOptions(
    api_endpoint=f"{location}-discoveryengine.googleapis.com"
)
client = discoveryengine.SearchServiceClient(client_options=client_options)
serving_config = f"projects/{project}/locations/{location}/collections/default_collection/engines/{vertexai_search_engine_name}/servingConfigs/default_config"

request = discoveryengine.SearchRequest(
    query="Vodafone top markers",
    filter="category: ANY(\"network\")",
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

# Markdown from Output
#%%

for response in page_result:
    document = response.document
    print(f"--- Document ID: {document.id} ---")
    print(f"Title: {document.struct_data['title']}")
    print(f"Link: {document.derived_struct_data['link']}")

    if document.derived_struct_data and 'extractive_segments' in document.derived_struct_data:
        extractive_segments_list = document.derived_struct_data['extractive_segments']
        print("\nExtractive Segments:")
        for segment in extractive_segments_list: # Iterate directly over RepeatedComposite
            print(f"  Content:\n{segment["content"]}\n")
            print(f"  Relevance Score: {segment["relevanceScore"]}")
            page_start = segment["page_span"]["page_start"] if segment["page_span"] else 0
            page_end = segment["page_span"]["page_end"] if segment["page_span"] else 0
            print(f"  Page Span: {int(page_start)} - {int(page_end)}")
            print(f"  Segment ID: {segment["id"]}")

            for ps in segment["previous_segments"]:
                print(f"  Previous Segment Content:\n{ps["content"]}\n")
            for ns in segment["next_segments"]:
                print(f"  Next Segment Content:\n{ns["content"]}\n")
            print("-" * 20)

    if response.model_scores and 'relevance_score' in response.model_scores:
        # Accessing directly as a float
        print(f"Document Relevance Score: {response.model_scores['relevance_score'].values[0]}")

    print("=" * 50)



## MarkDown Testing
#%%

markdown_output = []

for response in page_result:
    document = response.document

    markdown_output.append(f"## Document ID: {document.id}")
    markdown_output.append(f"**Title:** {document.struct_data['title']}")
    markdown_output.append(f"**Link:** {document.derived_struct_data['link']}")

    if document.derived_struct_data and 'extractive_segments' in document.derived_struct_data:
        extractive_segments_list = document.derived_struct_data['extractive_segments']
        markdown_output.append("\n### Extracted Segments:")
        for i, segment in enumerate(extractive_segments_list):
            markdown_output.append(f"#### Segment {i+1}:")

            if "content" in segment:
                markdown_output.append(f"**Content:**\n```text\n{segment['content']}\n```")
            else:
                markdown_output.append("**Content:** Not available")

            if "relevanceScore" in segment:
                markdown_output.append(f"**Relevance Score:** {segment['relevanceScore']}")
            else:
                markdown_output.append("**Relevance Score:** Not available")

            if "page_span" in segment and segment["page_span"]:
                page_start = segment["page_span"].get("page_start", 0)
                page_end = segment["page_span"].get("page_end", 0)
                markdown_output.append(f"**Page Span:** {int(page_start)} - {int(page_end)}")
            else:
                markdown_output.append("**Page Span:** Not available")

            if "id" in segment:
                markdown_output.append(f"**Segment ID:** {segment['id']}")
            else:
                markdown_output.append("**Segment ID:** Not available")

            # Accessing previous and next segments
            if "previous_segments" in segment and segment["previous_segments"]:
                markdown_output.append("**Previous Segments:**")
                for j, ps in enumerate(segment["previous_segments"]):
                    if "content" in ps:
                        markdown_output.append(f"  - **Prev Segment {j+1} Content:**\n```text\n{ps['content']}\n```")
                    else:
                        markdown_output.append(f"  - **Prev Segment {j+1} Content:** Not available")

            if "next_segments" in segment and segment["next_segments"]:
                markdown_output.append("**Next Segments:**")
                for j, ns in enumerate(segment["next_segments"]):
                    if "content" in ns:
                        markdown_output.append(f"  - **Next Segment {j+1} Content:**\n```text\n{ns['content']}\n```")
                    else:
                        markdown_output.append(f"  - **Next Segment {j+1} Content:** Not available")

            markdown_output.append("---")

    if response.model_scores and 'relevance_score' in response.model_scores:
        markdown_output.append(f"**Document Relevance Score:** {response.model_scores['relevance_score'].values[0]}")

    markdown_output.append("=" * 50)
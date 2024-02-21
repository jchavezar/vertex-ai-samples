#%%
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "financial-internal-docs_1706730313453"
}

client = discoveryengine.SearchServiceClient()
serving_config = client.serving_config_path(
    project=variables["project"],
    location=variables["location"],
    data_store=variables["datastore"],
    serving_config="default_config",
    )

#request = discoveryengine.SearchRequest(
#    serving_config=serving_config, query=prompt, page_size=100)

content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True),
summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=5, include_citations=True),
extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
        max_extractive_answer_count=5,
        max_extractive_segment_count=5))

request = discoveryengine.SearchRequest(
    serving_config=serving_config, query="how much money did Amazon made during 2022?", page_size=2, content_search_spec=content_search_spec)  
# %%
response = client.search(request)
# %%
context = []
documents = [MessageToDict(i.document._pb) for i in response.results]
for i in documents:
    for ans in i["derivedStructData"]["extractive_answers"]:
        context.append(ans["content"])
res = ''.join(context)
# %%

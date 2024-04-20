#%%
from typing import List
from langchain.tools import tool
from google.protobuf.json_format import MessageToDict
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

project_id = "254356041555"
location = "global"
engine_id = "countries-and-their-cultur_1706277976842"

api_endpoint=f"{location}-discoveryengine.googleapis.com"
client = discoveryengine.SearchServiceClient()
serving_config = f"projects/{project_id}/locations/{location}/dataStores/{engine_id}/servingConfigs/default_config"

content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True),
    extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
        max_extractive_answer_count=2,
        max_extractive_segment_count=2))


class InternalSearchTools:
    @tool("Search Internal")
    def search_internal(query):
        """Useful to search internal documents about a given topic and return relevant results"""
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=10,
            content_search_spec=content_search_spec,
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
        )

        response = client.search(request)
        documents = [MessageToDict(i.document._pb) for i in response.results]

        context = []
        for i in documents:
            for ans in i["derivedStructData"]["extractive_segments"]:
                context.append(ans["content"])

        return ''.join(context)

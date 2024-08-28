import flet as ft
from typing import Dict
from google.cloud import aiplatform
from google.protobuf.json_format import MessageToDict
from vertexai.generative_models import GenerativeModel
from google.cloud import discoveryengine_v1 as discoveryengine

project_id = "vtxdemos"
vais_location = "global"
engine_id = "verano_1724170347575"

client = discoveryengine.SearchServiceClient(client_options=None)
serving_config = f"projects/{project_id}/locations/{vais_location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"
serving_config = f"projects/390227712642/locations/global/collections/default_collection/engines/verano_1724170347575/servingConfigs/default_search"

content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True
    ),
    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=5,
        include_citations=True,
        ignore_adversarial_query=True,
        ignore_non_summary_seeking_query=True,
        model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
            version="stable",
        ),
    ),
)

request = discoveryengine.SearchRequest(
    serving_config=serving_config,
    query="what are the most affordable edibles?",
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



results = []
for result in response.results:
  results.append(MessageToDict(result.document._pb))

# for i in results:
#   print("metatags:\n")
#   print(i['derivedStructData']['pagemap']['metatags'][0]['og:description'])
#   print("snippets:\n")
#   print("#"*80)
#   print(i['derivedStructData']['snippets'])
#   print("+"*80)
#   print(i['derivedStructData']['snippets'][0]['snippet'])
#   print("-"*80)


metadata = {}

for i in response._response.results:
    met_list = []
    for k, v in i.document.derived_struct_data.get("pagemap").get("metatags")[0].items():
        met_list.append({k:v})
    metadata[i.id] = met_list

print(metadata)

metadata_2 = []
for i in results:
    metadata_2.append({
        "title": i['derivedStructData']['pagemap']['metatags'][0]['twitter:title'],
        "description": i['derivedStructData']['pagemap']['metatags'][0]['og:description'],
        "url": i['derivedStructData']['pagemap']['metatags'][0]['og:url'],
        "image": i['derivedStructData']['pagemap']['metatags'][0]['og:image'],
        "reviews": i['derivedStructData']['pagemap']['metatags'][0]['twitter:description'],
     })

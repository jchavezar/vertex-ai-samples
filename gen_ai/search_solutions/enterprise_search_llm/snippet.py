#%%
import json
from typing import Any, Mapping, List, Dict, Optional, Tuple, Sequence, Union
from google.cloud import discoveryengine_v1beta
from google.protobuf.json_format import MessageToDict

search_client = discoveryengine_v1beta.SearchServiceClient()
serving_config_id='default_config'
serving_config: str = search_client.serving_config_path(
        project="vtxdemos",
        location="global",
        data_store="news_1687453492092",
        serving_config=serving_config_id,
        )

def _search(query:str):
    """Helper function to run a search"""
    request = discoveryengine_v1beta.SearchRequest(serving_config=serving_config, query=query)
    return search_client.search(request)

def get_relevant_snippets(query: str) -> List[str]:
    """Retrieve snippets from a search query"""
    res = _search(query)
    snippets = []
    for result in res.results:
        data = MessageToDict(result.document._pb)
        if data.get('derivedStructData', {}) == {}:
            snippets.append(json.dumps(data.get('structData', {})))
        else:
            snippets.extend([d.get('snippet') for d in data.get('derivedStructData', {}).get('snippets', []) if d.get('snippet') is not None])
        with open("snippets_out.txt", "w") as f:
            for i in snippets:
                f.write(i+"\n")
    return snippets

get_relevant_snippets("News about Harrison Ford")
# %%


_res=discoveryengine_v1beta.SearchServiceClient().search(discoveryengine_v1beta.SearchRequest(serving_config=serving_config, query="News about Harrison Ford"))
# %%
for i in _res.results:
    data = MessageToDict(i.document._pb)
    print([d.get('snippet') for d in data.get('derivedStructData', {}).get('snippets', []) if d.get('snippet') is not None])
    print(data.get('derivedStructData', {}).get('link'))
# %%

for i in _res.results:
    print(i.document._pb)
    break
# %%

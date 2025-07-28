#%%
from google import genai
from google.genai import types
from google.cloud import discoveryengine_v1 as discoveryengine

project_id="vtxdemos"
location="global"
engine_id="ap_news"
model_id="gemini-2.5-flash"

serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

csearch_client = discoveryengine.SearchServiceClient()
chat_client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location
)

# noinspection PyTypeChecker
content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True
    ),
)

titles = []
snippets = []
thumbnails = []
images = []

def custom_search(prompt: str):
    # noinspection PyTypeChecker
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=prompt,
        page_size=50,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    import time
    start_time = time.time()
    page_result = csearch_client.search(request)
    print(time.time()-start_time)

    start_time = time.time()
    results_count = 0
    for response in page_result:
        if results_count >= 20:
            break
        for key,value in response.document.derived_struct_data.items():
            if key == "title":
                titles.append(value)
            if key == "snippets":
                snippets.append(value[0]["snippet"])
            if key == "pagemap":
                thumbnails.append(value["cse_thumbnail"][0]["src"])
                images.append(value["cse_image"][0]["src"])
        results_count += 1

    response_json = {
        "titles": titles,
        "snippets": snippets,
        "thumbnails": thumbnails,
        "images": images
    }
    print(time.time()-start_time)
    return  response_json

def send_message(prompt: str):
    try:
        response = chat_client.models.generate_content(
            model=model_id,
            contents=[prompt],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0
                )
            )
        )
        print(response.text)
        return response.text
    except Exception as e:
        print(e)
        return f"Error: {e}"

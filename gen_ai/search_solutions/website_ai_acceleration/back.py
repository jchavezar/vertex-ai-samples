
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
    titles.clear()
    snippets.clear()
    thumbnails.clear()
    images.clear()

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
            elif key == "snippets":
                snippets.append(value[0]["snippet"])
            elif key == "pagemap":
                # Safely get thumbnail and image, providing empty string if not found
                thumbnails.append(value.get("cse_thumbnail", [{}])[0].get("src", ""))
                images.append(value.get("cse_image", [{}])[0].get("src", ""))
        results_count += 1

    response_json = {
        "titles": titles,
        "snippets": snippets,
        "thumbnails": thumbnails,
        "images": images
    }
    print(time.time()-start_time)
    return  response_json

def send_message(prompt: str, grounding: False):
    try:
        response = chat_client.models.generate_content(
            model=model_id,
            contents=[prompt],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0
                ),
                tools=[types.Tool(google_search=types.GoogleSearch())] if grounding else []
            ),
        )
        print(response.text)
        return response.text
    except Exception as e:
        print(e)
        return f"Error: {e}"

def classify_and_summarize_news():
    # In a real application, you would fetch news from an API or database
    # For this example, we'll use the data from the last search
    if not titles:
        custom_search("latest news") # or some default query

    news_items = []
    for i in range(len(titles)):
        news_items.append(f"Title: {titles[i]}\nSnippet: {snippets[i]}")

    news_text = "\n\n".join(news_items)

    prompt = f'''Please analyze the following list of news articles. Your task is to:
1.  Group the articles into 3-5 distinct categories based on their content.
2.  For each category, provide a short, descriptive name.
3.  Write a concise, one-paragraph summary of all the news presented.

Here are the articles:
{news_text}

Please format your response as a JSON object with two keys:
-   `summary`: A string containing the overall summary.
-   `categories`: A dictionary where each key is a category name and the value is a list of articles belonging to that category. Each article in the list should be an object with `title` and `snippet` keys.'''

    response_text = send_message(prompt, grounding=True)

    try:
        import json
        # Handle markdown code block
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
             response_text = response_text.split("```")[1].split("```")[0]
        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError):
        # Handle cases where the response is not valid JSON
        return {
            "summary": "Failed to parse the AI response.",
            "categories": {}
        }

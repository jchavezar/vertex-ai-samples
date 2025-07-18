
import base64
import pickle
import numpy as np
import vertexai
from google import genai
from google.genai import types
from google.cloud import storage
from vertexai.vision_models import MultiModalEmbeddingModel
from google.cloud import discoveryengine_v1 as discoveryengine
import concurrent.futures

project_id = "vtxdemos"
region_for_gemini = "global"
region_for_embeddings = "us-central1"
model_emb = "multimodalembedding@001"
pickle_file_name = "video_gen_dataset.pkl"
engine_id = "time_mag_1"
serving_config = f"projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

vertexai.init(project=project_id, location=region_for_embeddings)

gem_client = genai.Client(vertexai=True, project=project_id, location=region_for_gemini)
storage_client = storage.Client(project_id)
vais_client = discoveryengine.SearchServiceClient()
# bucket = storage_client.bucket(bucket_name)
emb_model = MultiModalEmbeddingModel.from_pretrained(model_emb)


with open(pickle_file_name, 'rb') as pf:
    all_videos_data = pickle.load(pf)

def _perform_vertex_search(prompt: str):
    """Performs a search using Vertex AI Search."""
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=prompt,
        page_size=20,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = vais_client.search(request)
    page = next(response.pages)
    vertex_search_results = []
    for result in page.results:
        if "image" in result.document.derived_struct_data and "thumbnail" in result.document.derived_struct_data.get("image", {}):
            _, encoded_data = result.document.derived_struct_data["image"]["thumbnail"].split(",", 1)
            decoded_data = base64.b64decode(encoded_data)
            vertex_search_results.append({
                "title": result.document.derived_struct_data.get("title"),
                "link": result.document.derived_struct_data.get("link", "").replace("gs://", "https://storage.googleapis.com/"),
                "decoded_data": decoded_data
            })
    return vertex_search_results

def _perform_multimodal_retrieval(prompt: str, top_n: int = 5):
    """Performs multimodal video retrieval."""
    prompt_result = emb_model.get_embeddings(contextual_text=prompt)
    prompt_embedding = np.array(prompt_result.text_embedding).reshape(1, -1)

    all_segments_with_title = []
    for video_data in all_videos_data:
        video_title = video_data.get('video_title', 'Unknown Title')
        for segment in video_data['segmented_data']:
            segment_copy = segment.copy()
            segment_copy['video_title'] = video_title
            all_segments_with_title.append(segment_copy)

    existing_embeddings = np.array([emb["embedding"] for emb in all_segments_with_title if emb.get("embedding") is not None])
    valid_segments = [seg for seg in all_segments_with_title if seg.get("embedding") is not None]

    dot_products = np.dot(prompt_embedding, existing_embeddings.T)
    norm_prompt = np.linalg.norm(prompt_embedding)
    norm_segments = np.linalg.norm(existing_embeddings, axis=1)

    denominators = norm_prompt * norm_segments
    sim_scores = np.zeros_like(denominators, dtype=float)
    non_zero_mask = denominators != 0
    sim_scores[non_zero_mask] = dot_products[0, non_zero_mask] / denominators[non_zero_mask]

    top_indices = np.argsort(sim_scores)[::-1]

    multimodal_results = []
    for i in range(min(top_n, len(top_indices))):
        idx = top_indices[i]
        segment = valid_segments[idx].copy()
        if 'embedding' in segment:
            del segment['embedding']
        multimodal_results.append(segment)
    return multimodal_results


def find_most_similar(prompt: str, top_n: int = 5):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit both tasks to the executor
        vertex_search_future = executor.submit(_perform_vertex_search, prompt)
        multimodal_retrieval_future = executor.submit(_perform_multimodal_retrieval, prompt, top_n)

        # Get the results
        vertex_search_results = vertex_search_future.result()
        multimodal_results = multimodal_retrieval_future.result()

    return vertex_search_results, multimodal_results


def generate_chat_response(video_uri, question, chat_history_view, page):
    gs_uri = video_uri.replace("https://storage.googleapis.com/", "gs://")

    video_part = types.Part.from_uri(
        file_uri=gs_uri,
        mime_type="video/mp4",
    )

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        )
    )

    model = "gemini-2.5-flash-lite-preview-06-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Question: {question}\n\nAnswer:"),
                video_part,
            ]
        )
    ]

    try:
        response = gem_client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
        print("#"*80)
        print(gs_uri)
        print(response)
        return response.text

    except Exception as e:
        return f"Error: {e}"

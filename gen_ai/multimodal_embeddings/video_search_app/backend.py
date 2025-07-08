import pickle
import numpy as np
import vertexai
from google import genai
from google.genai import types
from google.cloud import storage
from vertexai.vision_models import MultiModalEmbeddingModel

project_id = "vtxdemos"
region = "us-central1"
model_emb = "multimodalembedding@001"
pickle_file_name = "video_gen_dataset.pkl"

vertexai.init(project=project_id, location=region)

gem_client = genai.Client(vertexai=True, project=project_id, location=region)
storage_client = storage.Client(project_id)
# bucket = storage_client.bucket(bucket_name)
emb_model = MultiModalEmbeddingModel.from_pretrained(model_emb)


with open(pickle_file_name, 'rb') as pf:
    all_videos_data = pickle.load(pf)

def find_most_similar(prompt: str, top_n: int = 5):
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

    results = []
    for i in range(min(top_n, len(top_indices))):
        idx = top_indices[i]
        segment = valid_segments[idx].copy()
        if 'embedding' in segment:
            del segment['embedding']
        results.append(segment)
    print(results)
    return results

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

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Question: {question}\n\nAnswer:"),
                video_part,
                config
            ]
        )
    ]

    try:
        response = gem_client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
        return response.text

    except Exception as e:
        return f"Error: {e}"

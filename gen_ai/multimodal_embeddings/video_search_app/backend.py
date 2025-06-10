import pickle
import numpy as np
import vertexai

from google.cloud import storage
from vertexai.vision_models import MultiModalEmbeddingModel

project_id = "vtxdemos"
region = "us-central1"
model_emb = "multimodalembedding@001"
# bucket_name = "vtxdemos-datasets-public"
pickle_file_name = "video_gen_dataset.pkl"

vertexai.init(project=project_id, location=region)

storage_client = storage.Client(project_id)
# bucket = storage_client.bucket(bucket_name)
emb_model = MultiModalEmbeddingModel.from_pretrained(model_emb)


with open(pickle_file_name, 'rb') as pf:
    all_videos_data = pickle.load(pf)

def find_most_similar(prompt: str, top_n: int = 5):
    prompt_result = emb_model.get_embeddings(contextual_text=prompt)
    prompt_embedding = np.array(prompt_result.text_embedding).reshape(1, -1)

    all_segments = []
    for video_data in all_videos_data:
        all_segments.extend(video_data['segmented_data'])

    existing_embeddings = np.array([emb["embedding"] for emb in all_segments if emb.get("embedding") is not None])

    # Filter segments to match the embeddings that were actually used
    valid_segments = [seg for seg in all_segments if seg.get("embedding") is not None]

    dot_products = np.dot(prompt_embedding, existing_embeddings.T)
    norm_prompt = np.linalg.norm(prompt_embedding)
    norm_segments = np.linalg.norm(existing_embeddings, axis=1)

    denominators = norm_prompt * norm_segments
    sim_scores = np.zeros_like(denominators, dtype=float)
    non_zero_mask = denominators != 0
    sim_scores[non_zero_mask] = dot_products[0, non_zero_mask] / denominators[non_zero_mask]

    # Sort indices by similarity score in descending order
    top_indices = np.argsort(sim_scores)[::-1]

    results = []
    # Ensure we don't go out of bounds
    for i in range(min(top_n, len(top_indices))):
        idx = top_indices[i]
        # Use the list of valid segments that corresponds to existing_embeddings
        segment = valid_segments[idx].copy()
        if 'embedding' in segment:
            del segment['embedding']
        results.append(segment)

    return results

# find_most_similar(prompt)

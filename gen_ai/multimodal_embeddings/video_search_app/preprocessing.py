#%%
import json
import pickle
import time
from typing import List
import numpy as np
import vertexai
from google import genai
from google.genai import types
from google.cloud import storage
from vertexai.vision_models import VideoSegmentConfig
from thumbnails import generate_specific_gcs_thumbnail
from vertexai.vision_models import MultiModalEmbeddingModel, Video

project_id = "vtxdemos"
region = "us-central1"
bucket_name = "vtxdemos-datasets-public"
prefix_bucket_videos = "video_search_app/videos"
prefix_bucket_thumbnails = "video_search_app/thumbnails"
model_emb = "multimodalembedding@001"
model_gem = "gemini-2.5-flash-preview-05-20"

vertexai.init(project=project_id, location=region)

storage_client = storage.Client(project_id)
bucket = storage_client.bucket(bucket_name)
emb_model = MultiModalEmbeddingModel.from_pretrained(model_emb)
gem_model = genai.Client(
    vertexai=True,
    project=project_id,
    location=region,
)


def generate_content(
        segment_definitions_list: List,
        video_uri: str,
        number_of_segments_to_generate: int,
):
    config = types.GenerateContentConfig(
        system_instruction="""
        You will be provided with a video file and a list of specific segment definitions. Each definition will include a `start_offset_sec` and an `end_offset_sec` that define a single segment within that video. These definitions (e.g., {"start_offset_sec": 0.0, "end_offset_sec": 12.0}) will be passed in the user's part of the prompt.
        
        Your task is to:
        1.  Generate a concise **title** that broadly describes the entire video content.
        2.  For **each** `segment_definition` provided in the user's prompt, generate a corresponding summary. Each summary should be an object containing:
            * The `start_offset_sec` (number) from the input definition.
            * The `end_offset_sec` (number) from the input definition.
            * A `summary_text` (string) capturing the key information or events *specifically within that segment*. Ensure this summary is concise and directly relevant to the events occurring within its defined timestamps.
        
        Respond ONLY with a JSON object.
        Do not try to summarize the entire video outside the combined provided segments. Focus the `summary_text` within each `segments_summary` entry *only* on its respective segment.    
    """,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type = "application/json",
        response_schema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A concise title that broadly describes the entire video content."
                },
                "segments_summary": {
                    "type": "array",
                    "description": "A list of summaries, where each entry corresponds to a specific segment of the video.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start_offset_sec": {
                                "type": "number",
                                "format": "float",
                                "description": "The start offset in seconds for this specific video segment.",
                                "minimum": 0.0
                            },
                            "end_offset_sec": {
                                "type": "number",
                                "format": "float",
                                "description": "The end offset in seconds for this specific video segment.",
                                "minimum": 0.0
                            },
                            "summary_text": {
                                "type": "string",
                                "description": "A concise description of the key information or events occurring specifically within this video segment."
                            }
                        },
                        "required": [
                            "start_offset_sec",
                            "end_offset_sec",
                            "summary_text"
                        ]
                    },
                    # minItems and maxItems are correctly placed here for the array itself
                    "minItems": number_of_segments_to_generate,
                    "maxItems": number_of_segments_to_generate
                }
            },
            "required": [
                "title",
                "segments_summary"
            ],
        }
    )
    text = types.Part.from_text(
        text=f"""
        Please provide an overall title for the video and detailed summaries for the following segments, 
        based on their start and end offsets:\n{json.dumps(segment_definitions_list, indent=2)}
        """
    )
    video = types.Part.from_uri(file_uri=video_uri, mime_type="video/mp4")
    try:
        re = gem_model.models.generate_content(
            model=model_gem,
            config=config,
            contents=[
                text,
                video
            ]
        )
        print(segment_definitions_list)
        print(video)
        print(re.text)
        return re.text
    except Exception as e:
        return f"Problems {e}"


#%%

interval_sec = 12
all_videos_data = []
pickle_file_path = "./video_gen_dataset.pkl"

for i in bucket.list_blobs(prefix=prefix_bucket_videos):
    print(i.name)
    if ".mp4" in i.name:
        start_time = time.time()
        print(f"{'gs://'+bucket_name}/{i.name}")
        embeddings = emb_model.get_embeddings(
            video=Video.load_from_file(
                f"{'gs://'+bucket_name}/{i.name}"
            ),
            video_segment_config=VideoSegmentConfig(interval_sec=interval_sec)
        )
        print(f"Time taken for embeddings: {time.time()-start_time}")

        segment_definitions_for_llm = []
        embeddings_map = {}
        for emb in embeddings.video_embeddings:
            segment_definitions_for_llm.append({
                "start_offset_sec": emb.start_offset_sec,
                "end_offset_sec": emb.end_offset_sec
            })
            embeddings_map[(emb.start_offset_sec, emb.end_offset_sec)] = emb.embedding

        start_time_llm = time.time()
        response = generate_content(
            segment_definitions_list=segment_definitions_for_llm,
            number_of_segments_to_generate=len(embeddings.video_embeddings),
            video_uri=f"{'gs://'+bucket_name}/{i.name}"
        )
        response_json_str = json.loads(response)
        print(f"Time taken for LLM: {time.time()-start_time_llm}")

        combined_output = {
            "video_title": response_json_str.get("title", "No Title Provided"),
            "segmented_data": []
        }

        for segment_summary in response_json_str.get("segments_summary", []):
            start_s = segment_summary["start_offset_sec"]
            end_s = segment_summary["end_offset_sec"]
            summary_text = segment_summary["summary_text"]

            embedding_vector = embeddings_map.get((start_s, end_s))
            thumbnail_target_time_sec = (start_s + end_s) / 2.0

            print(f"Generating thumbnail for segment {start_s}-{end_s} at {thumbnail_target_time_sec:.2f}s for {i.name}")
            start_time_thumbnail = time.time()
            thumbnail_gcs_uri = generate_specific_gcs_thumbnail(
                bucket_name=bucket_name,
                video_blob_name=i.name,
                output_thumbnail_blob_name=f"{prefix_bucket_thumbnails}/{i.name.split("/")[-1].split(".")[0]}-thumb_at_{thumbnail_target_time_sec:.2f}s.png",
                target_time_sec=thumbnail_target_time_sec
            )
            print(f"Time taken for thumbnail: {time.time()-start_time_thumbnail:.2f}s. URI: {thumbnail_gcs_uri}")

            if embedding_vector:
                combined_output["segmented_data"].append({
                    "start_offset_sec": start_s,
                    "end_offset_sec": end_s,
                    "summary_text": summary_text,
                    "embedding": embedding_vector,
                    "thumbnail_gcs_uri": thumbnail_gcs_uri,
                    "video_gcs_uri": f"{'https://storage.googleapis.com/'+bucket_name}/{i.name}"
                })
            else:
                print(f"Warning: No embedding found for segment {start_s}-{end_s}")
                combined_output["segmented_data"].append({
                    "start_offset_sec": start_s,
                    "end_offset_sec": end_s,
                    "summary_text": summary_text,
                    "embedding": None,
                    "thumbnail_gcs_uri": thumbnail_gcs_uri,
                    "video_gcs_uri": f"{'https://storage.googleapis.com/'+bucket_name}/{i.name}"
                })
            print(bucket_name)
            print(f"video_gcs_uri: {f'https://storage.googleapis.com/'+bucket_name}/{i.name}")
            print(f"thumbnail_gcs_uri: {thumbnail_gcs_uri}")
            print(f"summary_text: {summary_text}")

        all_videos_data.append(combined_output)
        print(f"Completed processing for {i.name}. Total time: {time.time()-start_time:.2f}s")

with open(pickle_file_path, "wb") as f:
    pickle.dump(all_videos_data, f)

print(f"\nSuccessfully saved data for {len(all_videos_data)} videos to {pickle_file_path}")

#%%
# Testing embeddings

def cosine_similarity(vec1, vec2):
    """Computes the cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0: # Avoid division by zero
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)

def find_most_similar(prompt: str):
    prompt_result = emb_model.get_embeddings(contextual_text=prompt)
    prompt_embedding = np.array(prompt_result.text_embedding).reshape(1, -1)

    existing_embeddings = np.array([emb["embedding"] for emb in combined_output["segmented_data"]])

    dot_products = np.dot(prompt_embedding, existing_embeddings.T)
    norm_prompt = np.linalg.norm(prompt_embedding)
    norm_segments = np.linalg.norm(existing_embeddings, axis=1)

    denominators = norm_prompt * norm_segments

    sim_scores = np.zeros_like(denominators, dtype=float)
    non_zero_mask = denominators != 0
    sim_scores[non_zero_mask] = dot_products[0, non_zero_mask] / denominators[non_zero_mask]
    most_similar_idx = np.argmax(sim_scores)
    most_similar_segment = combined_output["segmented_data"][most_similar_idx]

    print(f"Prompt: '{prompt}'")
    print(f"Most similar segment summary: '{most_similar_segment['summary_text']}'")
    print(f"Similarity score: {sim_scores[most_similar_idx]:.4f}")
    print(f"Thumbnail: {most_similar_segment['thumbnail_gcs_uri']}")

    return most_similar_segment

prompt = "bell and american woman with us flag"

#%%
most_sim = find_most_similar(prompt)


#%%
import pandas as pd

df = pd.read_pickle("video_gen_dataset.pkl")

#%%

with open("video_gen_dataset.pkl", "rb") as f:
    all_videos = pickle.load(f)


#%%
import json
import time
from typing import List

import vertexai
from google import genai
from google.genai import types
from google.cloud import storage
from vertexai.vision_models import VideoSegmentConfig
from vertexai.vision_models import MultiModalEmbeddingModel, Video

project_id = "vtxdemos"
region = "us-central1"
bucket_name = "vtxdemos-datasets-public"
prefix_bucket = "video_search_app"
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
    print(text)
    print(video)
    try:
        re = gem_model.models.generate_content(
            model=model_gem,
            config=config,
            contents=[
                text,
                video
            ]
        )
        return re.text
    except Exception as e:
        return f"Problems {e}"


#%%

interval_sec = 12

for i in bucket.list_blobs(prefix=prefix_bucket):
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
        print(f"Time taken: {time.time()-start_time}")
        segment_definitions_for_llm = []
        # Also create a map to quickly look up embeddings by their start_offset_sec
        embeddings_map = {} # Key: (start_offset_sec, end_offset_sec), Value: embedding object
        for emb in embeddings.video_embeddings:
            segment_definitions_for_llm.append({
                "start_offset_sec": emb.start_offset_sec,
                "end_offset_sec": emb.end_offset_sec
            })
            embeddings_map[(emb.start_offset_sec, emb.end_offset_sec)] = emb.embedding # Store the actual vector

        num_segments_to_expect = len(segment_definitions_for_llm)

        start_time = time.time()
        response = generate_content(
            segment_definitions_list=segment_definitions_for_llm,
            number_of_segments_to_generate=len(embeddings.video_embeddings),
            video_uri=f"{'gs://'+bucket_name}/{i.name}"
        )
        response_json_str = json.loads(response)

        combined_output = {
            "video_title": response_json_str.get("title", "No Title Provided"),
            "segmented_data": []
        }

        for segment_summary in response_json_str.get("segments_summary", []):
            start_s = segment_summary["start_offset_sec"]
            end_s = segment_summary["end_offset_sec"]
            summary_text = segment_summary["summary_text"]

            embedding_vector = embeddings_map.get((start_s, end_s))
            if embedding_vector:
                combined_output["segmented_data"].append({
                    "start_offset_sec": start_s,
                    "end_offset_sec": end_s,
                    "summary_text": summary_text,
                    "embedding": embedding_vector # Add the embedding vector here
                })
            else:
                print(f"Warning: No embedding found for segment {start_s}-{end_s}")
                combined_output["segmented_data"].append({
                    "start_offset_sec": start_s,
                    "end_offset_sec": end_s,
                    "summary_text": summary_text,
                    "embedding": None
                })
        break
import asyncio
from google.protobuf import duration_pb2
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1 import (
  Content,
  GenerateContentRequest,
  PredictionServiceAsyncClient,
)
from google.cloud.aiplatform_v1.types.content import VideoMetadata, Part, FileData

class Model:
  def __init__(self, project: str, location: str, model: str):
    self.project = project
    self.location = location
    self.model = model

  async def run(self, text: str, video: str, start_offset: int, end_offset: int):
    text_part = Part(
        {
            "text": text
        }
    )
    video_metadata = VideoMetadata(
        start_offset=duration_pb2.Duration(seconds=start_offset),
        end_offset=duration_pb2.Duration(seconds=end_offset),
    )
    input_part = Part(
        {
            "file_data": FileData(
                {
                    "mime_type": "video/*",
                    "file_uri": video
                }
            ),
            "video_metadata": video_metadata,
        }
    )
    self.request = GenerateContentRequest(
        {
            "contents": [
                Content(
                    {
                        "role": "user",
                        "parts": [text_part, input_part]
                    }
                )
            ],
            "model": f"projects/{self.project}/locations/{self.location}/publishers/google/models/{self.model}",
        }
    )
    client: PredictionServiceAsyncClient = initializer.global_config.create_client(
        client_class=PredictionServiceAsyncClient,
        location_override=self.location,
        prediction_client=True,
    )
    return await client.generate_content(self.request)

  async def generate_content(self, prompt: str, yt_link: str, video_length_to_process: int):
    num_chunks = video_length_to_process // 10
    offsets = [(i * 10, (i + 1) * 10) for i in range(num_chunks)]

    async def process_chunk(offset):
      start_offset, end_offset = offset
      return await self.run(prompt, yt_link, start_offset, end_offset)

    results = await asyncio.gather(*(process_chunk(offset) for offset in offsets))

    all_results = []
    for i, result in enumerate(results):
      if result and result.candidates: #Check for valid result and candidates
        first_candidate = result.candidates[0] #Get the first candidate
        extracted_data = {
            "text": first_candidate.content.parts[0].text if first_candidate.content.parts else "",  #Extract text safely
            "prompt_token_count": result.usage_metadata.prompt_token_count,
            "start_offset": (i * 10),
            "end_offset": ((i + 1) * 10),

        }
        all_results.append(extracted_data)
      else:
        print(f"Processing failed for chunk {i}")

    return all_results

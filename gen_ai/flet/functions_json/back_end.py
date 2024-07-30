import json
import base64
import vertexai
from anthropic import AnthropicVertex
from youtube_transcript_api import YouTubeTranscriptApi
from vertexai.generative_models import GenerativeModel
from vertexai.preview.vision_models import ImageGenerationModel

project_id = "vtxdemos"
region = "us-central1"
model_id = "gemini-1.5-flash-001"
anthropic_region = "europe-west1"  # or "us-east5"
imagen_model_id = "imagen-3.0-fast-generate-preview-0611"

vertexai.init(project=project_id, location="us-central1")

client = AnthropicVertex(region=anthropic_region, project_id=project_id)
imagen_model = ImageGenerationModel.from_pretrained(imagen_model_id)

system_instruction = """
You are a universal knowledge chatbot with access to tools to answer questions. 
Follow these instructions:

1. **Analyze Intent:** Carefully determine the user's intent from their prompt.
2. **Tool Usage:**
   - **If the intent is related to 'youtube':**  
      - Extract and provide ONLY the YouTube link in the "youtube" field. 
      - I will then provide you with the transcript of that video.
   - **If the intent is related to 'bananas':** 
      - Rephrase or enhance the user's prompt to be a clear and concise request for a banana-related tool. Place this modified prompt in the "bananas" field.  
      - I will then provide you with the output from that tool.
   - **If the intent is related to 'imagen':**  
      - Rephrase or enhance the user's prompt to get the best quality image generation.
      - I will then provide you with the output from that tool.
3. **General Knowledge:** If the intent does not require using 'youtube' or 'bananas', provide a concise answer directly in the "answer" field.
4. **Use the Provided Context:**  If you use the 'youtube' or 'bananas' tools, wait for me to provide additional information (the "context"). Use this context to formulate your final answer in the "answer" field. 

always use "answer" to answer the question.

**Output Format (JSON):**
{
"general": "<The user's prompt IF it doesn't fit the 'youtube' or 'bananas' intent, otherwise leave as an empty string>",
"youtube": "<The extracted YouTube link, or an empty string>",
"bananas": "<The modified/improved prompt for the banana tool, or an empty string>",
"imagen": "<The modified/improved prompt for the imagen tool, or an empty string>"
"answer": "<Your direct answer to the prompt IF it's not related to tools, OR your answer based on the provided context>" 
}
"""

model = GenerativeModel(
    model_id,
    system_instruction=[system_instruction]
)

chat = model.start_chat()

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json"
}


def youtube(prompt: str, youtube_url: str):
  print("Gather Transcription")
  transcript = "".join([chunk["text"] for chunk in
                        YouTubeTranscriptApi.get_transcript(youtube_url.split("v=")[-1])])
  contents = [prompt, f"Video Transcription: {transcript}"]
  print(contents)
  print("Using the Gemini")
  ll_model = GenerativeModel(model_id)
  response = ll_model.generate_content(contents)
  print("Gemini Finished...")

  return response.text

def send_recipe(prompt: str,):
  message = client.messages.create(
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": "Send me a recipe for banana bread.",
          }
      ],
      model="claude-3-5-sonnet@20240620",
  )
  response = json.loads(message.model_dump_json(indent=2))["content"][0]["text"]
  print("Anthropic Response:")
  print(response)
  return response

def image_gen(prompt: str):
  print("Image generation started...")
  response = imagen_model.generate_images(
      prompt=prompt,
      number_of_images=2,
      add_watermark=True,
      aspect_ratio="16:9",
      language="en",
      guidance_scale=7.5,
  )
  print("Image Done!")
  src_base64 = base64.b64encode(response[0]._loaded_bytes).decode('utf-8')
  return src_base64

def chatbot(prompt: str):
  _ = json.loads(chat.send_message(
      [prompt],
      generation_config=generation_config,
  ).text)

  print(_)

  if _["youtube"] != "":
    context = youtube(prompt=prompt, youtube_url=_["youtube"])
    return json.loads(chat.send_message(
        [f"original_prompt: {prompt}, context: {context}"],
        generation_config=generation_config,
    ).text)
  elif _["bananas"] != "":
    context = send_recipe(prompt)
    return json.loads(chat.send_message(
        [f"original_prompt: {prompt}, context: {context}"],
        generation_config=generation_config,
    ).text)
  elif _["imagen"] != "":
    src_base64 = image_gen(_["imagen"])
    _res = json.loads(chat.send_message(
        [f"""original_prompt: {prompt}, 
        context: Because you are generating an image, 
        just answer that you have done it"""],
        generation_config=generation_config,
    ).text)
    print(_res)
    _res["image_src64"] = src_base64
    return _res
  else:
    return _

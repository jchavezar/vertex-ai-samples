#%%
import io
import ssl
import time
import filetype
import vertexai
from pytube import YouTube
from vertexai.generative_models import GenerativeModel, Part, Tool

ssl._create_default_https_context = ssl._create_unverified_context

vertexai.init(project="vtxdemos", location="us-central1")

# Functions Calling

youtube_search_tool = {
    "name": "youtube_search_tool",
    "description": "Use any youtube video to get information from, the user would try to ask anything regarding youtube video link",
    "parameters": {
        "type": "object",
        "properties": {
            "link": {
                "type": "string",
                "description": "the youtube link of the video"
            },
        },
        "required": [
            "link"
        ]
    }
}


all_tools = Tool.from_dict(
    {
        "function_declarations": [
            youtube_search_tool,
        ]
    }
)

model = GenerativeModel(
    model_name="gemini-1.5-flash-preview-0514",
    tools=[all_tools],
)
chat = model.start_chat()

def get_video_bytes_and_mimetype(youtube_url):
  yt = YouTube(youtube_url)
  stream = yt.streams.get_lowest_resolution()

  buffer = io.BytesIO()
  stream.stream_to_buffer(buffer)
  video_bytes = buffer.getvalue()

  # Reset buffer position before MIME type detection
  buffer.seek(0)
  kind = filetype.guess(buffer)
  mime_type = kind.mime if kind else "video/unknown"

  return video_bytes, mime_type

def llm(prompt):

  response = chat.send_message(prompt)

  try:
    function_call = response.candidates[0].function_calls[0]

    if function_call.name == "youtube_search_tool":
      link = function_call.args["link"]
      video_bytes, mime_type = get_video_bytes_and_mimetype(link)
      video1_1 = Part.from_data(mime_type=mime_type, data=video_bytes)

      contents = [video1_1, prompt]

      ll_model = GenerativeModel(model_name="gemini-1.5-flash-preview-0514")
      response = ll_model.generate_content(contents)

  except:
    return response.text


  response = chat.send_message(
      Part.from_function_response(
          name="youtube_search_tool",
          response={
              "content": response.text,
          },
      ),
  )

  print(response.text)
  return response.text



def run(text: str = ""):
  start_time = time.time()
  print("Running...")
  response = llm(text)
  end_time = time.time()
  job_time = end_time - start_time
  print(f"Time taken: {job_time} seconds")
  return response, round(job_time,2)

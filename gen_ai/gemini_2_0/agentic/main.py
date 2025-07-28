#%%
from flet import *
from google import genai
from google.genai import types


# Backend
client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="us-central1",
)

system_instruction = """
  You are a very friendly chatbot, your name is murderbot.
  Use the following tools ONLY to find the true:
  
  - 1 Vertex AI Search Grounding.
  - 2 Your knowledge data (Knowledge Data) used during your training.
  
  > Notes: 
  Tool 1 contains movies metadata, so use semantic representation of the title for your matches, it does not need to be exactly the title.
  Tool 1 schema: budget, genres, original language, release date, poster path, revenue, tagline, title, vote average, vote count
  
  Rules:
  * **Character:** Based on the user feed create a character of yourself that adapts to its speaking and respond in the same tone.
  * **Sequence is Key:** User the tool number 1 (VAIS) first, use tool number 2 if 1 (VAIS) doesn't have the answer.
  * **Output Format:** The output is raw text with the tool used at the end.
  * **Brief Explain:** Briefly explain if you either or not find information in tool 1 and/or 2.
  E.g.
  Response: your response
  Data Source Reference: Vertex AI Search
  
  * **What not to do**:
  Never use any other tool like Google Search.
  """
chat_history = []

def conversation_ai(prompt: str):

  input_text = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
  chat_history.append(input_text)

  tools = [
      types.Tool(retrieval=types.Retrieval(vertex_ai_search=types.VertexAISearch(datastore="projects/vtxdemos/locations/global/collections/default_collection/dataStores/kaggle-movies_1692703558099"))),
  ]

  config = types.GenerateContentConfig(system_instruction=system_instruction, tools=tools)

  response = client.models.generate_content(
      model="gemini-2.0-flash-001",
      contents=chat_history,
      config=config
  )
  chat_history.append(response.text)
  return response.text

# FrontEnd

def main(page: Page):
  page_width = page.width
  page_height = page.height

  def send_message(e):
    print(e.data)
    re=conversation_ai(e.data)
    primary.content=Text(re)
    primary.update()

  primary: Container=Container(
      alignment=alignment.center,
      height=page_height*.80,
      bgcolor=Colors.AMBER_100,
      content=Text("hi"),
  )
  secondary: Container=Container(
      height=page_height*.20,
      bgcolor=Colors.BLUE_100,
      content=Container(
          height=200,
          expand=True,
          content=TextField(
              label="Write something...",
              on_submit=send_message
          )
      )
  )

  main_layout: Column=Column(
  controls=[
      primary,
      secondary
      ]
  )
  page.add(main_layout)
app(target=main)
import time
import vertexai
from flet import *
from text_to_summarize import text
from vertexai.generative_models import GenerativeModel, Tool
import vertexai.preview.generative_models as generative_models

# Vertex AI initialization
vertexai.init(project="vtxdemos", location="us-central1")
tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(disable_attribution=False)
    ),
]

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

model = GenerativeModel(
    "gemini-1.5-flash-001",
    tools=tools,
)


def main(page: Page):
  context = text
  summary_text: Text = Text()
  response_text: Text = Text()

  summary_box: Container = Container(
      border_radius=12,
      padding=12,
      margin=margin.only(top=12, bottom=12),
      content=summary_text,
  )

  def chat_message(message):
    text = message.control.value
    me = Text("")
    chat_message_view.controls.append(
        Column(
            controls=[
                Text("You:", style=TextStyle(color=colors.BLUE_GREY_900, weight="bold")),
                me
            ]
        )
    )

    for character in text:
      me.value += character
      time.sleep(0.005)
      chatbot.update()

    chatbot.content.controls[0].update()
    try:
      response = model.generate_content(
          [text],
          generation_config=generation_config,
          safety_settings=safety_settings,
      )
      gemini_response = Text("")
      chat_message_view.controls.append(
          Column(
              controls=[
                  Divider(height=10, color=colors.TRANSPARENT),
                  Text("Gemini:", style=TextStyle(color=colors.BLUE_GREY_900, weight="bold")),
                  gemini_response
              ]
          )
      )
      for character in response.text:
        gemini_response.value += character
        time.sleep(0.005)
        chat_message_view.update()
      chatbot.update()
    except Exception as err:
      summary_text.value = f"Error generating summary: {err}"

  def summarization(e):
    nonlocal context
    try:
      response = model.generate_content(
          [
              f"""
              Give me a summary of the following

              <context>
              {context}
              </context>
              """
          ],
          generation_config=generation_config,
          safety_settings=safety_settings,
      )
      summary_text.value = response.text
      summary_box.bgcolor = colors.BLUE_GREY_100
    except Exception as err:
      summary_text.value = f"Error generating summary: {err}"

    page.update()

  button1: ElevatedButton = ElevatedButton("summarization", on_click=summarization)

  widgets: Container = Container(
      border=border.all(1, colors.GREY),
      border_radius=12,
      padding=12,
      margin=margin.only(left=40, top=12, bottom=12),
      # Use expand with a flex value for dynamic sizing
      expand=1,
      content=Column(
          controls=[
              Container(
                  content=button1,
              ),
              summary_box,
          ]
      ),
  )

  chat_message_view: ListView = ListView(
      height=500,
      auto_scroll=True,
      controls=[response_text],
  )

  chatbot: Container = Container(
      border=border.all(1, colors.GREY),
      border_radius=12,
      padding=12,
      margin=margin.only(right=40, top=12, bottom=12),
      # Use expand with a flex value for dynamic sizing
      expand=1,
      content=Column(
          alignment=MainAxisAlignment.SPACE_BETWEEN,
          controls=[
              chat_message_view,
              TextField(
                  "How can I help you?",
                  on_submit=chat_message,
              )
          ]
      ),
  )

  divider: VerticalDivider = VerticalDivider(width=10)

  main_dash: Row = Row(
      alignment=MainAxisAlignment.SPACE_EVENLY,
      controls=[
          widgets,
          divider,
          chatbot,
      ],
      # Ensure the Row expands to fill available space
      expand=True,
  )

  page.add(main_dash)

app(target=main)
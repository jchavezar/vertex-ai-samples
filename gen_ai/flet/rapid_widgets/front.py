import json
import time
import vertexai
from flet import *
from text_to_summarize import conversation_text, example
from vertexai.generative_models import GenerativeModel, Tool
import vertexai.preview.generative_models as generative_models

# Vertex AI initialization
vertexai.init(project="vtxdemos", location="us-central1")
tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(
            disable_attribution=False)
    ),
]

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

summary_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

chat_model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=[
        """
        You are a capsule (online pharmacy assistant), your mission is to help users to either buy or refill any kind of medications,
        anything is allowed, the questions to fill their prescription should be around:
        - Name
        - Name of the medicine
        - Address
        """
    ],
    # tools=tools,
)

summary_model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=[
        conversation_text
    ],
    tools=tools,
)

chat_model = chat_model.start_chat()
chat_history = []

def main(page: Page):
  context = example
  summary_response_inquiry: Text = Text()
  summary_response_text: Text = Text()
  response_text: Text = Text()
  duration: Text = Text()

  summary_path: Container = Container(
      content=Column(
      )
  )


  def chat_message(message):
    text = message.control.value
    me = Text("", style=TextStyle(size=15))
    chat_message_view.controls.append(
        Column(
            controls=[
                Text(
                    "You:",
                    style=TextStyle(color=colors.BLUE_GREY_900,
                                    weight="bold", size=15)),
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
      response = chat_model.send_message(
          [text],
          generation_config=generation_config,
          safety_settings=safety_settings
      )
      gemini_response = Text("")
      chat_message_view.controls.append(
          Column(
              controls=[
                  Divider(height=10, color=colors.TRANSPARENT),
                  Row(
                      controls=[
                          Text("Agent:", style=TextStyle(color=colors.BLUE_GREY_900,
                                                          weight="bold", size=15)),
                          Text(style=TextStyle(color=colors.GREEN, size=15))
                      ]
                  ),
                  gemini_response
              ]
          )
      )
      start_time = time.perf_counter()
      for character in response.text:
        gemini_response.value += character
        time.sleep(0.005)
        elapsed_time = time.perf_counter() - start_time
        chat_message_view.controls[-1].controls[1].controls[1].value = f"{elapsed_time:.2f} seconds"
        #duration.value = f"{elapsed_time:.2f} seconds"
        chat_message_view.update()
      chat_input.value = ""
      chat_input.focus()
      page.update()
      chat_history.append({"user": text, "gemini": response.text})
    except Exception as err:
      summary_response_inquiry.value = f"Error generating summary: {err}"
      chat_history.append({"user": text, "gemini": "error"})
    print(len(chat_history))
    if len(chat_history) > 4:
        context = str(chat_history)
        summarization("")

  def summarization(e):
    nonlocal context
    try:
      response = summary_model.generate_content(
          [
              f"""
              <user_input>
              {context}
              </user_input>
              """
          ],
          generation_config=summary_generation_config,
          safety_settings=safety_settings,
      )

      def chat_bot_input_message_box(e):
        chat_input.value = _dict["smart_response"]
        chat_input.focus()
        page.update()

      print(response.text)
      _dict = json.loads(response.text)
      summary_path.content.controls =[
          Text("Inquiry Summary:", style=TextStyle(color=colors.GREY, weight=FontWeight.BOLD, size=20)),
          Text(_dict["inquiry_summary"], style=TextStyle(size=15)),
          Divider(height=5, color=colors.TRANSPARENT),
          Text("Actions Taken:", style=TextStyle(color=colors.GREY, weight=FontWeight.BOLD, size=20)),
          Text(_dict["action"], style=TextStyle(size=15)),
          Divider(height=5, color=colors.TRANSPARENT),
          Container(
              bgcolor=colors.BLUE_GREY_100,
              padding=12,
              border_radius=12,
              content=Column(
                  controls=[
                      Text("Smart Response", style=TextStyle(color=colors.INDIGO, weight=FontWeight.BOLD, size=20)),
                      Container(
                          bgcolor=colors.WHITE,
                          padding=12,
                          border_radius=12,
                          content=Column(
                              controls=[
                                  Row(
                                      alignment=MainAxisAlignment.SPACE_BETWEEN,
                                      controls=[
                                        Text("Suggested Comm", style=TextStyle(weight=FontWeight.BOLD, size=18)),
                                        ElevatedButton(
                                            "Compose Message",
                                            on_click=chat_bot_input_message_box,
                                        ),
                                      ],
                                  ),
                                  Divider(height=15, color=colors.TRANSPARENT),
                                  Text(_dict["smart_response"], style=TextStyle(size=15)),
                              ]
                          )
                      )
                  ]
              )
          ),
      ]
    except Exception as err:
      print(f"Error generating summary: {err}")

    page.update()

  button1: ElevatedButton = ElevatedButton("Smart Response",
                                           on_click=summarization)

  # Left Side Container with Summary
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
                  alignment=alignment.center,
                  content=button1,
              ),
              Divider(height=10, color=colors.TRANSPARENT),
              summary_path,
          ]
      ),
  )

  chat_message_view: ListView = ListView(
      expand=True,
      auto_scroll=True,
      controls=[response_text],
  )

  chat_input : TextField = TextField(
      border_radius=12,
      hint_text="How can I help you?",
      on_submit=chat_message,
  )

  # Right Side Container with Conversational Bot
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
              chat_input
          ],
          expand=True,
          spacing=0
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

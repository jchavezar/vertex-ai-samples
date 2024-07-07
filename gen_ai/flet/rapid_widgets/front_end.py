import json
import time
import logging
import vertexai
from flet import *
from simulating_database import database
from vertexai.generative_models import GenerativeModel, Tool
import vertexai.preview.generative_models as generative_models

# Replace this with your actual example data
example = ""

# Flet Logging
logging.basicConfig(level=logging.DEBUG)

# Vertex AI initialization
vertexai.init(project="vtxdemos", location="us-central1")
tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(
            disable_attribution=False)
    ),
]

chatbot_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
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
        You are a capsule (online pharmacy assistant), your mission is to help
        to order, modify or cancel prescriptions always try to fulfill the following
        requirements:
        - Full Name
        - Phone Number
        - <detect the intent (either order, modify or cancel)>
        
        If the full name and phone number have not been fulfilled the value in json
        should be <String>="None"
        
        <output_in_json>
        gemini_response, full_name, phone_number, intent
        </output_in_json>

        """
    ],
    # tools=tools,
)

summary_model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=[
        f"""
        You are a capsule (online pharmacy) analyst your mission is as follows:
        
        <tasks>
        1. Gather information from the database according and match user name and phone number with the current_dialog.
        2. Generate a brief summary (database_summary) as natural language text.
        2. Generate an inquiry_summary.
        3. Suggest 2 of the actions below based on the information gathered, (order is important prioritize the one based on your intent detections).
        3. Generate a suggested communication (response) for each of the actions.
        </tasks>
         
        <database>
        {database}
        </database>
        
        <actions_to_consider>
        1. cancel
        2. change
        3. confirm
        </actions_to_consider>
        
        <output_json>
        {{
        "database_summary": <database_summary>,
        "inquiry_summary": <inquiry_summary>,
        "actions_to_take": [
        {{<action_suggested_1>: <suggested_communication_1>}}, {{<action_suggested_2>: <suggested_communication_2>}}],
        }}
        </output_json>
        """
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
      content=Column()
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
          generation_config=chatbot_generation_config,
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
      _response = json.loads(response.text)
      for character in _response["gemini_response"]:
        gemini_response.value += character
        time.sleep(0.005)
        elapsed_time = time.perf_counter() - start_time
        chat_message_view.controls[-1].controls[1].controls[1].value = f"{elapsed_time:.2f} seconds"
        #duration.value = f"{elapsed_time:.2f} seconds"
        chat_message_view.update()
      chat_input.value = ""
      chat_input.focus()
      page.update()
      chat_history.append({"user": text, "gemini": _response["gemini_response"]})
    except Exception as err:
      summary_response_inquiry.value = f"Error generating summary: {err}"
      chat_history.append({"user": text, "gemini": "error"})

    if _response["full_name"] != "None" \
        and _response["phone_number"] != "None" and _response["intent"] != "None":
      context = str(chat_history)
      summarization("", chat_res=_response)


  def summarization(e, chat_res):
    nonlocal context
    try:
      response = summary_model.generate_content(
          [
              f"""
                    <current_dialog>
                    chat_history: str({chat_history})
                    name_extracted: {chat_res["full_name"]}
                    phone_extracted: {chat_res["phone_number"]}
                    intent_extracted: {chat_res["intent"]}
                    </current_dialog>
                    """
          ],
          generation_config=summary_generation_config,
          safety_settings=safety_settings,
      )

      def selection(e, content):
        nonlocal suggested_comm_container  # Access the container
        suggested_comm_container.content = Column(
            controls=[
                Row(
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text("Suggested Comm", style=TextStyle(weight=FontWeight.BOLD, size=18)),
                        ElevatedButton(
                            "Compose Message",
                            on_click=lambda e: chat_bot_input_message_box(e, content),
                        ),
                    ],
                ),
                Divider(height=15, color=colors.TRANSPARENT),
                Text(content, style=TextStyle(size=15)),
            ]
        )
        # Make the container visible after setting the content
        suggested_comm_container.visible = True
        page.update()


      def chat_bot_input_message_box(e, content):
        chat_input.value = content
        chat_input.focus()
        page.update()

      _dict = json.loads(response.text)
      action_1, comm_suggested_1 = list(_dict["actions_to_take"][0].items())[0]
      action_2, comm_suggested_2 = list(_dict["actions_to_take"][1].items())[0]

      # Create the container for Suggested Comm, initially hidden
      suggested_comm_container = Container(
          bgcolor=colors.WHITE,
          padding=12,
          border_radius=12,
          visible=False  # Initially hidden
      )

      summary_path.content.controls =[
          Text("Inquiry Summary:", style=TextStyle(color=colors.GREY, weight=FontWeight.BOLD, size=20)),
          Text(_dict["inquiry_summary"], style=TextStyle(size=15)),
          Text("History Summary:", style=TextStyle(color=colors.GREY, weight=FontWeight.BOLD, size=20)),
          Text(_dict["database_summary"], style=TextStyle(size=15)),
          Divider(height=5, color=colors.TRANSPARENT),
          Divider(height=5, color=colors.TRANSPARENT),
          Container(
              bgcolor=colors.BLUE_GREY_100,
              padding=12,
              border_radius=12,
              content=Column(
                  controls=[
                      Text("Actions Suggested", style=TextStyle(color=colors.INDIGO, weight=FontWeight.BOLD, size=20)),
                      Container(
                          bgcolor=colors.WHITE10,
                          width=250,
                          padding=5,
                          border_radius=12,
                          content=Column(
                              alignment=MainAxisAlignment.CENTER,
                              controls=[
                                  Row(
                                      alignment=MainAxisAlignment.SPACE_BETWEEN,
                                      controls=[
                                          ElevatedButton(
                                              action_1,
                                              on_click=lambda e: selection(e, comm_suggested_1),
                                          ),
                                          ElevatedButton(
                                              action_2,
                                              on_click=lambda e: selection(e, comm_suggested_2),
                                          ),
                                      ],
                                  ),
                              ]
                          )
                      ),
                      # Add the Suggested Comm container here
                      suggested_comm_container
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
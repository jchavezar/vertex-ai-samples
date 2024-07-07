import json
import time
import vertexai
from flet import *
from text_to_summarize import conversation_text, example  # Assuming these are defined elsewhere
from vertexai.generative_models import GenerativeModel, Tool
import vertexai.preview.generative_models as generative_models

# Vertex AI initialization
vertexai.init(project="vtxdemos", location="us-central1")

# Define tools for the models (currently only used by the summary model)
tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(
            disable_attribution=False)
    ),
]

# Configuration for text generation
generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens in the generated response
    "temperature": 1,            # Controls the randomness of the response (higher = more random)
    "top_p": 0.95,              # Controls the diversity of the response
}

# Configuration for summary generation (JSON format)
summary_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",  # Expect JSON response
}

# Safety settings for the models
safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

# Initialize the chat model
chat_model = GenerativeModel(
    "gemini-1.5-flash-001",  # Model ID
    system_instruction=[
        """
        You are a capsule (online pharmacy assistant), your mission is to help users to either buy or refill any kind of medications,
        anything is allowed, the questions to fill their prescription should be around:
        - Name
        - Name of the medicine
        - Address
        """
    ],
    # tools=tools,  # Tools are not used for the chat model in this version
)

# Initialize the summary model
summary_model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=[
        conversation_text  # Assumes `conversation_text` contains initial instructions for summarization
    ],
    tools=tools,  # Summary model uses tools for grounding
)

# Start the chat session
chat_model = chat_model.start_chat()
chat_history = []  # Store the conversation history

# --- Main Flet application ---
def main(page: Page):
  context = example  # Initial context for summarization
  summary_response_inquiry: Text = Text()  # Placeholder for inquiry summary
  summary_response_text: Text = Text()    # Placeholder for general summary
  response_text: Text = Text()           # Placeholder for response text
  duration: Text = Text()                 # Placeholder for response time

  # Container for the summary section
  summary_path: Container = Container(
      content=Column()  # Initially empty, will be populated later
  )

  # Function to handle user chat messages
  def chat_message(message):
    text = message.control.value  # Get the user's message
    me = Text("", style=TextStyle(size=15))  # Placeholder for displaying user message
    chat_message_view.controls.append(  # Add user message to the chat view
        Column(
            controls=[
                Text("You:", style=TextStyle(color=colors.BLUE_GREY_900, weight="bold", size=15)),
                me
            ]
        )
    )

    # Animate the user message typing effect
    for character in text:
      me.value += character
      time.sleep(0.005)
      chatbot.update()

    chatbot.content.controls[0].update()

    try:
      # Send the user message to the chat model
      response = chat_model.send_message(
          [text],
          generation_config=generation_config,
          safety_settings=safety_settings
      )

      gemini_response = Text("")  # Placeholder for displaying the model's response
      # Add the model's response to the chat view
      chat_message_view.controls.append(
          Column(
              controls=[
                  Divider(height=10, color=colors.TRANSPARENT),
                  Row(
                      controls=[
                          Text("Agent:", style=TextStyle(color=colors.BLUE_GREY_900, weight="bold", size=15)),
                          Text(style=TextStyle(color=colors.GREEN, size=15))  # Placeholder for response time
                      ]
                  ),
                  gemini_response
              ]
          )
      )

      # Animate the model's response typing effect and measure response time
      start_time = time.perf_counter()
      for character in response.text:
        gemini_response.value += character
        time.sleep(0.005)
        elapsed_time = time.perf_counter() - start_time
        chat_message_view.controls[-1].controls[1].controls[1].value = f"{elapsed_time:.2f} seconds"
        chat_message_view.update()

      # Clear the input field and focus it for the next message
      chat_input.value = ""
      chat_input.focus()
      page.update()

      # Append the interaction to the chat history
      chat_history.append({"user": text, "gemini": response.text})

    except Exception as err:
      summary_response_inquiry.value = f"Error generating summary: {err}"
      chat_history.append({"user": text, "gemini": "error"})

    # Trigger summarization if the chat history has more than 4 interactions
    print(len(chat_history))
    if len(chat_history) > 4:
      context = str(chat_history)
      summarization("")

  # Function to handle summarization
  def summarization(e):
    nonlocal context  # Modify the context variable outside the function scope
    try:
      # Send the chat history to the summarization model
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

      # Function to populate the chat input with the suggested response
      def chat_bot_input_message_box(e):
        chat_input.value = _dict["smart_response"]
        chat_input.focus()
        page.update()

      print(response.text)
      _dict = json.loads(response.text)  # Parse the JSON response

      # Update the summary section with the extracted information
      summary_path.content.controls = [
          Text("Inquiry Summary:", style=TextStyle(color=colors.GREY, weight=FontWeight.BOLD, size=20)),
          Text(_dict["inquiry_summary"], style=TextStyle(size=15)),
          Divider(height=5, color=colors.TRANSPARENT),
          Text("Actions Taken:", style=TextStyle(color=colors.GREY, weight=FontWeight.BOLD, size=20)),
          Text(_dict["action"], style=TextStyle(size=15)),
          Divider(height=5, color=colors.TRANSPARENT),
          # Container for Smart Response
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
                                              on_click=chat_bot_input_message_box,  # Button to use the suggested response
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

  # Button to trigger summarization (not used currently)
  button1: ElevatedButton = ElevatedButton("Smart Response", on_click=summarization)

  # Left side container for the summary section
  widgets: Container = Container(
      border=border.all(1, colors.GREY),
      border_radius=12,
      padding=12,
      margin=margin.only(left=40, top=12, bottom=12),
      expand=1,  # Expand to fill available space
      content=Column(
          controls=[
              Container(
                  alignment=alignment.center,
                  content=button1,
              ),
              Divider(height=10, color=colors.TRANSPARENT),
              summary_path,  # The summary section container
          ]
      ),
  )

  # Chat message view (displays the conversation)
  chat_message_view: ListView = ListView(
      expand=True,
      auto_scroll=True,
      controls=[response_text],
  )

  # Chat input field
  chat_input: TextField = TextField(
      border_radius=12,
      hint_text="How can I help you?",
      on_submit=chat_message,  # Call the chat_message function when Enter is pressed
  )

  # Right side container for the chatbot interface
  chatbot: Container = Container(
      border=border.all(1, colors.GREY),
      border_radius=12,
      padding=12,
      margin=margin.only(right=40, top=12, bottom=12),
      expand=1,  # Expand to fill available space
      content=Column(
          alignment=MainAxisAlignment.SPACE_BETWEEN,
          controls=[
              chat_message_view,  # The chat message display area
              chat_input           # The chat input field
          ],
          expand=True,
          spacing=0
      ),
  )

  divider: VerticalDivider = VerticalDivider(width=10)  # Divider between left and right sections

  # Main layout row (left side: summary, right side: chatbot)
  main_dash: Row = Row(
      alignment=MainAxisAlignment.SPACE_EVENLY,
      controls=[
          widgets,     # Left side container
          divider,     # Divider
          chatbot,    # Right side container
      ],
      expand=True,  # Expand the row to fill available space
  )

  page.add(main_dash)  # Add the main layout to the page

# Run the Flet application
app(target=main)
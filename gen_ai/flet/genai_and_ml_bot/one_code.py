import json
from typing import Dict

import vertexai
import flet as ft
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from vertexai.generative_models import GenerativeModel

project_id = "vtxdemos"

vertexai.init(project=project_id, location="us-central1")

system_instruction='''
You are a friendly and helpful conversational chatbot. You can answer a wide range of questions. 

ONLY If asked to predict if a customer will buy on a return visit, you need additional information.  You should politely ask the user for the following information, one question at a time, until you have all the details:

* **Latest Ecommerce Progress:** What is the customer's progress in the checkout process? (For example: 1 = added to cart, 2 = entered shipping info, 3 = completed payment)
* **Bounces:** How many times has the customer visited the website but left after viewing only one page?
* **Time on Site:** How many seconds did the customer spend on the website during their last visit?
* **Pageviews:** How many pages did the customer view during their last visit?
* **Source:** Where did the customer come from? (For example: Google, Facebook, newsletter)
* **Medium:** What marketing medium brought the customer to the website? (For example: organic, cpc, email)
* **Channel Grouping:** What is the overall channel grouping of the customer's visit? (For example: Organic Search, Paid Search, Direct)
* **Device Category:** What type of device did the customer use? (For example: desktop, mobile, tablet)
* **Country:** What country is the customer located in?

*Rule*
If field is not fulfilled value should be an empty string.

Once you have gathered all the necessary information, let the user know you have everything you need. You don't need to make the prediction yourself, just gather the data.
{ "response": "<your response>", 
  "fulfilled": <true or false (true only if all Fields_required_for_point_2 are filled)>, 
  "latest_ecommerce_progress" :  <a number or empty if not fulfilled (integer)>, 
  "bounces" :  <a number or empty if not fulfilled (integer)>, 
  "time_on_site": <a number or empty if not fulfilled (integer)>, 
  "pageviews": <a number or empty if not fulfilled (integer)>, 
  "source": <a string or empty if not fulfilled>, 
  "medium": <a string or empty if not fulfilled>, 
  "channelGrouping": <a string or empty if not fulfilled>, 
  "deviceCategory": <a string or empty if not fulfilled>, 
  "country": <a string or empty if not fulfilled> }
**Output your responses in this JSON format:**
'''

chatbot_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
}

chat_model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=system_instruction
)
chat = chat_model.start_chat()

# Vertex Endpoint
resource_name = aiplatform.Endpoint.list(filter='display_name=catboost-inference-ep')[0].resource_name
endpoint = aiplatform.Endpoint(endpoint_name=resource_name)

def machine_learning_prediction(input_dict: Dict):
  filtered_input_dict = {k: [v] for k, v in input_dict.items() if k not in ("response", "fulfilled")}
  instances = [json_format.ParseDict(instance_dict, Value()) for instance_dict in [filtered_input_dict]]
  parameters = json_format.ParseDict({}, Value())
  response = endpoint.predict(instances=instances, parameters=parameters).predictions
  return f"""
  Context: 0.0 means No and 1 or 1.0 means Yes
  Function Response:
  Customer will return on visit: {str(response)}"""

def main(page: ft.Page):
  page.title = "Gemini Chatbot"
  page.vertical_alignment = ft.MainAxisAlignment.CENTER
  status_bar: ft.Text = ft.Text("Ready", size=14, color="black")
  page.session.context = ""
  messages = ft.ListView(
      auto_scroll=True,
      expand=True,
      spacing=10,
      padding=20)

  def send_message(e):
    user_message = user_input.value
    messages.controls.append(
        ft.Row(
            [
                ft.Container(
                    content=ft.Text(f"You: {user_message}", size=14,
                                    color="black"),
                    padding=10,
                    border_radius=ft.border_radius.all(20),
                    expand=True,
                    width=400
                ),
                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.END,
        )
    )
    user_input.value = ""
    user_input.focus()
    messages.update()

    # Send user message to the Flask server

    data = chat.send_message(
        [
            f"""
            Query:
            {user_message}
            """
        ],
        generation_config=chatbot_generation_config
    ).text
    re = json.loads(data)

    if re["fulfilled"] == False:
      pass
    else:
      ml_re = machine_learning_prediction(re)
      data = chat.send_message([
          f'''
          Fulfilled answer from ML:
          {ml_re}
          
          Original Query: {str(re)}
          
          Output in JSON:
          {{"response: <your response>", "fulfilled": <true or false>}}
          ''']
      ).text
      print(data)
      re = json.loads(data)

    # Display chatbot response in the chat window
    messages.controls.append(
        ft.Row(
            [
                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
                ft.Container(
                    content=ft.Text(f"Chatbot: {re['response']}", size=14, color="black"),
                    padding=10,
                    border_radius=ft.border_radius.all(20),
                    bgcolor=ft.colors.GREY_50,
                    # Lighter indigo for chatbot bubble
                    expand=True,
                    width=400
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
    )

    panel_logs = []

    for k, v in re.items():
      if k not in ("response", "fulfilled") and v != "":
        panel_logs.append(
            ft.Text(f"{k}: {str(v)}", size=14, color="black")
        )
    tracking_bar.content.controls = panel_logs
    tracking_bar.update()

    # Scroll to the latest message

    messages.page.scroll = "always"
    messages.update()

  def upload_file(e):
    file_picker.pick_files(allow_multiple=False)

  def on_file_picker_result(e):
    # global context
    if file_picker.result:
      file = file_picker.result.files[0]

      messages.controls.append(
          ft.Row(
              [
                  ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
                  ft.Text(f"Extraction: done", size=14, color="black"),
                  # ft.Markdown(
                  #     page.session.context,
                  #     selectable=True,
                  #     on_tap_link=lambda e: page.launch_url(e.data)
                  # )
              ],
              alignment=ft.MainAxisAlignment.END,
          )
      )

      status_bar.value = "Done!"
      messages.update()
      status_bar.update()

      # Scroll to the latest message
      messages.page.scroll = "auto"

  user_input = ft.TextField(
      hint_text="Type your message here...",
      on_submit=send_message,
      expand=True,
  )

  file_picker = ft.FilePicker(on_result=on_file_picker_result)

  document: ft.Container = ft.Container(
      height=30,
      width=100,
      alignment=ft.alignment.center,
      border_radius=ft.border_radius.all(12.0),
      border=ft.border.all(1, ft.colors.GREY),
      content=ft.Text("pdf", size=14, color="black")
  )

  tracking_bar: ft.Container = ft.Container(
      alignment=ft.alignment.center,
      width=300,
      border_radius=ft.border_radius.all(12.0),
      border=ft.border.all(1, ft.colors.GREY),
      content=ft.Column(
          expand=True,
          alignment=ft.MainAxisAlignment.CENTER,
          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          controls=[
          ],
      )
  )

  page.add(
      ft.AppBar(
          title=ft.Text("Gemini Chatbot"),
          center_title=True),
      ft.Column(
          controls=
          [
              ft.Container(
                  expand=True,
                  padding=10,
                  border_radius=12.0,
                  border=ft.border.all(1, ft.colors.GREY),
                  content=ft.Row(
                      controls=[
                          messages,
                          tracking_bar
                      ]
                  ),
              ),
              ft.Row(
                  [
                      status_bar,
                  ],
                  alignment=ft.MainAxisAlignment.CENTER,
              ),
              ft.Container(
                  border=ft.border.all(1, ft.colors.GREY),
                  border_radius=12,
                  content=ft.Row(
                      [
                          user_input,
                          ft.IconButton(icon=ft.icons.SEND,
                                        on_click=send_message),
                          ft.ElevatedButton(on_click=upload_file,
                                            content=ft.Icon(
                                                ft.icons.ATTACH_FILE)),
                      ]
                  ),
                  padding=10,
              ),
          ],
          expand=True,
      ),
      file_picker,
  )


ft.app(target=main)
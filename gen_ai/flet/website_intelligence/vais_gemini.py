import flet as ft
from typing import Dict

from flet_core import FontWeight
from flet_core import MainAxisAlignment
from flet_core import ScrollMode
from flet_core import TextStyle
from google.cloud import aiplatform
from google.protobuf.json_format import MessageToDict
from mpmath import FPContext
from openai.types.beta.threads import ImageFile
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from google.cloud import discoveryengine_v1 as discoveryengine

project_id = "vtxdemos"
vais_location = "global"
engine_id = "verano_1724170347575"

client = discoveryengine.SearchServiceClient(client_options=None)
serving_config = f"projects/{project_id}/locations/{vais_location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"
serving_config = f"projects/390227712642/locations/global/collections/default_collection/engines/verano_1724170347575/servingConfigs/default_search"

content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True
    ),
    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=5,
        include_citations=True,
        ignore_adversarial_query=True,
        ignore_non_summary_seeking_query=True,
        # model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
        #     preamble="YOUR_CUSTOM_PROMPT"
        # ),
        model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
            version="stable",
        ),
    ),
)


chatbot_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    # "response_mime_type": "application/json",
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

chat_model = GenerativeModel(
    "gemini-1.5-flash-001",
)
chat = chat_model.start_chat()

# Vertex Endpoint
resource_name = aiplatform.Endpoint.list(filter='display_name=catboost-inference-ep')[0].resource_name
endpoint = aiplatform.Endpoint(endpoint_name=resource_name)

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
    tracking_bar.content.controls.clear()
    user_message = user_input.value
    messages.controls.append(
        ft.Row(
            [
                ft.Container(
                    content=ft.Text(f"You: {user_message}", size=20,
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
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=user_message,
        page_size=10,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)
    results = []
    for result in response.results:
      results.append(MessageToDict(result.document._pb))
    _res = [i['derivedStructData']['pagemap']['metatags'][0]['og:description'] for i in results]

    metadata = []
    for i in results:
      metadata.append({
          "title": i['derivedStructData']['pagemap']['metatags'][0]['twitter:title'],
          "description": i['derivedStructData']['pagemap']['metatags'][0]['og:description'],
          "url": i['derivedStructData']['pagemap']['metatags'][0]['og:url'],
          "image": i['derivedStructData']['pagemap']['metatags'][0]['og:image'],
          "reviews": i['derivedStructData']['pagemap']['metatags'][0]['twitter:description'],
      })
    print(metadata)
    for data in metadata:
      tracking_bar.content.controls.append(
          ft.Image(
              width=200,
              height=200,
              src=data["image"]
          )
      )
      print(data["url"])
      tracking_bar.content.controls.append(
          ft.Text(
              spans=[
                  ft.TextSpan(data["reviews"]),
                  ft.TextSpan("\n  \n"),
                  ft.TextSpan(
                      data["url"],
                      ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, color=ft.colors.BLUE),
                      on_click=lambda e, url=data["url"]: page.launch_url(str(url))
                  ),
              ]
          )
      )
      tracking_bar.update()

    data = chat.send_message(
        [
            f"""
            From the following context try to respond to the query:
            
            Rules:
            Respond does not have to be accurate, just be friendly and always have an answer.
            
            Context:
            {str(metadata)}
            
            Query:
            {user_message}
            
            A concise with the reference link, Response:
            
            """
        ],
        generation_config=chatbot_generation_config,
        safety_settings=safety_settings
    ).text


    # Display chatbot response in the chat window
    messages.controls.append(
        ft.Row(
            [
                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
                ft.Container(
                    bgcolor=ft.colors.PINK,
                    content=ft.Text(data, size=20, color="white", selectable=True),
                    padding=10,
                    border_radius=ft.border_radius.all(20),
                    #bgcolor=ft.colors.GREY_50,
                    # Lighter indigo for chatbot bubble
                    expand=True,
                    width=400
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
    )

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
      padding=12,
      width=500,
      border_radius=ft.border_radius.all(12.0),
      border=ft.border.all(1, ft.colors.GREY),
      content=ft.Column(
          expand=True,
          scroll=ScrollMode.AUTO,
          alignment=ft.MainAxisAlignment.CENTER,
          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          controls=[
          ],
      )
  )

  def handle_close(e):
    page.close(dlg_modal)

  def open_dlg(e):
    page.overlay.append(dlg_modal)
    dlg_modal.open = True
    page.update()

  dlg_modal = ft.AlertDialog(
      modal=True,
      title=ft.Text("Diagram"),
      content=ft.Container(
          width=500,
          height=500,
          content=ft.Image(src="./website_intelligence.png", fit=ft.ImageFit.CONTAIN)
      ),
      actions=[
          ft.TextButton("Close", on_click=handle_close),
      ]
  )

  page.add(
      ft.AppBar(
          title=ft.Column(
              controls=[
                  ft.Row(
                      alignment=MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.Image(
                              src="https://verano.com/wp-content/uploads/2021/11/Verano_Blk_RGB.svg"
                          ),
                          # ft.Text("Google Gemini Chatbot", style=TextStyle(color=ft.colors.BLACK12, size=28, weight=FontWeight.BOLD)),
                          ft.Text(
                              spans=[
                                  ft.TextSpan(
                                      "Google Gemini Chatbot",
                                      ft.TextStyle(
                                          size=26,
                                          weight=ft.FontWeight.BOLD,
                                          foreground=ft.Paint(
                                              gradient=ft.PaintLinearGradient(
                                                  (0,50), (0,25), [ft.colors.BLUE, ft.colors.PINK]
                                              )
                                          )
                                      )
                                  )
                              ]
                          )
                      ]
                  )
              ]
          ),
          center_title=True),
      ft.Column(
          controls=
          [
              ft.Container(
                  height=30,
                  content=ft.ElevatedButton("Diagram", on_click=open_dlg)
              ),
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


ft.app(target=main, assets_dir="assets")
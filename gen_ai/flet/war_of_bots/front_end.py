import json
import time
import logging
from back_end import *
from flet import *

# Replace this with your actual example data
example = ""

# Flet Logging
#logging.basicConfig(level=logging.DEBUG)


def main(page: Page):
  page.bgcolor = colors.WHITE
  page.title = "War of Bots"
  page.update()
  context = example
  chat_gpt_response: Text = Text("")
  gemini_response: Text = Text("")
  summary_response_inquiry: Text = Text()
  summary_response_text: Text = Text()
  response_text: Text = Text()
  duration: Text = Text()
  duration: Text = Text()

  def typescript(text, chat_gpt=True):
    start_time = time.perf_counter()
    if chat_gpt:
      for character in text:
        bots_view.controls[-1].controls[2].value += character
        # chat_gpt_response.value += character
        time.sleep(0.005)
        elapsed_time = time.perf_counter() - start_time
        bots_view.controls[-1].controls[1].controls[0].value = "ChatGPT:"
        bots_view.controls[-1].controls[1].controls[1].value = f"{elapsed_time:.2f} seconds"
        duration.value = f"{elapsed_time:.2f} seconds"
        bots_view.update()
    else:
      for character in text:
        bots_view.controls[-1].controls[2].value += character
        # gemini_response.value += character
        time.sleep(0.005)
        elapsed_time = time.perf_counter() - start_time
        bots_view.controls[-1].controls[1].controls[0].value = "Gemini:"
        bots_view.controls[-1].controls[1].controls[1].value = f"{elapsed_time:.2f} seconds"
        duration.value = f"{elapsed_time:.2f} seconds"
        bots_view.update()


  def open_grounding_dialog(e, justification, veracity, citations):
    dlg = AlertDialog(
        content=Column(
            controls=[
                Text(f"Justification: {justification}"),
                Text(f"Veracity: {veracity}"),
                Text(f"Citations: {citations}")
            ]
        )
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


  def chat_message(message):
    text = message.control.value
    me = Text("", style=TextStyle(size=15))
    bots_view.controls.append(
        Column(
            controls=[
                Text(
                    "Topic:",
                    style=TextStyle(color=colors.BLUE_GREY_900,
                                    weight="bold", size=15)),
                me
            ]
        )
    )
    for character in text:
      me.value += character
      time.sleep(0.005)
      view_container.update()
    view_container.content.controls[1].update()
    conversation_history = [text]
    current_speaker = "GPT-4"  # Start with GPT-4
    for _ in range(4):
      if current_speaker == "GPT-4":
        bots_view.controls.append(
            Column(
                controls=[
                    Divider(height=10, color=colors.TRANSPARENT),
                    Row(
                        controls=[
                            Text(style=TextStyle(color=colors.BLUE_GREY_900,
                                                 weight="bold", size=15)),
                            Text(style=TextStyle(color=colors.GREEN, size=15)),
                            VerticalDivider(width=10)
                        ]
                    ),
                    Text("")
                ]
            )
        )
        response, justification, veracity, citations = chat_gpt_4(" ".join(conversation_history[-1]))
        typescript(response)
        bots_view.controls[-1].controls[1].controls.append(
            ElevatedButton(
                "grounding",
                on_click=lambda e, j=justification, v=veracity, c=citations: open_grounding_dialog(e, j, v, c),
                style=ButtonStyle(color=colors.BLUE_GREY_900, bgcolor=colors.WHITE, shape=RoundedRectangleBorder(radius=2))
            )
        )
        bots_view.controls[-1].controls[1].update()
        current_speaker = "Gemini"
      else:
        bots_view.controls.append(
            Column(
                controls=[
                    Divider(height=10, color=colors.TRANSPARENT),
                    Row(
                        controls=[
                            Text(style=TextStyle(color=colors.BLUE_GREY_900,
                                                 weight="bold", size=15)),
                            Text(style=TextStyle(color=colors.GREEN, size=15)),
                            VerticalDivider(width=10)
                        ]
                    ),
                    Text("")
                ]
            )
        )
        response, justification, veracity, citations = gemini(" ".join(conversation_history[-1]))
        typescript(response, chat_gpt=False)
        bots_view.controls[-1].controls[1].controls.append(
            ElevatedButton(
            "grounding",
            on_click=lambda e, j=justification, v=veracity, c=citations: open_grounding_dialog(e, j, v, c),
            style=ButtonStyle(color=colors.BLUE_GREY_900, bgcolor=colors.WHITE, shape=RoundedRectangleBorder(radius=2))
            )
        )
        bots_view.controls[-1].controls[1].update()
        print(f"{current_speaker}: {response}")
        current_speaker = "GPT-4"
      conversation_history.append(response)



  bots_view: ListView = ListView(
      expand=True,
      auto_scroll=True,
      controls=[response_text],
  )

  # Left Side Container with Summary
  view_container: Container = Container(
      border_radius=12,
      padding=12,
      margin=margin.only(left=20, top=12, bottom=12),
      # Use expand with a flex value for dynamic sizing
      expand=1,
      content=Column(
          controls=[
              Container(
                  alignment=alignment.center,
                  padding=Padding(left=12, right=12, top=0, bottom=0),
                  content=Row(
                      alignment=MainAxisAlignment.CENTER,
                      controls=[
                          Container(
                              bgcolor=colors.BLUE_GREY_100,
                              expand=1,
                              # width=250,
                              height=25,
                              padding=12,
                              border_radius=12,
                              content=None
                          ),
                          Text("VS",
                               style=TextStyle(color=colors.GREY, size=25)),
                          Container(
                              bgcolor=colors.BLUE_GREY_100,
                              expand=1,
                              # width=250,
                              height=25,
                              padding=12,
                              border_radius=12,
                              content=None
                          ),
                      ]
                  )
              ),
              bots_view,
              Divider(height=10, color=colors.TRANSPARENT),
          ]
      ),
  )

  user_input: TextField = TextField(
      border_color=colors.TRANSPARENT,
      hint_text="...",
      on_submit=chat_message,
  )

  # Right Side Container with Conversational Bot
  input: Container = Container(
      border_radius=12,
      padding=12,
      margin=margin.only(left=20, top=12, bottom=12),
      # Use expand with a flex value for dynamic sizing
      expand=1,
      content=Column(
          controls=[
              Text(
                  "Write anything to discuss:",
                  style=TextStyle(color=colors.GREY, size=25),
              ),
              Divider(height=10, color=colors.TRANSPARENT),
              user_input
          ],
          expand=True,
          spacing=0
      ),
  )

  divider: VerticalDivider = VerticalDivider(width=10)

  main_dash: Row = Row(
      alignment=MainAxisAlignment.SPACE_EVENLY,
      controls=[
          view_container,
          divider,
          input,
      ],
      # Ensure the Row expands to fill available space
      expand=True,
  )

  page.add(main_dash)


app(target=main)

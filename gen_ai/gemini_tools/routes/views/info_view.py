from flet import *
from typing import Union
from views.Router import Router, DataStrategyEnum
from State import global_state


def InfoView(page: Page, router: Union[Router, str, None] = None):
  if router and router.data_strategy == DataStrategyEnum.STATE:
    data = global_state.get_state_by_key("data").get_state()
  text = Text("State: " + str(data))

  title = Text(data["title"])
  description = Text(data["description"])
  price = Text(value="$8.00")
  materials = Text(value="Polyester")

  image_container = Container(
      content=None
  )

  #Left Panel Content
  left = Container(
      height=page.height * .80,
      width=page.width * .50,
      col={"sm": 6, "md": 6, "xl": 6},
      content=Column(
          scroll=ScrollMode.ALWAYS,
          controls=[
              image_container
          ]
      )
  )

  chat_text_input = Container(
      expand=True,
      content=TextField(
          hint_text="Looking for specific info? Ask Chatsy!",
          hint_style=TextStyle(size=14),
          multiline=True,
          min_lines=1,
          max_lines=10,
          shift_enter=True,
          #on_submit=execute
      )
  )

  chatbot_window = Container(
      padding=padding.only(left=15, right=15),
      width=page.width * .50,
      content=Row(
          vertical_alignment=CrossAxisAlignment.CENTER,
          controls=[
              Container(
                  height=30,
                  width=30,
                  content=Image(src="https://gcpetsy.sonrobots.net/artifacts/etsymate.png", fit=ImageFit.CONTAIN),
              ),
              chat_text_input,
              IconButton(
                  icon=icons.SEND,
                  icon_color=colors.DEEP_ORANGE_400,
                  # on_click=execute
              )
          ]
      )
  )

  response = Text()

  chatbot_response = Container(
      padding=15,
      border=border.all(1, color=colors.DEEP_ORANGE_400),
      border_radius=14,
      width=page.width * .50,
      content=Column(
          alignment=MainAxisAlignment.START,
          spacing=5,
          controls=[
              Text("Chatsy: ", style=TextStyle(color=colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)),
              response
          ]
      )
  )

  # Right Panel Content
  right = Container(
      height=page.height * .80,
      width=page.width * .50,
      col={"sm": 6, "md": 6, "xl": 6},
      padding=14.0,
      content=Column(
          scroll=ScrollMode.ALWAYS,
          alignment=MainAxisAlignment.START,
          spacing=20,
          controls=[
              title,
              price,
              description,
              chatbot_window,
              chatbot_response
          ]
      )
  )


  return ResponsiveRow(
      controls=[
          left,
          right
      ]
  )
import random
from flet import *
from typing import Union
from views.Router import Router, DataStrategyEnum
from State import global_state

items_available = random.randint(1,8)

def InfoView(page: Page, router: Union[Router, str, None] = None):
  if router and router.data_strategy == DataStrategyEnum.STATE:
    data = global_state.get_state_by_key("data").get_state()
  text = Text("State: " + str(data))

  title = Text(data["generated_titles"])
  description = Text(data["generated_descriptions"])
  public_cdn_link = data["public_cdn_link"]
  listing_id = data["listing_id"]
  price = Text(value="$8.00")
  materials = Text(value="Polyester")

  image_container = Container(
      content=Image(
          public_cdn_link,
          fit=ImageFit.CONTAIN
      ),
      on_click=lambda x: page.launch_url(listing_id)
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

  # Right Panel Content
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

  # Right Panel Content
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

  # Right Panel Content
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

  panel = ExpansionPanelList(
      expand_icon_color=colors.DEEP_ORANGE_400,
      elevation=0,
      divider_color=colors.DEEP_ORANGE_400,
      controls=[
          ExpansionPanel(
              header=ListTile(title=Text("Item Details", size=14)),
              content=Container(
                  content=Column(
                      alignment=MainAxisAlignment.CENTER,
                      horizontal_alignment=CrossAxisAlignment.CENTER,
                      controls=[Text(line.strip(), selectable=True) for line in data["description"].split('\\n')]
                  ),
              ),
          )
      ]
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
              Text(f"Low in stock, only {items_available} left", color=colors.DEEP_ORANGE_400, size=16, weight=FontWeight.BOLD),
              Text(f'$ {data["price_usd"]}', weight=FontWeight.BOLD, size=20),
              Text(data["generated_titles"], selectable=True, size=14),
              Text(data["title"], selectable=True, size=14),
              Text(
                  spans=[
                      TextSpan("Description: ", TextStyle(weight=FontWeight.BOLD)),
                      TextSpan(data["generated_descriptions"].strip())
                  ],
                  selectable=True,
              ),
              panel,
              # Text(
              #     spans=[
              #         TextSpan("Materials: ", TextStyle(weight=FontWeight.BOLD)),
              #         TextSpan(data["materials"].strip())
              #     ],
              #     selectable=True,
              # ),
              chatbot_window,
              chatbot_response
          ]
      )
  )

  def go_home(e):
    page.go("/")

  # Bottom App Bar
  bottom_app_footer = BottomAppBar(
      bgcolor=colors.TRANSPARENT,
      content=Row(
          alignment=MainAxisAlignment.START,
          controls=[
              IconButton(
                  icon=icons.ARROW_BACK_IOS_NEW,
                  icon_color=colors.DEEP_ORANGE_400,
                  on_click=lambda _: page.go("/")
              )
          ]
      )
  )

  page.appbar = bottom_app_footer
  page.update()

  return ResponsiveRow(
      controls=[
          left,
          right
      ]
  )
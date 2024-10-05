import json

from flet import *
from typing import Union
from State import global_state, State
from views.Router import Router, DataStrategyEnum

def SearchView(page: Page, router_data: Union[Router, str, None] = None):
  def send_data(e: ControlEvent):
    text_field = TextField()
    send_button = ElevatedButton("Send")
    send_button.on_click = send_data

  grid_view = GridView(
      max_extent=200,
      spacing=60,
      run_spacing=1,
  )

  grid_screen = Container(
      margin=margin.only(left=20),
      content=Column(
          [
              Column(
                  controls=[
                      grid_view
                  ],
                  scroll=ScrollMode.AUTO,
                  expand=True
              ),
          ],
          height=460,
      ),
  )

  matches_box = ResponsiveRow([grid_screen])

  def navigate_to_search_page(e):
    if e.control.data == "":
      return
    if router_data and router_data.data_strategy == DataStrategyEnum.QUERY:
      e.page.go("/info_widget", data=json.dumps(e.control.data))
    elif router_data and router_data.data_strategy == DataStrategyEnum.STATE:
      state = State("data", e.control.data)
      e.page.go("/info_widget")
    else:
      e.page.go("/info_widget")

  async def search(e):
    items = [
        {
            "title": "masamba",
            "description": "mambo"
        },
        {
            "title": "masamb2",
            "description": "mambo"
        },
        {
            "title": "masamb2",
            "description": "mambo"
        },
        {
            "title": "masamb2",
            "description": "mambo"
        },
    ]
    for item in items:
      grid_view.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Container(
                      content=Card(
                          elevation=20,
                          content=Container(
                              bgcolor=colors.GREY_500,
                              height=150,
                              width=150,
                              content=Text(item["title"]) # To Change
                          )
                      ),
                      data=item,
                      on_click=navigate_to_search_page
                  ),
                  Container(
                      padding=padding.all(10),
                      width=150,
                      content=Row(
                          alignment=MainAxisAlignment.SPACE_BETWEEN,
                          controls=[
                              Container(
                                  width=70,
                                  content=Text(item["title"], overflow=TextOverflow.ELLIPSIS)
                              ),
                              Container(
                                  content=Text("$12", size=12)
                              )
                          ]
                      )
                  )
              ]
          )
      )
    page.update()

  def shadow_hover(e):
    if e.data == "true":
      search_text_input_c.shadow: BoxShadow = BoxShadow(
          spread_radius=0.2,
          blur_radius=2,
          color=colors.BLUE_GREY_300,
          offset=Offset(0, 0),
          blur_style=ShadowBlurStyle.OUTER
      )
    else:
      search_text_input_c.shadow = None
    search_text_input_c.update()


  search_text_input_c: Container = Container(
      width=page.width * 0.50,
      padding=10,
      border=border.all(0.5, color=colors.GREY_400),
      border_radius=30,
      content=TextField(
          prefix_icon=icons.SEARCH,
          height=28,
          text_size=12,
          text_vertical_align=VerticalAlignment.START,
          content_padding=10,
          border_color=colors.TRANSPARENT,
          data=1,
          on_submit=search,
          #on_change=textbox_changed
      ),
      on_hover=shadow_hover
  )

  content = Container(
      # bgcolor=colors.RED,
      alignment=alignment.center,
      margin=margin.only(top=30),
      content=Column(
          controls=[
              search_text_input_c,
              Divider(height=50, color=colors.TRANSPARENT),
              matches_box
          ],
          horizontal_alignment=CrossAxisAlignment.CENTER
      )
  )


  return content
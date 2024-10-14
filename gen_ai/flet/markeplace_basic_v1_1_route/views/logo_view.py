from flet import *
from typing import Union
from views.Router import Router
from State import global_state, State
from views.Router import Router, DataStrategyEnum
from middleware.main import LocalEmbeddings, VaIS, listing_queries

vais = VaIS()

suggestion_list = sorted(listing_queries.to_list())[::len(listing_queries.to_list())//1000]

def LogoView(page: Page, router_data: Union[Router, str, None] = None):
  def set_input(e):
    print(word_text_input)
    df_retrieved = vais.search(word_text_input)
    state = State("retrieved_dataset", df_retrieved)
    state = State("text_input", word_text_input)
    e.page.go("/")

  # first
  def textbox_changed(string):
    global word_text_input
    word_text_input = string.control.value
    str_lower = word_text_input.lower()
    list_view.controls = [
        ListTile(
            title=Text(word, size=20, color= colors.DEEP_ORANGE_400),
            leading=Icon(icons.ARROW_FORWARD, color=colors.GREY_400),
            on_click=set_input,
            data=word,
        ) for word
        in suggestion_list if str_lower in word.lower()
    ] if str_lower else []
    page.update()

  list_view = ListView(expand=1, spacing=2, padding=10)

  def search(e):
    df_retrieved = vais.search(e.control.value)
    state = State("retrieved_dataset", df_retrieved)
    state = State("text_input", e.control.value)
    e.page.go("/")

  def shadow(e):
    if e.data == "true":
      input.shadow = BoxShadow(
          spread_radius=0.2,
          blur_radius=2,
          color=colors.BLUE_GREY_300,
          offset=Offset(0,0),
          blur_style=ShadowBlurStyle.OUTER
      )
    else:
      input.shadow = None
    input.update()

  bottom_app_footer = BottomAppBar(
      bgcolor=colors.TRANSPARENT,
      content=Row(
          alignment=MainAxisAlignment.END,
          controls=[
              Text("V1.1", size=18, color=colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)
          ]
      )
  )

  page.bottom_appbar = bottom_app_footer
  page.update()

  return Column(
      alignment=MainAxisAlignment.START,
      horizontal_alignment=CrossAxisAlignment.CENTER,
      controls=[
          Divider(height=50, color=colors.TRANSPARENT),
          Container(
              content=Image(
                  src="https://gcpetsy.sonrobots.net/artifacts/etsy.png",
                  fit=ImageFit.CONTAIN,
                  width=0.2,
                  aspect_ratio=8.23,
              )
          ),
          input:=Container(
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
                  on_change=textbox_changed
              ),
              on_hover=shadow
          ),
          Container(
              width=page.width * 0.50,
              height=page.height * 0.70,
              padding=10,
              content=list_view
          )
      ]
  )
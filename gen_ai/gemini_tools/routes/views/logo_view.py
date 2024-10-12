from flet import *
from typing import Union
from views.Router import Router
from State import global_state, State
from views.Router import Router, DataStrategyEnum
from middleware.main import LocalEmbeddings, VaIS

vais = VaIS()

def LogoView(page: Page, router_data: Union[Router, str, None] = None):
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
                  # on_change=textbox_changed
              ),
              on_hover=shadow
          )
      ]
  )
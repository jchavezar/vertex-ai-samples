from flet import *
from videos_listing import listing
from videos_analysis import video_llm
from back_end import vector_search_images

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("flet_core").setLevel(logging.INFO)

def main(page: Page):
  # heightscr = page.window.height
  # widthscr = page.window.width
  page.spacing = 0
  page.padding = 0
  print(page.window.height)
  print(page.window.height)
  print(page.window.height)

  def navigate_to_url(e):
    link = e.control.data
    page.session.link = link["uri"]
    page.session.start_off = link["start_sec"]
    page.session.end_off = link["end_sec"]
    page.go("/video")

  def navigate_to_list(e):
    page.go("/list")

  def search(e):
    videos_grid_view.controls.clear()
    re = vector_search_images(e.control.value)

    for k1, v1 in re.items():
      videos_grid_view.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Container(
                      content=Card(
                          elevation=20,
                          content=Image(
                              src=v1["thumbnails_uri"],
                              fit=ImageFit.COVER,
                              border_radius=border_radius.all(10),
                          )
                      ),
                      data={"uri": v1["uri"], "start_sec": v1["start_sec"], "end_sec": v1["end_sec"]},
                      on_click=navigate_to_url
                  ),
                  Text(v1["title"])
              ]
          ),
      )
    page.update()
    gridscreen.content.controls[0].color = colors.BLACK87
    gridscreen.update()

  search_field: Row = Row(
      controls=[
          Icon(icons.SEARCH),
          TextField(
              label="Hi!",
              border_color=colors.TRANSPARENT,
              on_submit=search
          )
      ]
  )

  search_bar: Container = Container(
      margin=margin.only(top=10, left=100, right=100),
      alignment=alignment.center,
      border=border.all(1, colors.GREY),
      border_radius=16,
      padding=10,
      content=search_field
  )

  videos_grid_view: GridView = GridView(
      # expand=True,
      runs_count=5,
      max_extent=150,
      child_aspect_ratio=1,
      spacing=15,
      run_spacing=15,
  )

  gridscreen = Container(
      margin=margin.only(left=20),
      content=Column(
          [
              Text("Result:", weight="bold", size=30, color=colors.TRANSPARENT),
              Column( # Use a Column with scroll="auto"
                  controls=[videos_grid_view],
                  scroll="auto", # Enable vertical scrolling
                  expand=True     # Allow the column to expand to fill available space
              )
          ],
          height= 350,
          expand=True,
          #scroll="auto"
      )
  )

  search_results_panel: Container = Container(
      border=border.all(1, colors.BLUE),
      alignment=alignment.center,
      content=gridscreen
  )

  button_panel: Container = Container(
      height=50,
      margin=margin.only(right=20),
      alignment=alignment.center_right,
      content=ElevatedButton(
          "videos",
          icon=icons.VIDEOCAM_SHARP ,
          on_click=navigate_to_list,
          opacity=0.8,
          style=ButtonStyle(shape=RoundedRectangleBorder(radius=2))
      ),
  )

  main_layout: ResponsiveRow = ResponsiveRow([
      Container(
          # width=widthscr,
          # height=heightscr,
          content=Column(
              controls=[
                search_bar,
                button_panel,
                gridscreen,
                Container(content=None, bgcolor=colors.TRANSPARENT, height=20)
              ]
          )
      )
  ])

  def route_change(route):
    # page.window.center()
    # page.window.height = 900
    # page.window.width = 1126
    page.update()
    page.views.clear()
    page.views.append(
        View(
            "/",
            [main_layout]
        )
    )
    if page.route == "/video":
      sample_media = [
          VideoMedia(page.session.link),
      ]
      page.views.append(
          View(
              "/video",
              [
                  AppBar(title=Text("Store"), bgcolor=colors.SURFACE_VARIANT),
                  Text(page.session.link),
                  video_llm(page=page, sample_media=sample_media),
              ],
          )
      )
    elif page.route == "/list":
      page.views.append(
          View(
              "/list",
              [
                  AppBar(title=Text("Back"), bgcolor=colors.SURFACE_VARIANT),
                  listing
              ]
          )
      )
    page.update()

  def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  page.go(page.route)

app(target=main, view=AppView.WEB_BROWSER, )
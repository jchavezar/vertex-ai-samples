import time

from flet import *
import second_page
from middleware import list_items, parallel_vector_search

def view(page):
  def navigate_to_second_page(e):
    page.go("/second")

  def navigate_to_search_page(e):
    link = e.control.data
    page.session.link = link["uri"]
    page.go("/search_results")

  async def search(e):
    grid_view.controls.clear()
    # items = vector_search(e.control.value)
    items = parallel_vector_search(e.control.value)
    start_time = time.time()
    # items = await page.asyncio_call(vector_search_wrapper, e.control.value, e.control.value)
    print(time.time() - start_time)
    for item in items:
      # print(item["uri"])
      grid_view.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Container(
                      content=Card(
                          elevation=20,
                          content=Container(
                              height=120,
                              width=120,
                              content=Image(
                                  src=item["uri"],
                                  fit=ImageFit.COVER,
                              )
                          )
                      )
                  ),
                  Text(item["title"])
              ]
          )
      )
    page.update()

  def add_stuff(e):
    grid_view.controls.clear()
    gridscreen.height = "",
    gridscreen.expand = True,
    items = list_items()
    for item in items:
      print(item["uri"])
      grid_view.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Container(
                      content=Card(
                          elevation=20,
                          content=Container(
                              height=120,
                              width=120,
                              content=Image(
                                  src=item["uri"],
                                  fit=ImageFit.COVER,
                              )
                          )
                      )
                  ),
                  Text(item["title"])
              ]
          )
      )
    page.update()

  grid_view: GridView = GridView(
      # expand=True,
      runs_count=5,
      max_extent=200,
      # child_aspect_ratio=1,
      spacing=15,
      run_spacing=15,
  )

  gridscreen = Container(
      margin=margin.only(left=20),
      content=Column(
          [
              Text("Result:", weight="bold", size=30, color=colors.TRANSPARENT),
              Column(
                  controls=[grid_view],
                  scroll="auto",
                  expand=True
              )
          ],
          height= 450,
          # expand=True,
      )
  )

  main_layout: ResponsiveRow = ResponsiveRow(
      [
          gridscreen
      ]
  )

  return View(
      "/",
      [
          Column(
              # alignment=MainAxisAlignment.CENTER,
              controls=[
                  Divider(height=20, color=colors.TRANSPARENT),
                  Container(
                      height=50,
                      padding=padding.only(left=15, right=15),
                      margin=margin.only(left=150, right=150),
                      border_radius=30,
                      border=border.all(2, colors.BLACK),
                      bgcolor=colors.WHITE,
                      content=Row(
                          controls=[
                              TextField(
                                  hint_text="Search for anything",
                                  hint_style=TextStyle(color=colors.GREY_500, font_family="Helvetica", weight=FontWeight.W_200),
                                  expand=True,
                                  border_color=colors.TRANSPARENT,
                                  data={"uri": "test"},
                                  on_submit=search
                              ),
                              Icon(
                                  name=icons.SEARCH,
                                  color=colors.ORANGE,
                                  size=25,
                              ),
                          ]
                      )
                  ),
                  # Container(
                  #     bgcolor=colors.GREEN_50,
                  #     height=300,
                  #     content=main_layout
                  # ),
                  main_layout,
                  ElevatedButton(
                      on_click=add_stuff
                  ),
                  ElevatedButton(
                      "Go to Second Page",
                      on_click=navigate_to_second_page,
                      bgcolor=colors.BLUE,
                      color=colors.WHITE,
                  )
              ]
          )
      ]
  )
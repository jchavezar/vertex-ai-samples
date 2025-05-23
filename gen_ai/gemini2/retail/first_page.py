# first_page.py

import time
from flet import *
import second_page
from middleware import vector_search


def view(page):
  page.bgcolor = colors.TRANSPARENT
  page.update()

  def navigate_to_second_page(e):
    page.go("/second")

  # def navigate_to_search_page(e):
  #   link = e.control.data
  #   page.session.link = link["uri"]
  #   page.session.private_uri = link["private_uri"]
  #   page.session.title = link["title"]
  #   page.session.price = link["price"]
  #   page.session.subtitle = link["subtitle"]
  #   page.session.summary = link["summary"]
  #   page.session.description = link["description"]
  #   page.session.materials = link["materials"]
  #   page.session.questions = link["questions"]
  #   page.session.content = link["content"]
  #   page.go("/search_results")

  async def search(e):
    grid_view.controls.clear()
    items = vector_search(e.control.value)
    print(items)
    #items = parallel_vector_search(e.control.value)
    # items = await page.asyncio_call(vector_search_wrapper, e.control.value, e.control.value)

    # Store search results in page session
    # page.session.search_results = items

    for index, item in items.iterrows():
      grid_view.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Container(
                      content=Card(
                          elevation=20,
                          content=Container(
                              height=150,
                              width=150,
                              content=Image(
                                  src=item["image_public_uri"],
                                  fit=ImageFit.COVER,
                              ),
                          ),
                      ),
                      # data={
                      #     "uri": item["uri"],
                      #     "private_uri": item["private_uri"],
                      #     "title": item["title"],
                      #     "price": item["price"],
                      #     "subtitle": item["subtitle"],
                      #     "summary": item["summary"],
                      #     "description": item["description"],
                      #     "materials": item["materials"],
                      #     "questions": item["questions"],
                      #     "content": item["content"],
                      # },
                      # on_click=navigate_to_search_page,
                  ),
                  Container(
                      padding=padding.all(10),
                      border=border.all(1, colors.BLACK),
                      width=150,
                      content=Row(
                          alignment=MainAxisAlignment.SPACE_BETWEEN,
                          controls=[
                              Container(
                                  bgcolor=colors.YELLOW_50,
                                  width=70,
                                  content=Text(item["ProductName"], overflow=TextOverflow.ELLIPSIS),
                              ),
                              Container(
                                  content=Text(f"$ {item['Price (INR)']}", size=12)
                              )
                          ]
                      ),
                  )
                  # Text(item["title"]),
              ],
          )
      )
    page.update()

  # def listitems(e):
  #   grid_view.controls.clear()
  #   gridscreen.height = ""
  #   gridscreen.expand = True
  #   # items = list_items()
  #
  #   # Store list items results in page session
  #   page.session.search_results = items
  #
  #   for item in items:
  #     grid_view.controls.append(
  #         Column(
  #             alignment=MainAxisAlignment.CENTER,
  #             controls=[
  #                 Container(
  #                     content=Card(
  #                         elevation=20,
  #                         content=Container(
  #                             height=150,
  #                             width=150,
  #                             content=Image(
  #                                 src=item["uri"],
  #                                 fit=ImageFit.COVER,
  #                             ),
  #                         ),
  #                     ),
  #                     data={
  #                         "uri": item["uri"],
  #                         "title": item["title"],
  #                         "price": item["price"],
  #                         "subtitle": item["subtitle"],
  #                         "summary": item["summary"],
  #                         "description": item["description"],
  #                         "materials": item["materials"],
  #                         "questions": item["questions"],
  #                         "content": item["content"],
  #                     },
  #                     on_click=navigate_to_search_page,
  #                 ),
  #                 Text(item["title"]),
  #             ],
  #         )
  #     )
  #   page.update()

  grid_view: GridView = GridView(
      # expand=True,
      # runs_count=5,
      max_extent=200,
      # child_aspect_ratio=1,
      spacing=60,
      run_spacing=1,
  )

  gridscreen = Container(
      margin=margin.only(left=20),
      content=Column(
          [
              # Text(
              #     "Result:", weight="bold", size=30, color=colors.BLUE
              # ),
              Column(controls=[grid_view], scroll="auto", expand=True),
          ],
          height=460,
          # expand=True,
      ),
  )

  main_layout: ResponsiveRow = ResponsiveRow([gridscreen])

  # Check for stored search results
  # if hasattr(page.session, "search_results"):
  #   items = page.session.search_results
  #   for item in items:
  #     grid_view.controls.append(
  #         Column(
  #             alignment=MainAxisAlignment.CENTER,
  #             controls=[
  #                 Container(
  #                     content=Card(
  #                         elevation=20,
  #                         content=Container(
  #                             height=150,
  #                             width=150,
  #                             content=Image(
  #                                 src=item["uri"],
  #                                 fit=ImageFit.COVER,
  #                             ),
  #                         ),
  #                     ),
  #                     data={
  #                         "uri": item["uri"],
  #                         "private_uri": item.get("private_uri", ""),  # Handle potential missing key
  #                         "title": item["title"],
  #                         "price": item["price"],
  #                         "subtitle": item["subtitle"],
  #                         "summary": item["summary"],
  #                         "description": item["description"],
  #                         "materials": item["materials"],
  #                         "questions": item["questions"],
  #                         "content": item["content"],
  #                     },
  #                     # on_click=navigate_to_search_page,
  #                 ),
  #                 Container(
  #                     padding=padding.all(10),
  #                     width=150,
  #                     content=Row(
  #                         alignment=MainAxisAlignment.SPACE_BETWEEN,
  #                         controls=[
  #                             Container(
  #                                 width=70,
  #                                 content=Text(item["title"], overflow=TextOverflow.ELLIPSIS),
  #                             ),
  #                             Container(
  #                                 content=Text(f"$ {item['price']}", size=12)
  #                             )
  #                         ]
  #                     ),
  #                 )
  #             ],
  #         )
  #     )
  #   page.update()

  return View(
      "/",
      [
          Column(
              # alignment=MainAxisAlignment.CENTER,
              controls=[
                  Divider(height=10, color=colors.TRANSPARENT),
                  Row(
                      alignment=MainAxisAlignment.SPACE_EVENLY,
                      controls=[
                          Container(
                              margin=margin.only(left=50),
                              height=75,
                              width=75,
                              content=Image(
                                  src="https://gcpetsy.sonrobots.net/artifacts/etsy.png",
                                  fit=ImageFit.CONTAIN,
                              ),
                          ),
                          Container(
                              height=40,
                              expand=True,
                              padding=padding.only(left=5, right=5),
                              margin=margin.only(left=15, right=75),
                              border_radius=30,
                              border=border.all(2, colors.BLACK),
                              bgcolor=colors.WHITE,
                              content=Row(
                                  alignment=MainAxisAlignment.SPACE_BETWEEN,
                                  controls=[
                                      TextField(
                                          hint_text="Search for anything",
                                          hint_style=TextStyle(
                                              color=colors.GREY_500,
                                              font_family="Helvetica",
                                              weight=FontWeight.W_200,
                                              size=14,
                                          ),
                                          # expand=True,
                                          border_color=colors.TRANSPARENT,
                                          data={"uri": "test"},
                                          on_submit=search,
                                      ),
                                      Icon(
                                          name=icons.SEARCH,
                                          color=colors.DEEP_ORANGE_400,
                                          size=25,
                                      ),
                                  ],
                              ),
                          ),
                      ],
                  ),
                  main_layout,
              ],
          ),
          BottomAppBar(
              bgcolor=colors.TRANSPARENT,
              content=Row(
                  controls=[
                      IconButton(
                          icon=icons.PHOTO_LIBRARY,
                          # on_click=listitems,
                          icon_color=colors.DEEP_ORANGE_400,
                      ),
                      IconButton(
                          icon=icons.ARCHITECTURE,
                          on_click=navigate_to_second_page,
                          icon_color=colors.DEEP_ORANGE_400,
                      ),
                  ],
              ),
          ),
      ],
  )
from flet import *
from middleware import list_items, parallel_vector_search

def view(page):
  def page_resize(e):
    input.width = page.width * 0.50
    page.update()
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

  def navigate_to_second_page(e):
    page.go("/second")

  def navigate_to_third_page(e):
    page.go("/third")

  def navigate_to_search_page(e):
    link = e.control.data
    page.session.link = link["uri"]
    page.session.private_uri = link["private_uri"]
    page.session.title = link["title"]
    page.session.price = link["price"]
    page.session.subtitle = link["subtitle"]
    page.session.summary = link["summary"]
    page.session.description = link["description"]
    page.session.materials = link["materials"]
    #page.session.questions = link["questions"]
    page.session.content = link["content"]
    page.session.questions_cat1 = link["questions_cat1"]
    page.session.answers_cat1 = link["answers_cat1"]
    page.session.questions_cat2 = link["questions_cat2"]
    page.session.answers_cat2 = link["answers_cat2"]
    page.session.textual_questions = link["textual_questions"]
    page.session.textual_answers = link["textual_answers"]
    page.session.visual_questions = link["visual_questions"]
    page.session.visual_answers = link["visual_answers"]
    page.session.textual_tile = link["textual_tile"]
    page.session.textual_image_uri = link["textual_image_uri"]
    page.session.visual_tile = link["visual_tile"]
    page.session.visual_image_uri = link["visual_image_uri"]
    page.go("/search_results")

  async def search(e):
    if e.control.data == 1:
      print("working?")
      mp.controls[0] = second_main
      footer.visible = True
      input_field.value = e.control.value
      page.session.query = input_field.value
      page.update()
    else:
      grid_view.controls.clear()
    items = parallel_vector_search(e.control.value)

    # Store search results in page session
    page.session.search_results = items

    for item in items:
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
                                  src=item["uri"],
                                  fit=ImageFit.COVER,
                              ),
                          ),
                      ),
                      data={
                          "uri": item["uri"],
                          "private_uri": item["private_uri"],
                          "title": item["title"],
                          "price": item["price"],
                          "subtitle": item["subtitle"],
                          "summary": item["summary"],
                          "description": item["description"],
                          "materials": item["materials"],
                          #"questions": item["questions"],
                          "content": item["content"],
                          "questions_cat1": item["questions_cat1"],
                          "answers_cat1": item["answers_cat1"],
                          "questions_cat2": item["questions_cat2"],
                          "answers_cat2": item["answers_cat2"],
                          "textual_questions": item["textual_questions"],
                          "textual_answers": item["textual_answers"],
                          "visual_questions": item["visual_questions"],
                          "visual_answers": item["visual_answers"],
                          "textual_tile": item["textual_tile"],
                          "textual_image_uri": item["textual_image_uri"],
                          "visual_tile": item["visual_tile"],
                          "visual_image_uri": item["visual_image_uri"],
                      },
                      on_click=navigate_to_search_page,
                  ),
                  Container(
                      padding=padding.all(10),
                      width=150,
                      content=Row(
                          alignment=MainAxisAlignment.SPACE_BETWEEN,
                          controls=[
                              Container(
                                  width=70,
                                  content=Text(item["title"], overflow=TextOverflow.ELLIPSIS),
                              ),
                              Container(
                                  content=Text(f"$ {item['price']}", size=12)
                              )
                          ]
                      ),
                  )
              ],
          )
      )
    page.update()

  def listitems(e):
    grid_view.controls.clear()
    # gridscreen.height = ""
    # gridscreen.expand = True
    items = list_items()

    # Store list items results in page session
    page.session.search_results = items

    for item in items:
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
                                  src=item["uri"],
                                  fit=ImageFit.COVER,
                              ),
                          ),
                      ),
                      data={
                          "uri": item["uri"],
                          "title": item["title"],
                          "price": item["price"],
                          "subtitle": item["subtitle"],
                          "summary": item["summary"],
                          "description": item["description"],
                          "materials": item["materials"],
                          #"questions": item["questions"],
                          "content": item["content"],
                      },
                      # on_click=navigate_to_search_page,
                  ),
                  Text(item["title"]),
              ],
          )
      )
    page.update()

  #second
  grid_view: GridView = GridView(
      max_extent=200,
      spacing=60,
      run_spacing=1,
  )

  def go(e):
    mp.controls[0]=second_main
    input_field.value = e.control.value
    search(e.control.value)
    page.update()

  # first
  main_layout: Column = Column(
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
          input := Container(
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
                  on_submit=search
              ),
              on_hover=shadow
          ),
      ]
  )

  #second
  gridscreen = Container(
      margin=margin.only(left=20),
      content=Column(
          [
              Column(controls=[grid_view], scroll="auto", expand=True),
          ],
          height=460,
      ),
  )

  #second
  second_main_layout: ResponsiveRow = ResponsiveRow([gridscreen])

  #second
  input_field = TextField(
      prefix_icon=icons.SEARCH,
      height=28,
      text_size=12,
      text_vertical_align=VerticalAlignment.START,
      content_padding=10,
      border_color=colors.TRANSPARENT,
      data={"uri": "test"},
      on_submit=search
  )

  #second
  input_container = Container(
      width=page.width * 0.70,
      padding=10,
      border=border.all(0.5, color=colors.GREY_400),
      border_radius=30,
      content=input_field
  )

  #second
  second_main: Column = Column(
      controls=[
          Divider(height=10, color=colors.TRANSPARENT),
          Row(
              spacing=10,
              alignment=MainAxisAlignment.SPACE_BETWEEN,
              controls=[
                  Container(
                      margin=margin.only(left=70),
                      height=75,
                      width=75,
                      content=Image(
                          src="https://gcpetsy.sonrobots.net/artifacts/etsy.png",
                          fit=ImageFit.CONTAIN,
                      ),
                  ),
                  input_container,
                  VerticalDivider(width=75, color=colors.TRANSPARENT),
              ],
          ),
          second_main_layout,
      ],
  )

  mp: View = View(
      "/",
      controls=[
          main_layout,
          footer := BottomAppBar(
              visible=False,
              bgcolor=colors.TRANSPARENT,
              content=Row(
                  controls=[
                      IconButton(
                          icon=icons.PHOTO_LIBRARY,
                          on_click=listitems,
                          icon_color=colors.DEEP_ORANGE_400,
                      ),
                      IconButton(
                          icon=icons.ARCHITECTURE,
                          on_click=navigate_to_second_page,
                          icon_color=colors.DEEP_ORANGE_400,
                          tooltip="Search Engine Processing"
                      ),
                      IconButton(
                          icon=icons.CATEGORY,
                          on_click=navigate_to_third_page,
                          icon_color=colors.DEEP_ORANGE_400,
                          tooltip="Category 3 Processing"
                      ),
                  ],
              ),
          ),
      ]
  )

  if hasattr(page.session, "search_results"):
    mp.controls[0] = second_main
    footer.visible = True
    input_field.value = page.session.query
    items = page.session.search_results
    for item in items:
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
                                  src=item["uri"],
                                  fit=ImageFit.COVER,
                              ),
                          ),
                      ),
                      data={
                          "uri": item["uri"],
                          "private_uri": item.get("private_uri", ""),  # Handle potential missing key
                          "title": item["title"],
                          "price": item["price"],
                          "subtitle": item["subtitle"],
                          "summary": item["summary"],
                          "description": item["description"],
                          "materials": item["materials"],
                          #"questions": item["questions"],
                          "content": item["content"],
                          "questions_cat1": item["questions_cat1"],
                          "answers_cat1": item["answers_cat1"],
                          "questions_cat2": item["questions_cat1"],
                          "answers_cat2": item["answers_cat2"],
                          "textual_questions": item["textual_questions"],
                          "textual_answers": item["textual_answers"],
                          "visual_questions": item["visual_questions"],
                          "visual_answers": item["visual_answers"],
                          "textual_tile": item["textual_tile"],
                          "textual_image_uri": item["textual_image_uri"],
                          "visual_tile": item["visual_tile"],
                          "visual_image_uri": item["visual_image_uri"]
                      },
                      on_click=navigate_to_search_page,
                  ),
                  Container(
                      padding=padding.all(10),
                      width=150,
                      content=Row(
                          alignment=MainAxisAlignment.SPACE_BETWEEN,
                          controls=[
                              Container(
                                  width=70,
                                  content=Text(item["title"], overflow=TextOverflow.ELLIPSIS),
                              ),
                              Container(
                                  content=Text(f"$ {item['price']}", size=12)
                              )
                          ]
                      ),
                  )
              ],
          )
      )
    page.update()

  return mp
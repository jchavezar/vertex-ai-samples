import json
import random
from flet import *
from middleware import gemini_chat



def view(page):
  page.bgcolor=colors.WHITE
  page.update()
  questions = json.loads(page.session.questions)["questions_category_1"]


  items_available = random.randint(1,8)
  dollars = random.randint(0,99)
  cents = random.randint(0,99)
  price = f"${dollars:02d}.{cents:02d}"

  def etsymate(e):
    re = gemini_chat(user_query=e.control.value, context=str(page.session.content), image_uri=page.session.private_uri, questions=questions)
    conv.controls.clear()
    question.text = text_input.value
    answer.text = re["answer"]
    text_input.value=""
    text_input.focus()
    if len(re["questions_to_ask"]) != 0:
      conv.controls = (
          [
              ElevatedButton(
                  text=label,
                  color="black",
                  bgcolor="#E3F2FD",
                  style=ButtonStyle(
                      shape=RoundedRectangleBorder(radius=25),
                      padding=15,
                  ),
                  data=label,
                  on_click=button_etsymate,
              )
              for label in re["questions_to_ask"]["category_1"][:2]
          ]
          +
          [
          ElevatedButton(
              text=label,
              color="black",
              bgcolor=colors.RED_100,
              style=ButtonStyle(
                  shape=RoundedRectangleBorder(radius=25),
                  padding=15,
              ),
              data=label,
              on_click=button_etsymate,
          )
          for label in re["questions_to_ask"]["category_2"][:2]
      ]
          +[Divider(height=20, color=colors.TRANSPARENT)])
      log.value=f"Category Detected: {re['category_picked']}"
      image_panel.update()
      text_input.value=""
      text_input.focus()
      llm_response.visible = True
      llm_response.update()
      conv.update()

  def button_etsymate(e):
    text_input.value = e.control.data
    text_input.update()

  def send_message(e):
    re=gemini_chat(user_query=text_input.value, context=str(page.session.content), image_uri=page.session.private_uri, questions=questions)
    print(re)
    conv.controls.clear()
    question.text = text_input.value
    answer.text = re["answer"]
    text_input.value=""
    text_input.focus()
    llm_response.visible = True
    llm_response.update()
    print(re)
    if len(re["questions_to_ask"]) != 0:
      print("it worked")
      conv.controls = (
          [
              ElevatedButton(
                  text=label,
                  color="black",
                  bgcolor="#E3F2FD",
                  style=ButtonStyle(
                      shape=RoundedRectangleBorder(radius=25),
                      padding=15,
                  ),
                data=label,
                on_click=button_etsymate,
              )
              for label in re["questions_to_ask"]["category_1"][:2]
          ]
          +
          [
              ElevatedButton(
                  text=label,
                  color="black",
                  bgcolor=colors.RED_100,
                  style=ButtonStyle(
                      shape=RoundedRectangleBorder(radius=25),
                      padding=15,
                  ),
                  data=label,
                  on_click=button_etsymate,
              )
              for label in re["questions_to_ask"]["category_2"][:2]
          ]
          +[Divider(height=20, color=colors.TRANSPARENT)])
      log.value=f"Category Detected: {re['category_picked']}"
      image_panel.update()
      text_input.value=""
      text_input.focus()
      conv.update()

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
                    controls=[Text(line.strip(), selectable=True) for line in page.session.description.split('\\n')]
                ),
              ),
          )
      ]
  )

  log: Text = Text()

  return View(
      "/search_results",
      [
          Column(
              expand=True,
              scroll="auto",
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  ResponsiveRow(
                      controls=[
                          image_panel:=Container(
                              margin=margin.only(left=30, right=15, top=30),
                              #expand=6,
                              border_radius=12,
                              col={"sm": 6, "md": 6, "xl": 6},
                              content=Column(
                                  controls=[
                                      Image(
                                          src=page.session.link,
                                          fit=ImageFit.CONTAIN,
                                      ),
                                      Container(
                                          content=log
                                      )
                                  ]
                              )
                          ),
                          text_panel:=Container(
                              expand=True,
                              margin=margin.only(right=30, top=30),
                              padding=15,
                              # expand=6,
                              col={"sm": 6, "md": 6, "xl": 6},
                              #border=border.all(1,colors.GREY_400),
                              border_radius=12,
                              content=Column(
                                  alignment=MainAxisAlignment.CENTER,
                                  # horizontal_alignment=CrossAxisAlignment.CENTER,
                                  expand=True,
                                  #scroll="auto",
                                  spacing=10,
                                  controls=[
                                      Text(f"Low in stock, only {items_available} left", color=colors.DEEP_ORANGE_400, size=16, weight=FontWeight.BOLD),
                                      Text(price, weight=FontWeight.BOLD, size=20),
                                      Text(page.session.title.strip(), selectable=True, size=14),
                                      Text(page.session.subtitle.strip(), selectable=True, size=14),
                                      Text(
                                          spans=[
                                              TextSpan("Description: ", TextStyle(weight=FontWeight.BOLD)),
                                              TextSpan(page.session.summary.strip())
                                          ],
                                          selectable=True,
                                      ),
                                      Text(
                                          spans=[
                                              TextSpan("Materials: ", TextStyle(weight=FontWeight.BOLD)),
                                              TextSpan(page.session.materials.strip())
                                          ],
                                          selectable=True,
                                      ),
                                      panel,
                                      Divider(height=4, color=colors.TRANSPARENT),
                                      Container(
                                          padding=padding.only(left=15, right=15),
                                          content=Row(
                                              vertical_alignment=CrossAxisAlignment.CENTER,
                                              controls=[
                                                  Container(
                                                      height=30,
                                                      width=30,
                                                      content=Image(src="https://gcpetsy.sonrobots.net/artifacts/etsymate.png", fit=ImageFit.CONTAIN),
                                                  ),
                                                  # Container(
                                                  #     padding=5,
                                                  #     height=50,
                                                  #     expand=True,
                                                  #     border_radius=14,
                                                  #     border=border.all(1, colors.GREY),
                                                  #     content=Row(
                                                  #         controls=[
                                                  #             text_input:=TextField(
                                                  #                 hint_text="Looking for specific info? Ask EtsyMate!",
                                                  #                 hint_style=TextStyle(size=14),
                                                  #                 expand=True,
                                                  #                 border_color=colors.TRANSPARENT,
                                                  #                 on_submit=etsymate
                                                  #             ),
                                                  #             IconButton(icon=icons.SEND, icon_color=colors.DEEP_ORANGE_400, on_click=send_message), # Modify
                                                  #         ]
                                                  #     )
                                                  # ),
                                                  text_input:=TextField(
                                                      hint_text="Looking for specific info? Ask Chatsy!",
                                                      hint_style=TextStyle(size=14),
                                                      multiline=True,
                                                      min_lines=1,
                                                      max_lines=10,
                                                      expand=True,
                                                      on_submit=etsymate,
                                                      shift_enter=True,
                                                  ),
                                                  IconButton(icon=icons.SEND, icon_color=colors.DEEP_ORANGE_400, on_click=send_message)
                                              ]
                                          )
                                      ),
                                      llm_response:=Container(
                                          visible=False,
                                          padding=14,
                                          border_radius=14,
                                          border=border.all(1, colors.DEEP_ORANGE_400),
                                          content=Column(
                                              alignment=MainAxisAlignment.START,
                                              spacing=8,
                                              controls=[
                                                  Text(
                                                      spans=[
                                                          TextSpan("Your Question: ", style=TextStyle(color=colors.GREY_800, weight=FontWeight.BOLD)),
                                                          question:=TextSpan(),
                                                      ]
                                                  ),
                                                  Text(
                                                      spans=[
                                                          TextSpan("Chatsy:  ", style=TextStyle(color=colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)),
                                                          answer:=TextSpan(),
                                                      ]
                                                  ),
                                              ]
                                          )
                                      ),
                                      conv:=Row(
                                          wrap=True,
                                          scroll="auto",
                                          controls=[
                                              ElevatedButton(
                                                  text=label,
                                                  color="black",
                                                  bgcolor="#E3F2FD",
                                                  style=ButtonStyle(
                                                      shape=RoundedRectangleBorder(radius=25),
                                                      padding=15,
                                                  ),
                                                  data=label,
                                                  on_click=button_etsymate,
                                              )
                                              for label in questions
                                          ]+[Divider(height=20, color=colors.TRANSPARENT)]
                                      ),
                                  ]
                              )
                          ),
                      ]
                  ),
              ]
          ),
          ElevatedButton("Back", color=colors.DEEP_ORANGE_400, on_click=lambda _: page.go("/"))
      ]
  )



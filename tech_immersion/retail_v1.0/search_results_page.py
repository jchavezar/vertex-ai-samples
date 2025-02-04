import json
import random
from flet import *
from middleware import chat_message



def view(page):
  page.bgcolor=Colors.WHITE
  page.update()
  # questions = json.loads(page.session.questions)
  # print(questions)


  items_available = random.randint(1,8)
  dollars = random.randint(0,99)
  cents = random.randint(0,99)
  price = f"${dollars:02d}.{cents:02d}"

  # def etsymate(e):
  #   #re = gemini_chat(user_query=e.control.value, context=str(page.session.content), image_uri=page.session.private_uri, questions=str(questions))
  #   conv.controls.clear()
  #   question.text = text_input.value
  #   answer.text = re["answer"]
  #   text_input.value=""
  #   text_input.focus()
  #   if len(re["questions_to_ask"]) != 0:
  #     conv.controls = (
  #         [
  #             ElevatedButton(
  #                 text=label,
  #                 color="black",
  #                 bgcolor="#E3F2FD",
  #                 style=ButtonStyle(
  #                     shape=RoundedRectangleBorder(radius=25),
  #                     padding=15,
  #                 ),
  #                 data=label,
  #                 on_click=button_etsymate,
  #             )
  #             for label in re["questions_to_ask"]["category_1"][:2]
  #         ]
  #         +
  #         [
  #         ElevatedButton(
  #             text=label,
  #             color="black",
  #             bgcolor=Colors.RED_100,
  #             style=ButtonStyle(
  #                 shape=RoundedRectangleBorder(radius=25),
  #                 padding=15,
  #             ),
  #             data=label,
  #             on_click=button_etsymate,
  #         )
  #         for label in re["questions_to_ask"]["category_2"][:2]
  #         ]
  #         +
  #         [
  #             ElevatedButton(
  #                 text=label,
  #                 color="black",
  #                 bgcolor=Colors.YELLOW_50,
  #                 style=ButtonStyle(
  #                     shape=RoundedRectangleBorder(radius=25),
  #                     padding=15,
  #                 ),
  #                 data=label,
  #                 on_click=button_etsymate,
  #             )
  #             for label in re["questions_to_ask"]["category_3"][:2]
  #         ]
  #         +[Divider(height=20, color=Colors.TRANSPARENT)])
  #     log.value=f"Category Detected: {re['category_picked']}"
  #     image_panel.update()
  #     text_input.value=""
  #     text_input.focus()
  #     llm_response.visible = True
  #     llm_response.update()
  #     conv.update()

  def button_etsymate(e):
    print(e.control)
    text_input.value = e.control.data
    text_input.update()

  def send_message(e):
    print(e.control.data)
    if e.control.data["type"] == "text_field":
      input_data = e.control.value
    elif e.control.data["type"] == "button":
      input_data = text_input.value
    else:
      input_data = e.control.data["value"]
    # re=gemini_chat(user_query=text_input.value, context=str(page.session.content), image_uri=page.session.private_uri, questions=str(questions))
    re = chat_message(text=input_data, context=page.session.description)
    # conv.controls.clear()
    question.text = text_input.value
    answer.text = re["answer"]
    text_input.value=""
    text_input.focus()
    llm_response.visible = True
    llm_response.update()
    print(re)
    conv.controls = [
        ElevatedButton(
            text=q,
            color="black",
            bgcolor=color,
            style=ButtonStyle(
                shape=RoundedRectangleBorder(radius=25),
                padding=15,
            ),
            data={"type": "q_button", "value": q},
            on_click=send_message
        )
        for q, color in zip(
            re["questions_cat_1"] + re["questions_cat_2"] + re["questions_cat_3"],
            ["#E3F2FD"] * len(re["questions_cat_1"]) + ["#EEEEEE"] * len(re["questions_cat_2"]) + ["#EEBEBE"] * len(re["questions_cat_3"])
        )
    ]
    page.update()
    # if len(re["questions_to_ask"]) != 0:
    #   conv.controls = (
    #       [
    #           ElevatedButton(
    #               text=label,
    #               color="black",
    #               bgcolor="#E3F2FD",
    #               style=ButtonStyle(
    #                   shape=RoundedRectangleBorder(radius=25),
    #                   padding=15,
    #               ),
    #             data=label,
    #             on_click=button_etsymate,
    #           )
    #           for label in re["questions_to_ask"]["category_1"][:2]
    #       ]
    #       +
    #       [
    #           ElevatedButton(
    #               text=label,
    #               color="black",
    #               bgcolor=Colors.RED_100,
    #               style=ButtonStyle(
    #                   shape=RoundedRectangleBorder(radius=25),
    #                   padding=15,
    #               ),
    #               data=label,
    #               on_click=button_etsymate,
    #           )
    #           for label in re["questions_to_ask"]["category_2"][:2]
    #       ]
    #       +
    #       [
    #         ElevatedButton(
    #             text=label,
    #             color="black",
    #             bgcolor=Colors.YELLOW_50,
    #             style=ButtonStyle(
    #                 shape=RoundedRectangleBorder(radius=25),
    #                 padding=15,
    #             ),
    #             data=label,
    #             on_click=button_etsymate,
    #         )
    #       for label in re["questions_to_ask"]["category_3"][:2]
    #       ]
    #       +[Divider(height=20, color=Colors.TRANSPARENT)])
    #   log.value=f"Category Detected: {re['category_picked']}"
    #   image_panel.update()
    #   text_input.value=""
    #   text_input.focus()
    #   conv.update()

  panel = ExpansionPanelList(
      expand_icon_color=Colors.DEEP_ORANGE_400,
      elevation=0,
      divider_color=Colors.DEEP_ORANGE_400,
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
                              #border=border.all(1,Colors.GREY_400),
                              border_radius=12,
                              content=Column(
                                  alignment=MainAxisAlignment.CENTER,
                                  # horizontal_alignment=CrossAxisAlignment.CENTER,
                                  expand=True,
                                  #scroll="auto",
                                  spacing=10,
                                  controls=[
                                      Text(f"Low in stock, only {items_available} left", color=Colors.DEEP_ORANGE_400, size=16, weight=FontWeight.BOLD),
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
                                      Divider(height=4, color=Colors.TRANSPARENT),
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
                                                  #     border=border.all(1, Colors.GREY),
                                                  #     content=Row(
                                                  #         controls=[
                                                  #             text_input:=TextField(
                                                  #                 hint_text="Looking for specific info? Ask EtsyMate!",
                                                  #                 hint_style=TextStyle(size=14),
                                                  #                 expand=True,
                                                  #                 border_color=Colors.TRANSPARENT,
                                                  #                 on_submit=etsymate
                                                  #             ),
                                                  #             IconButton(icon=Icons.SEND, icon_color=Colors.DEEP_ORANGE_400, on_click=send_message), # Modify
                                                  #         ]
                                                  #     )
                                                  # ),
                                                  text_input:=TextField(
                                                      hint_text="Looking for specific info? Ask Chatsy!",
                                                      data={"type": "text_field"},
                                                      hint_style=TextStyle(size=14),
                                                      multiline=True,
                                                      min_lines=1,
                                                      max_lines=10,
                                                      expand=True,
                                                      on_submit=send_message,
                                                      shift_enter=True,
                                                  ),
                                                  IconButton(
                                                      icon=Icons.SEND,
                                                      data={"type": "button"},
                                                      icon_color=Colors.DEEP_ORANGE_400,
                                                      on_click=send_message)
                                              ]
                                          )
                                      ),
                                      llm_response:=Container(
                                          visible=False,
                                          padding=14,
                                          border_radius=14,
                                          border=border.all(1, Colors.DEEP_ORANGE_400),
                                          content=Column(
                                              alignment=MainAxisAlignment.START,
                                              spacing=8,
                                              controls=[
                                                  Text(
                                                      spans=[
                                                          TextSpan("Your Question: ", style=TextStyle(color=Colors.GREY_800, weight=FontWeight.BOLD)),
                                                          question:=TextSpan(),
                                                      ]
                                                  ),
                                                  Text(
                                                      spans=[
                                                          TextSpan("Chatsy:  ", style=TextStyle(color=Colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)),
                                                          answer:=TextSpan(),
                                                      ]
                                                  ),
                                              ]
                                          )
                                      ),
                                      conv:=Row(
                                          wrap=True,
                                          scroll=ScrollMode.AUTO,
                                          controls=[]
                                      )
                                      # conv:=Row(
                                          # wrap=True,
                                          # scroll="auto",
                                          # controls=[
                                          #     ElevatedButton(
                                          #         text=label,
                                          #         color="black",
                                          #         bgcolor="#E3F2FD",
                                          #         style=ButtonStyle(
                                          #             shape=RoundedRectangleBorder(radius=25),
                                          #             padding=15,
                                          #         ),
                                          #         data=label,
                                          #         on_click=button_etsymate,
                                          #     )
                                          #     for k,v in questions.items() for label in v if k == "questions_category_1"
                                          #          ]
                                          # +
                                          #          [
                                          #              ElevatedButton(
                                          #                  text=label,
                                          #                  color="black",
                                          #                  bgcolor=Colors.ORANGE_500,
                                          #                  style=ButtonStyle(
                                          #                      shape=RoundedRectangleBorder(radius=25),
                                          #                      padding=15,
                                          #                  ),
                                          #                  data=label,
                                          #                  on_click=button_etsymate,
                                          #              )
                                          #              for k,v in questions.items() for label in v if k == "questions_category_2"
                                          #          ]
                                          # +
                                          #          [
                                          #              ElevatedButton(
                                          #                  text=label,
                                          #                  color="black",
                                          #                  bgcolor=Colors.YELLOW_50,
                                          #                  style=ButtonStyle(
                                          #                      shape=RoundedRectangleBorder(radius=25),
                                          #                      padding=15,
                                          #                  ),
                                          #                  data=label,
                                          #                  on_click=button_etsymate,
                                          #              )
                                          #              for k,v in questions.items() for label in v if k == "questions_category_3"
                                          #          ]
                                                   # +[Divider(height=20, color=Colors.TRANSPARENT)]
                                      # ),
                                  ]
                              )
                          ),
                      ]
                  ),
              ]
          ),
          ElevatedButton("Back", color=Colors.DEEP_ORANGE_400, on_click=lambda _: page.go("/"))
      ]
  )



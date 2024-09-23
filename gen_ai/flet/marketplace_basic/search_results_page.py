import time
import json
import random
from flet import *
from middleware import gemini_chat



def view(page):
  page.bgcolor=colors.WHITE
  page.update()
  # questions = json.loads(page.session.questions)
  questions_cat1 = json.loads(page.session.questions_cat1)
  answers_cat1 = json.loads(page.session.answers_cat1)
  questions_cat2 = json.loads(page.session.questions_cat2)
  answers_cat2 = json.loads(page.session.answers_cat2)
  textual_questions = json.loads(page.session.textual_questions)
  textual_answers = json.loads(page.session.textual_answers)
  visual_questions = json.loads(page.session.visual_questions)
  visual_answers = json.loads(page.session.visual_answers)
  textual_tile = json.loads(page.session.textual_tile)
  textual_image_uri = json.loads(page.session.textual_image_uri)
  visual_tile = json.loads(page.session.visual_tile)
  visual_image_uri = json.loads(page.session.visual_image_uri)

  items_available = random.randint(1,8)
  dollars = random.randint(0,99)
  cents = random.randint(0,99)
  price = f"$ {page.session.price}"

  def button_message(e):
    text_input.value = e.control.data["question"]
    text_input.update()
    start_time = time.time()
    #re = gemini_chat(data=e.control.data, context=str(page.session.content), image_uri=page.session.private_uri, questions=str(questions))
    end_time = time.time() - start_time
    log.value=f"Total time: {end_time}"
    log.update()
    conv.controls.clear()
    #question.text = e.control.data["question"]
    answer.text = e.control.data["answer"]
    if e.control.data["type"] == "questions_category_1":
      answer.text = e.control.data["answer"]
      answer.style = TextStyle(color=colors.GREY_800,  size=18)
      cat.content = Text(e.control.data["type"])
      cat.bgcolor = "#E3F2FD"
      cat.border_radius = 14
      response_image_panel.visible = False
      llm_response.update()
    elif e.control.data["type"] == "questions_category_2":
      answer.text = e.control.data["answer"]
      answer.style = TextStyle(color=colors.GREY_800,  size=18)
      cat.content = Text(e.control.data["type"])
      cat.bgcolor = colors.RED100
      cat.border_radius = 14
      response_image_panel.visible = False
      llm_response.update()
    elif e.control.data["type"] == "questions_category_3":
      answer.text = e.control.data["answer"]
      answer.style = TextStyle(color=colors.GREY_800, size=18)
      cat.content = Text(e.control.data["type"])
      cat.bgcolor = colors.YELLOW_50
      cat.border_radius = 14
      cat.update()
    else:
      answer.style = TextStyle(color=colors.BLACK)
    if "image_uri" in e.control.data:
      response_image_panel.visible = True
      response_image_panel.content.controls=[
          Image(
              src=image,
              width=120,
              height=120,
              fit=ImageFit.CONTAIN,
              border_radius=border_radius.all(10)
          ) for image in visual_image_uri
      ]+[
          Image(
              src=image,
              width=120,
              height=120,
              fit=ImageFit.CONTAIN,
              border_radius=border_radius.all(10)
          ) for image in textual_image_uri
      ]
      response_image_panel.update()
    text_input.focus()
    llm_response.visible = True
    relevance_text.visible = True
    relevance_text.update()
    llm_response.update()

  def send_message(e):
    data={"type": "category_1", "question": text_input.value}
    start_time = time.time()
    re=gemini_chat(data=data, context=str(page.session.content), image_uri=page.session.private_uri, questions=str(questions))
    end_time = time.time() - start_time
    log.value=f"Total time: {end_time}"
    log.update()
    conv.controls.clear()
    question.text = text_input.value
    answer.text = re
    text_input.value=""
    text_input.focus()
    llm_response.visible = True
    llm_response.update()
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
    #               bgcolor=colors.RED_100,
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
    #             bgcolor=colors.YELLOW_50,
    #             style=ButtonStyle(
    #                 shape=RoundedRectangleBorder(radius=25),
    #                 padding=15,
    #             ),
    #             data=label,
    #             on_click=button_etsymate,
    #         )
    #       for label in re["questions_to_ask"]["category_3"][:2]
    #       ]
    #       +[Divider(height=20, color=colors.TRANSPARENT)])
    #   log.value=f"Category Detected: {re['category_picked']}"
    #   image_panel.update()
    #   text_input.value=""
    #   text_input.focus()
    #   conv.update()

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
                                                  text_input:=TextField(
                                                      hint_text="Looking for specific info? Ask Chatsy!",
                                                      hint_style=TextStyle(size=14),
                                                      multiline=True,
                                                      min_lines=1,
                                                      max_lines=10,
                                                      expand=True,
                                                      on_submit=send_message,
                                                      shift_enter=True,
                                                  ),
                                                  IconButton(
                                                      icon=icons.SEND,
                                                      icon_color=colors.DEEP_ORANGE_400,
                                                      on_click=send_message
                                                  )
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
                                                  # Text(
                                                  #     spans=[
                                                  #         TextSpan("Your Question: ", style=TextStyle(color=colors.GREY_800, weight=FontWeight.BOLD)),
                                                  #         question:=TextSpan(),
                                                  #     ]
                                                  # ),
                                                  Text(
                                                      spans=[
                                                          TextSpan("Chatsy:  ", style=TextStyle(color=colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)),
                                                          answer:=TextSpan(style=TextStyle(size=20, color=colors.BLUE_700)),
                                                      ]
                                                  ),
                                                  cat:=Container(
                                                      padding=padding.only(left=15, right=15),
                                                      height=20
                                                  ),
                                                  relevance_text:=Text("Here are some other relevant listings:", visible=False),
                                                  response_image_panel:=Container(
                                                      visible=False,
                                                      content=Row(expand=1, wrap=False, scroll="always")
                                                  ),
                                              ]
                                          )
                                      ),
                                      conv:=Row(
                                          wrap=True,
                                          scroll="auto",
                                          controls=[
                                              ElevatedButton(
                                                  text=question,
                                                  color="black",
                                                  bgcolor="#E3F2FD",
                                                  style=ButtonStyle(
                                                      shape=RoundedRectangleBorder(radius=25),
                                                      padding=15,
                                                  ),
                                                  data={"type": "questions_category_1", "question": question, "answer": answer},
                                                  on_click=button_message,
                                              )
                                              for question, answer in zip(questions_cat1, answers_cat1)
                                                   ]
                                          +
                                                   [
                                                       ElevatedButton(
                                                           text=question,
                                                           color="black",
                                                           bgcolor=colors.RED_100,
                                                           style=ButtonStyle(
                                                               shape=RoundedRectangleBorder(radius=25),
                                                               padding=15,
                                                           ),
                                                           data={"type": "questions_category_2", "question": question, "answer": answer},
                                                           on_click=button_message,
                                                       )
                                                       for question, answer in zip(questions_cat2, answers_cat2)
                                                   ]
                                          +
                                                   [
                                                       ElevatedButton(
                                                           text=question,
                                                           color="black",
                                                           bgcolor=colors.YELLOW_50,
                                                           style=ButtonStyle(
                                                               shape=RoundedRectangleBorder(radius=25),
                                                               padding=15,
                                                           ),
                                                           data={"type": "questions_category_3", "question": question, "answer": answer, "tile": tile, "image_uri": image_uri},
                                                           on_click=button_message,
                                                       )
                                                       for question, answer, tile, image_uri in zip(textual_questions, textual_answers, textual_tile, textual_image_uri)
                                                   ]
                                                   +
                                                   [
                                                       ElevatedButton(
                                                           text=question,
                                                           color="black",
                                                           bgcolor=colors.YELLOW_50,
                                                           style=ButtonStyle(
                                                               shape=RoundedRectangleBorder(radius=25),
                                                               padding=15,
                                                           ),
                                                           data={"type": "questions_category_3", "question": question, "answer": answer, "tile": tile, "image_uri": image_uri},
                                                           on_click=button_message,
                                                       )
                                                       for question, answer, tile, image_uri in zip(visual_questions, visual_answers, visual_tile, visual_image_uri)
                                                   ]
                                                   +[Divider(height=20, color=colors.TRANSPARENT)]
                                      ),
                                  ]
                              )
                          ),
                      ]
                  ),
              ]
          ),
          ElevatedButton("Back", color=colors.DEEP_ORANGE_400, on_click=lambda _: page.go("/main"))
      ]
  )



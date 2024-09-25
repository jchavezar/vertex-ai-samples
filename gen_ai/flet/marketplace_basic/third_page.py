from flet import *

def view(page):
  print(page.bgcolor)
  return View(
      "/third",
      [
          Text("Category 3 Diagram", size=24),
          Divider(height=30, color=colors.TRANSPARENT),
          Column(
              alignment=MainAxisAlignment.CENTER,
              scroll="auto",
              expand=True,
              controls=[
                  Row(
                      alignment=MainAxisAlignment.CENTER,
                      controls=[
                          Container(
                              height=550,
                              content=Image(src="https://gcpetsy.sonrobots.net/artifacts/et_cat3_diagram.png", fit=ImageFit.CONTAIN)
                          ),
                      ]
                  ),
              ]
          ),
          BottomAppBar(
              bgcolor=colors.TRANSPARENT,
              content=Row(
                  controls=[
                      ElevatedButton("Back", on_click=lambda _: page.go("/"), bgcolor=colors.DEEP_ORANGE_400, color=colors.WHITE)
                  ]
              )
          )
      ]
  )
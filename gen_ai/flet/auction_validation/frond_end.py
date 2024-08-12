from flet import *
from back_end import llm, vector_search, vector_search_images


def main(page: Page):
  value = Text()

  def on_file_picker_result(e):
    if file_picker.result:
      file = file_picker.result.files[0]
      form.content.controls[1].content.controls.append(Image(
          src=file.path,
          width=400,
          height=400,
          fit=ImageFit.CONTAIN,
      ))
      form.content.controls[1].update()
      input = {
          "item_name": item_name.value,
          "country_ori_name": country_ori_name.value,
          "artist_name": artist_name.value,
          "title_work_name": title_work_name.value
      }

      re = llm(input, file.path)
      form.content.controls[1].content.controls.append(
          Text(re)
      )
      form.content.controls[1].update()
      response = vector_search_images(file.path)
      verification_widget.content.controls.clear()
      verification_widget.content.update()
      verification_widget.update()
      for k,v in response.items():
        verification_widget.content.controls.append(Image(
            src=v,
            width=400,
            height=400,
            fit=ImageFit.CONTAIN,
        ))
        verification_widget.content.update()

  file_picker = FilePicker(on_result=on_file_picker_result)

  def upload_file(e):
    file_picker.pick_files(allow_multiple=False)

  def button_click(e):
    value.value = item_name.value
    form.content.controls[1].update()

  item_name: TextField = TextField(
      label="Item Name",
      border_color=colors.TRANSPARENT)
  country_ori_name: TextField = TextField(
      label="Country of Origin",
      border_color=colors.TRANSPARENT
  )
  artist_name: TextField = TextField(
      label="Artist Name",
      border_color=colors.TRANSPARENT
  )
  title_work_name: TextField = TextField(
      label="Title of Work",
      border_color=colors.TRANSPARENT
  )

  buttons: Row = Row(
      alignment=MainAxisAlignment.SPACE_EVENLY,
      controls=[
          Text("Attach an Image:"),
          ElevatedButton(
              "Upload",
              on_click=upload_file,
              content=Icon(icons.IMAGE)
          ),
          ElevatedButton(
              "Send",
              on_click=button_click,
              content=Icon(icons.SEND)
          )
      ]
  )

  form: Container = Container(
      content=Row(
          controls=[
              Container(
                  height=400,
                  padding=25,
                  expand=1,
                  border_radius=12.0,
                  border=border.all(1, colors.GREY),
                  content=Column(
                      alignment=MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          Container(
                              content=item_name,
                              width=450,
                              border=border.only(bottom=BorderSide(1, colors.GREY))
                          ),
                          Container(
                              content=country_ori_name,
                              width=450,
                              border=border.only(bottom=BorderSide(1, colors.GREY))
                          ),
                          Container(
                              content=artist_name,
                              width=450,
                              border=border.only(bottom=BorderSide(1, colors.GREY))
                          ),
                          Container(
                              content=title_work_name,
                              width=450,
                              border=border.only(bottom=BorderSide(1, colors.GREY))
                          ),
                          Container(
                              width=450,
                              content=buttons,
                          )
                      ]
                  )
              ),
              Container(
                  alignment=alignment.top_center,
                  padding=12,
                  height=600,
                  expand=1,
                  border_radius=12.0,
                  border=border.all(1, colors.GREY),
                  content=Column(
                      alignment=MainAxisAlignment.SPACE_BETWEEN,
                  )
              )
          ]
      )
  )

  def verification(e):
    res = vector_search(e.control.value)
    verification_widget.content.controls.clear()
    verification_widget.content.update()
    verification_widget.update()
    for k,v in res.items():
      verification_widget.content.controls.append(Image(
          src=v,
          width=400,
          height=400,
          fit=ImageFit.CONTAIN,
      ))
      verification_widget.content.update()
    verification_widget.content.controls.append(Divider(height=1, color=colors.TRANSPARENT))
    verification_widget.content.controls.append(Text(res))
    verification_widget.update()

  verification_widget: Container = Container(
      alignment=alignment.center,
      content=Column(
          alignment=MainAxisAlignment.CENTER,
          horizontal_alignment=CrossAxisAlignment.CENTER,
          controls=[
          ]
      )
  )

  main_view: ListView = ListView(
      spacing=10,
      auto_scroll=True,
      controls=[
          form,
          TextField(
              label="Enter Something",
              on_change=verification
          ),
          verification_widget
      ]
  )

  page.add(
      AppBar(
          title=Text("Gemini Auction Validator"),
          center_title=True),
      # Wrap the ListView in a scrollable Column
      Column(
          expand=True,
          scroll=True,  # Enables scrolling for the Column
          controls=[
              main_view
          ]
      ),
      file_picker
  )

app(target=main)
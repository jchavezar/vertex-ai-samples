from flet import *
from back_end import chatbot

def main(page: Page):

  def chatbot_message(e):
    for i in selected_services.controls:
      i.bgcolor = colors.TRANSPARENT
      selected_services.update()
    # Get user input
    text = input_box.content.value

    # Clear the input box
    input_box.content.value = ""

    # Append both user and bot texts to the chatbot window
    chatbot_window.controls[0].content.controls.append(
        Column(
            alignment=MainAxisAlignment.CENTER,
            controls=[
                Text("You:", style=TextStyle(size=18, color=colors.GREY, weight=FontWeight.BOLD)),
                Text(text, style=TextStyle(size=16))
            ]
        )
    )
    chatbot_window.controls[1].content.controls.append(
        Column(
            alignment=MainAxisAlignment.CENTER,
            controls=[
                Text("Original", style=TextStyle(size=18, color=colors.GREY, weight=FontWeight.BOLD)),
                Text(text, style=TextStyle(size=16))
            ]
        )
    )
    chatbot_window.controls[0].content.controls.append(
        Divider(height=15, color=colors.TRANSPARENT)
    )
    chatbot_window.update()
    # Get chatbot response
    response = chatbot(text)
    print(response)
    if "image_src64" in response:
      chatbot_window.controls[0].content.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Text("Gemini:", style=TextStyle(size=18, color=colors.PURPLE, weight=FontWeight.BOLD)),
                  Text(response["answer"], style=TextStyle(size=16)),
                  Image(src_base64=response["image_src64"])
              ]
          )
      )
      selected_services.controls[3].bgcolor = colors.YELLOW_300
      response.pop('image_src64', None)
      chatbot_window.controls[1].content.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Divider(height=10, color=colors.TRANSPARENT),
                  Text("Using Anthropic or YoutubeAPI Transcripts", style=TextStyle(size=16, color=colors.GREY)),
                  Text("Gemini Log:", style=TextStyle(size=18, color=colors.GREEN, weight=FontWeight.BOLD)),
                  Text(response, style=TextStyle(size=16, weight=FontWeight.BOLD))
              ]
          )
      )
    else:
      chatbot_window.controls[0].content.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Text("Gemini:", style=TextStyle(size=18, color=colors.PURPLE, weight=FontWeight.BOLD)),
                  Text(response["answer"], style=TextStyle(size=16))
              ]
          )
      )
      chatbot_window.controls[1].content.controls.append(
          Column(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Divider(height=10, color=colors.TRANSPARENT),
                  Text("Using Anthropic or YoutubeAPI Transcripts", style=TextStyle(size=16, color=colors.GREY)),
                  Text("Gemini Log:", style=TextStyle(size=18, color=colors.GREEN, weight=FontWeight.BOLD)),
                  Text(response, style=TextStyle(size=16, weight=FontWeight.BOLD))
              ]
          )
      )
    chatbot_window.update()
    chatbot_window.controls[0].content.controls.append(
        Divider(height=20, color=colors.TRANSPARENT)
    )
    if response["bananas"] != "":
      print("bananas!")
      selected_services.controls[1].bgcolor = colors.BROWN_300
    if response["youtube"] != "":
      print("youtube!")
      selected_services.controls[2].bgcolor = colors.RED_300
    if response["answer"] != "":
      print("gemini!")
      selected_services.controls[0].bgcolor = colors.PURPLE_300

    # Update the page to reflect changes
    page.update()

  # Input box for user input
  input_box: Container = Container(
      content=TextField(
          label="Ask something...",
          on_submit=chatbot_message
      )
  )

  # Buttons
  button_height=80
  selected_services: Column = Column(
      controls=[
          Container(
              alignment=alignment.center,
              border=border.all(1, colors.GREY),
              border_radius=12,
              height=button_height,
              width=100,
              content=Text("Gemini")
          ),
          Container(
              alignment=alignment.center,
              border=border.all(1, colors.GREY),
              border_radius=12,
              height=button_height,
              width=100,
              content=Text("Anthropic")
          ),
          Container(
              alignment=alignment.center,
              border=border.all(1, colors.GREY),
              border_radius=12,
              height=button_height,
              width=100,
              content=Text("Youtube")
          ),
          Container(
              alignment=alignment.center,
              border=border.all(1, colors.GREY),
              border_radius=12,
              height=button_height,
              width=100,
              content=Text("Imagen")
          )
      ]
  )

  # Header Functions
  header: Container = Container(
      alignment=alignment.center,
      height=90,
      content=Container(
          height=70,
          width=70,
          content=Image(
              src=f"https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Etsy_logo.svg/2880px-Etsy_logo.svg.png",
              fit=ImageFit.SCALE_DOWN,
          ),
      ),
  )

  # Main window for displaying conversation
  chatbot_window: Row = Row(
      controls=[
          Container(
              height=800,
              padding=10,
              border_radius=12,
              border=border.all(1, colors.GREY),
              expand=3,
              content=ListView()
          ),
          Container(
              height=800,
              padding=10,
              border_radius=12,
              border=border.all(1, colors.GREY),
              expand=3,
              content=ListView()
          ),
          Container(
              height=800,
              padding=10,
              border_radius=12,
              border=border.all(1, colors.GREY),
              expand=1,
              content=selected_services
          )
      ]
  )

  # Main layout including chatbot window and input box
  main_window: Column = Column(
      controls=[
          #header,
          chatbot_window,
          input_box
      ]
  )

  # Add main window to the page
  page.add(main_window)

# Run the app
app(target=main)

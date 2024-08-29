from flet import *
from back_end import llm

prompts = {
    "summarization":  """
                        Create a detailed summary about the following video:
  
                        Output rules:
                        Output as Markdown without Markdown decorators (```)
                        
                        Video:
                      """,
    "transcription":  """
                        Extract all the transcription, try to add the  name of the narrator:
  
                        Output rules:
                        Output as Markdown without Markdown decorators (```)
                        
                        Video:
                      """,
    "object_analysis":  """
                        Your mission is to detect as many objects as possible from the movie and add an occurrences count:
    
                        Output rules:
                        Output as Markdown without Markdown decorators (```)
                        e.g.
                        character_name_1: <number_of_occurrences>,
                        character_name_2: <number_of_occurrences>,
                        etc
                        
                        Video:
                      """,
    "sentiment_analysis":  """
                        Your task is to extract all the sentiment analysis capture either from audio or video:
  
                        <rules>
                        Try to guess who is the person/character if not describe her/him.
                        </rules>
  
                        Output rules:
                        Output as Markdown without Markdown decorators (```)
                        e.g.
                        object_1: <sentiment_type>,
                        object_2: <sentiment_type>,
                        etc
                        
                        Video:
                      """,
    "content_prediction":  """
                        Based on the characters' expressions and the current setting, what event or action do you foresee occurring in the next few moments?
                        Give me 2 possible scenarios, if theres an scene inside of scene try to predict it as well.
  
                        Output rules:
                        Output as Markdown without Markdown decorators (```)
                        
                        Video:
                      """,
}


def video_llm(page: Page, sample_media: list):

  def generative_function(func):
    prompt = prompts[func]
    print(video.playlist)
    re = llm(prompt, video.playlist[0].resource)
    print(re)
    if func == "summarization":
      llm_space.content.controls.append(Text("Summarization", style=TextStyle(color=colors.PINK, weight=FontWeight.BOLD, size=18)))
    elif func == "transcription":
      llm_space.content.controls.append(Text("Transcription", style=TextStyle(color=colors.PURPLE, weight=FontWeight.BOLD, size=18)))
    elif func == "object_analysis":
      llm_space.content.controls.append(Text("Object Analysis", style=TextStyle(color=colors.BLUE, weight=FontWeight.BOLD, size=18)))
    elif func == "sentiment_analysis":
      llm_space.content.controls.append(Text("Sentiment Analysis", style=TextStyle(color=colors.GREEN, weight=FontWeight.BOLD, size=18)))
    elif func == "content_prediction":
      llm_space.content.controls.append(Text("Content Prediction", style=TextStyle(color=colors.RED, weight=FontWeight.BOLD, size=18)))
    llm_space.content.controls.append(Markdown(re, selectable=True))
    llm_space.content.controls.append(Divider(height=5, color=colors.TRANSPARENT))
    view.page.scroll = "always"
    view.scroll_to(offset=-1)
    view.update()

  def handle_pause(e):
    video.pause()
  print("Video.pause()")

  def handle_play_or_pause(e):
    video.play_or_pause()
    print("Video.play_or_pause()")

  def handle_play(e):
    video.play()
    print("Video.play()")

  def handle_stop(e):
    video.stop()
    print("Video.stop()")

  def handle_next(e):
    video.next()
    print("Video.next()")

  def handle_previous(e):
    video.previous()
    print("Video.previous()")

  def video_loaded(e, video):
      video.seek(page.session.start_off*1000)
      video.play()  # Try playing after loading
      page.update()

  video: Video = Video(
      expand=True,
      playlist=sample_media,
      #fill_color=colors.BLUE_400,
      aspect_ratio=16/9,
      volume=100,
      autoplay=False,
      filter_quality=FilterQuality.HIGH,
      muted=False,
      on_loaded=lambda e: video_loaded(e, video),
      on_enter_fullscreen=lambda e: print("Video entered fullscreen!"),
      on_exit_fullscreen=lambda e: print("Video exited fullscreen!"),
  )

  main_view: Column = Column(
      horizontal_alignment=CrossAxisAlignment.CENTER,
      expand=True,
      scroll="auto",
      controls=[
          Container(
              width=660,
              height=370,
              content=video
          ),
          view:=ListView(
              expand=True,
              auto_scroll=True,
              controls=[
                  Container(
                      width=700,
                      content=Row(
                          wrap=True,
                          alignment=MainAxisAlignment.CENTER,
                          controls=[
                              ElevatedButton("Play", on_click=handle_play),
                              ElevatedButton("Pause", on_click=handle_pause),
                              ElevatedButton("Play Or Pause", on_click=handle_play_or_pause),
                              ElevatedButton("Stop", on_click=handle_stop),
                              ElevatedButton("Next", on_click=handle_next),
                              ElevatedButton("Previous", on_click=handle_previous),
                              ElevatedButton(
                                  icon=icons.CARPENTER_OUTLINED,
                                  text="Summarization",
                                  on_click=lambda e: generative_function("summarization"),
                                  color=colors.PINK,
                                  bgcolor=colors.PINK_50),
                              ElevatedButton(
                                  icon=icons.CARPENTER_OUTLINED,
                                  text="Transcription",
                                  on_click=lambda e: generative_function("transcription"),
                                  color=colors.PURPLE,
                                  bgcolor=colors.PURPLE_50),
                              ElevatedButton(
                                  icon=icons.CARPENTER_OUTLINED,
                                  text="Object Detection",
                                  on_click=lambda e: generative_function("object_analysis"),
                                  color=colors.BLUE,
                                  bgcolor=colors.BLUE_50),
                              ElevatedButton(
                                  icon=icons.CARPENTER_OUTLINED,
                                  text="Sentiment Analysis",
                                  on_click=lambda e: generative_function("sentiment_analysis"),
                                  color=colors.GREEN,
                                  bgcolor=colors.GREEN_50),
                              ElevatedButton(
                                  icon=icons.CARPENTER_OUTLINED,
                                  text="Content Prediction",
                                  on_click=lambda e: generative_function("content_prediction"),
                                  color=colors.RED,
                                  bgcolor=colors.RED_50),
                          ]
                      )
                  ),
                  llm_space := Container(
                      margin=20,
                      content=Column(
                          horizontal_alignment=CrossAxisAlignment.CENTER,
                          controls=[
                          ]
                      )
                  )
              ]
          )
      ]
  )

  return main_view
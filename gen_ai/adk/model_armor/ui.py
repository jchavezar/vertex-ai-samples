from flet import *
from backend import generate_content

def main(page: Page):
    page.title = "Gemini Chat UI"
    page.window_width = 800
    page.window_height = 700
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    # Changed page background to a very light blue-grey for contrast with white bubbles
    page.bgcolor = Colors.BLUE_GREY_50

    # Load custom font - Space Mono from Google Fonts for a futuristic feel
    page.fonts = {
        "Space Mono": "https://fonts.googleapis.com/css2?family=Space+Mono&display=swap",
    }
    # Apply the font to the page's default text style
    page.theme = Theme(font_family="Space Mono")
    page.update()

    hello_gradient = LinearGradient(
        begin=alignment.center_left,
        end=alignment.center_right,
        colors=[Colors.BLUE_400, Colors.PURPLE_400, Colors.PINK_300, Colors.RED_300],
    )

    hello_text_content = Text(
        "Hello, Jesus",
        size=36,
        weight=FontWeight.BOLD,
        text_align=TextAlign.CENTER,
        font_family="Space Mono", # Apply the new font
    )

    hello_text_shader_mask = ShaderMask(
        content=hello_text_content,
        blend_mode=BlendMode.SRC_IN,
        shader=hello_gradient
    )

    chat_list_view = ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
        padding=padding.symmetric(horizontal=20, vertical=10)
    )

    main_content_area = Container(
        content=hello_text_shader_mask,
        alignment=alignment.center,
        expand=True
    )

    async def on_submit_message(e):
        user_input = e.control.value
        if not user_input:
            return

        if main_content_area.content == hello_text_shader_mask:
            main_content_area.content = chat_list_view
            main_content_area.alignment = alignment.top_center

        # User's message with "User" label
        chat_list_view.controls.append(
            Column(
                [
                    Text(
                        "User",
                        size=12,
                        color=Colors.GREY_600,
                        weight=FontWeight.BOLD,
                        text_align=TextAlign.END,
                        font_family="Space Mono", # Apply font
                    ),
                    Row(
                        [
                            Container(
                                content=Text(
                                    user_input,
                                    selectable=True,
                                    color=Colors.BLACK87, # Text color for better contrast on light bubble
                                    size=15,
                                    font_family="Space Mono", # Apply font
                                ),
                                padding=padding.symmetric(horizontal=12, vertical=8),
                                bgcolor=Colors.BLUE_GREY_100, # Light blue-grey for user bubble
                                border_radius=border_radius.all(18),
                                alignment=alignment.center_right,
                                border=border.all(1, Colors.GREY_300), # Subtle border
                            )
                        ],
                        alignment=MainAxisAlignment.END,
                    )
                ],
                horizontal_alignment=CrossAxisAlignment.END,
                spacing=2,
            )
        )

        submitted_input = user_input
        e.control.value = ""
        e.control.focus()
        page.update()

        response = await generate_content(submitted_input)

        # Gemini's response with "Gemini" label
        chat_list_view.controls.append(
            Column(
                [
                    Text(
                        "Gemini",
                        size=12,
                        color=Colors.GREY_600,
                        weight=FontWeight.BOLD,
                        text_align=TextAlign.START,
                        font_family="Space Mono", # Apply font
                    ),
                    Row(
                        [
                            Container(
                                content=Text(
                                    response,
                                    selectable=True,
                                    color=Colors.BLACK87, # Text color for better contrast on white bubble
                                    size=15,
                                    expand=True,
                                    no_wrap=False,
                                    max_lines=None,
                                    weight=FontWeight.NORMAL,
                                    font_family="Space Mono", # Apply font
                                ),
                                padding=padding.symmetric(horizontal=12, vertical=8),
                                bgcolor=Colors.WHITE, # White for Gemini bubble
                                border_radius=border_radius.all(18),
                                alignment=alignment.center_left,
                                expand=True,
                                border=border.all(1, Colors.GREY_300), # Subtle border
                            )
                        ],
                        alignment=MainAxisAlignment.START,
                    )
                ],
                horizontal_alignment=CrossAxisAlignment.START,
                spacing=2,
            )
        )
        page.update()

    chat_input_field = TextField(
        hint_text="Ask Gemini",
        border=InputBorder.NONE,
        expand=True,
        text_style=TextStyle(color=Colors.BLACK87, size=16, font_family="Space Mono"), # Apply font
        hint_style=TextStyle(color=Colors.BLACK45, size=16, font_family="Space Mono"), # Apply font
        cursor_color=Colors.BLACK54,
        on_submit=on_submit_message,
    )

    input_container = Container(
        width=600,
        bgcolor=Colors.WHITE,
        border=border.all(1, Colors.with_opacity(0.3, Colors.BLACK26)),
        border_radius=border_radius.all(30),
        padding=padding.symmetric(horizontal=15, vertical=5),
        shadow=BoxShadow(
            spread_radius=1,
            blur_radius=3,
            color=Colors.with_opacity(0.1, Colors.BLACK),
            offset=Offset(0, 1),
        ),
        content=Column(
            [
                Row(
                    [
                        chat_input_field,
                        IconButton(
                            Icons.MIC_NONE_OUTLINED,
                            icon_color=Colors.BLACK54,
                            tooltip="Voice input"
                        ),
                    ],
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Divider(height=1, color=Colors.with_opacity(0.3, Colors.BLACK26)),
                Row(
                    [
                        IconButton(
                            Icons.ADD,
                            icon_size=20,
                            icon_color=Colors.BLACK54,
                            tooltip="Add",
                        ),
                        TextButton(
                            content=Row([Icon(Icons.SEARCH, size=18, color=Colors.BLACK54), Text("Search", color=Colors.BLACK54, font_family="Space Mono")]), # Apply font
                            style=ButtonStyle(padding=padding.symmetric(horizontal=8)),
                        ),
                        IconButton(
                            Icons.MORE_HORIZ,
                            icon_size=20,
                            icon_color=Colors.BLACK54,
                            tooltip="More",
                        ),
                    ],
                    alignment=MainAxisAlignment.START,
                    spacing=5,
                )
            ]
        )
    )

    page_layout = Column(
        [
            main_content_area,
            input_container,
        ],
        expand=True,
        horizontal_alignment=CrossAxisAlignment.CENTER
    )

    page.add(page_layout)

if __name__ == "__main__":
    app(target=main)
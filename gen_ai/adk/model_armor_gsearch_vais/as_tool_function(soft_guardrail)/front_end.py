from flet import *
from agent import generate_content

def main(page: Page):
    page.title = "Gemini Chat UI"
    page.window_width = 800
    page.window_height = 700
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.bgcolor = Colors.WHITE

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

    user_message_color = Colors.BLUE_700
    gemini_message_color = Colors.PURPLE_700

    async def on_submit_message(e):
        user_input = e.control.value
        if not user_input:
            return

        if main_content_area.content == hello_text_shader_mask:
            main_content_area.content = chat_list_view
            main_content_area.alignment = alignment.top_center

        chat_list_view.controls.append(
            Row(
                [
                    Container(
                        content=Text(
                            user_input,
                            selectable=True,
                            color=Colors.BLACK87,
                            size=15,
                        ),
                        padding=padding.symmetric(horizontal=12, vertical=8),
                        bgcolor=Colors.GREY_100,
                        border_radius=border_radius.all(18),
                        alignment=alignment.center_right,
                    )
                ],
                alignment=MainAxisAlignment.END,
            )
        )

        submitted_input = user_input
        e.control.value = ""
        e.control.focus()
        page.update()

        response = await generate_content(submitted_input)
        chat_list_view.controls.append(
            Row(
                [
                    Icon(
                        Icons.STAR_HALF_OUTLINED,
                        color=Colors.DEEP_PURPLE_ACCENT_100,
                        size=20
                    ),
                    Text(
                        response,
                        selectable=True,
                        color=Colors.BLACK87,
                        size=15,
                        expand=True,
                        no_wrap=False,
                        max_lines=None,
                        weight=FontWeight.NORMAL
                    )
                ],
                alignment=MainAxisAlignment.START,
            )
        )
        page.update()

    chat_input_field = TextField(
        hint_text="Ask Gemini",
        border=InputBorder.NONE,
        expand=True,
        text_style=TextStyle(color=Colors.BLACK87, size=16),
        hint_style=TextStyle(color=Colors.BLACK45, size=16),
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
                            content=Row([Icon(Icons.SEARCH, size=18, color=Colors.BLACK54), Text("Search", color=Colors.BLACK54)]),
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
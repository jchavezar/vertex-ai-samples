import flet as ft
from agent import send_question


def main(page: ft.Page):
    page.title = "Gemini Interface"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 40
    page.last_latency_info = ""  # Store the full string for the last latency

    # --- UI Controls ---

    last_latency_display = ft.Text(
        value="",
        color=ft.Colors.GREY,
        size=16,
        selectable=True
    )

    current_latency_display = ft.Text(
        value="",
        color=ft.Colors.GREEN_ACCENT_400,
        weight=ft.FontWeight.BOLD,
        size=16,
        selectable=True
    )

    grounding_dropdown = ft.Dropdown(
        width=250,
        options=[
            ft.dropdown.Option("Google Ent Grounding"),
            ft.dropdown.Option("No Google Ent Grounding"),
        ],
        value="No Google Ent Grounding",
        color=ft.Colors.WHITE,
        hint_text="Select Grounding",
        border_color=ft.Colors.BLUE_ACCENT_200
    )

    chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    status_bar = ft.ProgressBar(
        width=700,
        color=ft.Colors.BLUE_ACCENT_200,
        bgcolor=ft.Colors.WHITE12,
        visible=False,
    )

    async def send_message(e):
        text_field_control = e.control
        if not text_field_control.value:
            return

        grounding_option = grounding_dropdown.value
        user_message = text_field_control.value

        chat_history.controls.append(
            ft.Row(
                [ft.Text(f"You: {user_message}", color=ft.Colors.CYAN_ACCENT_200, size=16, weight=ft.FontWeight.BOLD)],
                alignment=ft.MainAxisAlignment.END,
            )
        )
        status_bar.visible = True
        text_field_control.disabled = True
        last_latency_display.value = page.last_latency_info
        current_latency_display.value = "Current: (Running...)"
        page.update()

        try:
            is_direct = grounding_option == "No Google Ent Grounding"
            response, time = await send_question(user_message, direct=is_direct)

            chat_history.controls.append(
                ft.Column(
                    [
                        ft.Text("Bot:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.BLUE_ACCENT_100),
                        ft.Text(response, selectable=True, size=16),
                    ]
                )
            )
            current_latency_display.value = f"Current: ({grounding_option}) {time:.2f}s"
            page.last_latency_info = f"Last: ({grounding_option}) {time:.2f}s"
            text_field_control.value = ""

        except Exception as ex:
            chat_history.controls.append(ft.Text(f"Error: {ex}", color=ft.Colors.RED))
            current_latency_display.value = "Current: (Error)"

        finally:
            status_bar.visible = False
            text_field_control.disabled = False
            page.update()
            text_field_control.focus()

    input_text_field = ft.TextField(
        hint_text="Ask Gemini",
        hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
        filled=False,
        border=ft.InputBorder.NONE,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        expand=True,
        on_submit=send_message,
    )

    input_container = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.WHITE70),
                ft.Container(
                    content=input_text_field,
                    expand=True,
                    margin=ft.margin.only(left=10, right=10),
                ),
                ft.IconButton(icon=ft.Icons.MIC, icon_color=ft.Colors.WHITE70),
            ]
        ),
        width=700,
        height=60,
        border_radius=30,
        bgcolor=ft.Colors.WHITE12,
        padding=ft.padding.only(left=15, right=5),
    )

    latency_column = ft.Column(
        [last_latency_display, current_latency_display],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.END
    )

    page.add(
        ft.Row(
            [grounding_dropdown, latency_column],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        ft.Container(content=chat_history, expand=True, border=ft.border.all(1, ft.Colors.WHITE24), border_radius=10, padding=10),
        status_bar,
        input_container,
    )


ft.app(target=main)

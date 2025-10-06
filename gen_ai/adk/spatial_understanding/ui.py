import os
import flet as ft

UPLOAD_DIRECTORY = "uploaded_files"

def main(page: ft.Page):
    page.title = "Simple Image Attachment"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    selected_files_text = ft.Text("No files selected yet.", size=16)

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    def handle_upload_complete(e):
        print(f"Server-side check: Upload complete! Files saved to {UPLOAD_DIRECTORY}")

    def handle_file_selection(e):
        if not e.files:
            page.update()
            return

        upload_list = []
        file_names = ", ".join([file.name for file in e.files])
        print(f"Files selected: {file_names}")

        for file in e.files:
            upload_url = page.get_upload_url(file.name, 3600)
            upload_list.append(ft.FilePickerUploadFile(file.name, upload_url))
            print(f"Generated URL for {file.name}: {upload_url}")

        file_picker.upload(upload_list)

        print(f"Starting background upload for: {file_names}")
        page.update()

    file_picker = ft.FilePicker(
        on_result=handle_file_selection,
        on_upload=handle_upload_complete
    )

    page.overlay.append(file_picker)
    page.update()

    page.add(
        ft.Column(
            [
                ft.ElevatedButton(
                    "Attach Images",
                    icon=ft.Icons.IMAGE,
                    on_click=lambda _: file_picker.pick_files(allow_multiple=True)
                ),
                selected_files_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

ft.app(target=main, view=ft.AppView.FLET_APP, upload_dir=UPLOAD_DIRECTORY)

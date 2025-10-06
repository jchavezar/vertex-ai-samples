import os
import secrets
from flet import *

UPLOAD_DIRECTORY = "uploaded_files"

def main(page: Page):
    page.title = "Flet Web File Uploader"
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.vertical_alignment = MainAxisAlignment.CENTER

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    def handle_upload_complete(e):
        print(f"Server-side check: Upload complete! Files saved to {UPLOAD_DIRECTORY}")

    def handle_file_selection(e: FilePickerResultEvent):
        if not e.files:
            page.update()
            return

        upload_list = []
        file_names = ", ".join([file.name for file in e.files])
        print(f"Files selected: {file_names}")

        for file in e.files:
            upload_url = page.get_upload_url(file.name, 3600)
            upload_list.append(FilePickerUploadFile(file.name, upload_url))
            print(f"Generated URL for {file.name}: {upload_url}")

        file_picker.upload(upload_list)

        print(f"Starting background upload for: {file_names}")
        page.update()

    file_picker = FilePicker(
        on_result=handle_file_selection,
        on_upload=handle_upload_complete
    )

    page.overlay.append(file_picker)
    page.update()

    page.add(
        Card(
            width=400,
            content=Container(
                padding=20,
                content=Column(
                    [
                        Text("Web File Uploader", size=24, weight=FontWeight.BOLD),
                        Text("Selected files will be uploaded to the server's 'uploaded_files' directory.",
                             color=Colors.BLUE_GREY_400),
                        Divider(),
                        ElevatedButton(
                            "Choose & Upload Files...",
                            icon=Icons.UPLOAD_FILE,
                            on_click=lambda _: file_picker.pick_files(allow_multiple=True),
                        ),
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER
                )
            )
        )
    )

if __name__ == "__main__":
    if "FLET_SECRET_KEY" not in os.environ:
        os.environ["FLET_SECRET_KEY"] = secrets.token_hex(16)

    app(target=main, upload_dir=UPLOAD_DIRECTORY)

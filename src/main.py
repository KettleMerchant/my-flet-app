import os
import time
import flet as ft
from supabase import create_client, Client

os.environ.setdefault("FLET_SECRET_KEY", "test-tunnel-secret-key-2026")

# Temporary staging folder on Render before pushing to Supabase
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)

# Supabase Credentials (loaded from Render Environment Variables)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
BUCKET_NAME = "uploads"

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def main(page: ft.Page):
    page.title = "Flet + Supabase Cloud App"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 24
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    status_color = ft.Colors.GREEN if supabase else ft.Colors.ORANGE
    status_text = (
        "Connected to Supabase Storage!"
        if supabase
        else "Missing SUPABASE_URL / SUPABASE_KEY in Render Environment"
    )
    status_badge = ft.Text(status_text, color=status_color, weight=ft.FontWeight.BOLD)

    # 1. Image Upload & Permanent Preview
    upload_status = ft.Text("No image uploaded yet.", italic=True)
    image_preview = ft.Image(
        src="",
        width=280,
        height=280,
        fit=ft.BoxFit.CONTAIN,
        visible=False,
        border_radius=12,
    )

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            local_path = os.path.join(TEMP_UPLOAD_FOLDER, e.file_name)

            if not supabase:
                upload_status.value = "Error: Supabase credentials not configured."
                upload_status.color = ft.Colors.RED
                page.update()
                return

            try:
                upload_status.value = "Syncing to permanent cloud storage..."
                page.update()

                # Create a unique filename so files never overwrite each other
                unique_name = f"{int(time.time())}_{e.file_name}"

                with open(local_path, "rb") as f:
                    supabase.storage.from_(BUCKET_NAME).upload(
                        path=unique_name,
                        file=f,
                        file_options={"content-type": "image/jpeg"},
                    )

                # Get permanent public URL from Supabase
                public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(
                    unique_name
                )

                # Remove temporary file from Render
                if os.path.exists(local_path):
                    os.remove(local_path)

                upload_status.value = f"Saved permanently: {unique_name}"
                upload_status.color = ft.Colors.BLUE
                image_preview.src = public_url
                image_preview.visible = True
            except Exception as ex:
                upload_status.value = f"Supabase upload failed: {ex}"
                upload_status.color = ft.Colors.RED

            page.update()

    file_picker = ft.FilePicker(on_upload=on_upload_progress)

    async def pick_and_upload(e):
        files = await file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        )
        if not files:
            upload_status.value = "Upload cancelled."
            page.update()
            return

        selected_file = files[0]
        upload_status.value = f"Uploading {selected_file.name}..."
        page.update()

        upload_url = page.get_upload_url(selected_file.name, expires=60)
        await file_picker.upload(
            [ft.FilePickerUploadFile(name=selected_file.name, upload_url=upload_url)]
        )

    # 2. Live Text Sync
    msg_input = ft.TextField(
        label="Type a test message...",
        width=320,
        on_submit=lambda e: send_message(e),
    )
    chat_log = ft.Column(spacing=6)

    def send_message(e):
        if not msg_input.value.strip():
            return
        chat_log.controls.append(
            ft.Container(
                content=ft.Text(f"Received: {msg_input.value}"),
                padding=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border_radius=8,
            )
        )
        msg_input.value = ""
        page.update()

    page.add(
        ft.Icon(ft.Icons.CLOUD_DONE, size=48, color=ft.Colors.BLUE),
        ft.Text("Flet + Supabase Cloud Storage", size=22, weight=ft.FontWeight.BOLD),
        status_badge,
        ft.Divider(height=20),
        ft.Text("1. Permanent Image Upload", size=16, weight=ft.FontWeight.W_600),
        ft.Button(
            content="Pick & Upload Image",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=pick_and_upload,
        ),
        upload_status,
        image_preview,
        ft.Divider(height=20),
        ft.Text("2. Live Data Sync", size=16, weight=ft.FontWeight.W_600),
        ft.Row(
            [
                msg_input,
                ft.IconButton(icon=ft.Icons.SEND, on_click=send_message),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        chat_log,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8550))
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        upload_dir=TEMP_UPLOAD_FOLDER,
        assets_dir=TEMP_UPLOAD_FOLDER,
    )

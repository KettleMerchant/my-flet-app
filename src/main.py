import os
import flet as ft

# Required by Flet so FilePicker uploads work over HTTP / Cloud Servers
os.environ.setdefault("FLET_SECRET_KEY", "test-tunnel-secret-key-2026")

# Resolve absolute upload path relative to src/ so uploads & image previews match
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def main(page: ft.Page):
    page.title = "Flet Cloud App"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 24
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- UI Controls ---
    status_badge = ft.Text(
        "Server Live! Ready to test.",
        color=ft.Colors.GREEN,
        weight=ft.FontWeight.BOLD,
    )

    # 1. Image Upload & Live Preview
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
            upload_status.value = f"Uploaded: {e.file_name}"
            upload_status.color = ft.Colors.BLUE
            # Served directly because assets_dir=UPLOAD_FOLDER
            image_preview.src = f"/{e.file_name}"
            image_preview.visible = True
            page.update()

    # Flet 1.0+ Service syntax (do NOT add to page.overlay)
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

    # --- Page Layout ---
    page.add(
        ft.Icon(ft.Icons.CLOUD_DONE, size=48, color=ft.Colors.BLUE),
        ft.Text("Flet Permanent Web App", size=22, weight=ft.FontWeight.BOLD),
        status_badge,
        ft.Divider(height=20),
        # Section A: Image Upload
        ft.Text("1. Image Upload & Live Preview", size=16, weight=ft.FontWeight.W_600),
        ft.Button(
            content="Pick & Upload Image",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=pick_and_upload,
        ),
        upload_status,
        image_preview,
        ft.Divider(height=20),
        # Section B: Live Text Sync
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
    # Render sets PORT automatically; defaults to 8550 locally
    port = int(os.environ.get("PORT", 8550))

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
        upload_dir=UPLOAD_FOLDER,
        assets_dir=UPLOAD_FOLDER,
    )

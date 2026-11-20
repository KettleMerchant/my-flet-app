import json
from pathlib import Path
import flet as ft

DATA_FILE = Path("components.json")

DEFAULT_COMPONENTS = [
    {
        "part_no": "IRLZ44N",
        "category": "MOSFET",
        "package": "TO-220",
        "specs": "55V, 47A, Logic-Level N-Channel, Rds(on) 22mΩ",
        "location": "Drawer A-01",
        "stock": 14,
        "notes": "Great for Arduino/ESP32 PWM motor and LED strip switching.",
        "datasheet": "https://www.infineon.com/dgdl/Infineon-IRLZ44N-DataSheet-v01_01-EN.pdf",
    },
    {
        "part_no": "NE555P",
        "category": "IC / Timer",
        "package": "DIP-8",
        "specs": "4.5V–16V, Precision Timer, up to 200mA output",
        "location": "Drawer B-03",
        "stock": 25,
        "notes": "Classic astable/monostable oscillator and PWM generator.",
        "datasheet": "https://www.ti.com/lit/ds/symlink/ne555.pdf",
    },
    {
        "part_no": "ESP32-WROOM-32",
        "category": "Microcontroller",
        "package": "SMD Module",
        "specs": "Dual-core 240MHz, Wi-Fi + BLE, 3.3V, 4MB Flash",
        "location": "Bin C-02",
        "stock": 3,
        "notes": "3.3V logic only; add 10µF cap on EN pin if flashing fails.",
        "datasheet": "https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf",
    },
    {
        "part_no": "LM7805",
        "category": "Voltage Regulator",
        "package": "TO-220",
        "specs": "5V Fixed Output, 1.5A max, 7V–35V Input",
        "location": "Drawer A-04",
        "stock": 9,
        "notes": "Use 0.33µF input and 0.1µF output decoupling capacitors.",
        "datasheet": "https://www.ti.com/lit/ds/symlink/lm340.pdf",
    },
    {
        "part_no": "2N2222A",
        "category": "Transistor",
        "package": "TO-92",
        "specs": "NPN BJT, 40V, 800mA, hFE 100–300",
        "location": "Drawer A-02",
        "stock": 42,
        "notes": "General-purpose low-side switch and small-signal amplifier.",
        "datasheet": "https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf",
    },
    {
        "part_no": "1N4148",
        "category": "Diode",
        "package": "DO-35",
        "specs": "100V, 200mA, Fast Switching (4ns)",
        "location": "Bin D-01",
        "stock": 0,
        "notes": "Fast signal diode; avoid using for high-current flyback.",
        "datasheet": "https://www.vishay.com/docs/81857/1n4148.pdf",
    },
    {
        "part_no": "LM358P",
        "category": "Op-Amp",
        "package": "DIP-8",
        "specs": "Dual Op-Amp, 3V–32V Single Supply, 1MHz GBW",
        "location": "Drawer B-05",
        "stock": 11,
        "notes": "Output swings near GND, not rail-to-rail on high side.",
        "datasheet": "https://www.ti.com/lit/ds/symlink/lm358.pdf",
    },
    {
        "part_no": "10kΩ 1/4W",
        "category": "Resistor",
        "package": "Axial (Through-Hole)",
        "specs": "10kΩ, ±1% Metal Film, 0.25W",
        "location": "Binder R-10K",
        "stock": 120,
        "notes": "Standard pull-up/pull-down and voltage divider resistor.",
        "datasheet": "",
    },
    {
        "part_no": "100µF 25V",
        "category": "Capacitor",
        "package": "Radial Electrolytic",
        "specs": "100µF, 25V, ±20%, 105°C",
        "location": "Bin C-08",
        "stock": 4,
        "notes": "Bulk power-rail decoupling; watch polarity stripe.",
        "datasheet": "",
    },
]


def load_components() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    save_components(DEFAULT_COMPONENTS)
    return list(DEFAULT_COMPONENTS)


def save_components(items: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def main(page: ft.Page):
    page.title = "Electronics Component Finder"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 1050
    page.window.height = 740

    components = load_components()

    # --- UI Controls ---
    search_field = ft.TextField(
        hint_text="Search by part number, specs, package, notes, or bin...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        on_change=lambda _: render_list(),
    )

    category_dropdown = ft.Dropdown(
        label="Category",
        value="All",
        width=210,
        on_select=lambda _: render_list(),
    )

    in_stock_switch = ft.Switch(
        label="In Stock Only",
        value=False,
        on_change=lambda _: render_list(),
    )

    count_text = ft.Text(size=13, color=ft.Colors.GREY_400)
    results_list = ft.ListView(expand=True, spacing=10)

    def refresh_categories():
        cats = sorted({c["category"] for c in components if c.get("category")})
        current = category_dropdown.value or "All"
        category_dropdown.options = [ft.dropdown.Option("All")] + [
            ft.dropdown.Option(cat) for cat in cats
        ]
        category_dropdown.value = current if current in ["All", *cats] else "All"

    def stock_badge(qty: int) -> ft.Container:
        if qty <= 0:
            bg, fg, label = ft.Colors.RED_900, ft.Colors.RED_200, "Out of Stock"
        elif qty <= 5:
            bg, fg, label = (
                ft.Colors.AMBER_900,
                ft.Colors.AMBER_200,
                f"Low Stock: {qty}",
            )
        else:
            bg, fg, label = ft.Colors.GREEN_900, ft.Colors.GREEN_200, f"In Stock: {qty}"

        return ft.Container(
            content=ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=fg),
            bgcolor=bg,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
        )

    # --- Component Detail Modal ---
    def open_detail_dialog(comp: dict):
        stock_label = ft.Text(str(comp["stock"]), size=18, weight=ft.FontWeight.BOLD)

        def adjust_stock(delta: int):
            comp["stock"] = max(0, comp["stock"] + delta)
            stock_label.value = str(comp["stock"])
            save_components(components)
            render_list()
            page.update()

        async def open_datasheet(_):
            if comp.get("datasheet"):
                await ft.UrlLauncher().launch_url(comp["datasheet"])

        def delete_component(_):
            components.remove(comp)
            save_components(components)
            refresh_categories()
            render_list()
            page.pop_dialog()

        actions = [
            ft.TextButton(
                content="Delete",
                style=ft.ButtonStyle(color=ft.Colors.RED_400),
                on_click=delete_component,
            ),
        ]
        if comp.get("datasheet"):
            actions.append(
                ft.Button(
                    content="Datasheet",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=open_datasheet,
                )
            )
        actions.append(
            ft.TextButton(content="Close", on_click=lambda _: page.pop_dialog())
        )

        dlg = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.MEMORY),
                    ft.Text(comp["part_no"], weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"Category: {comp['category']}", weight=ft.FontWeight.W_500
                    ),
                    ft.Text(f"Package: {comp['package']}"),
                    ft.Text(f"Location: {comp['location']}"),
                    ft.Divider(),
                    ft.Text("Specifications", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(comp["specs"]),
                    ft.Text("Notes", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(comp["notes"] or "No notes added."),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Text("Stock Quantity:", weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                on_click=lambda _: adjust_stock(-1),
                            ),
                            stock_label,
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                on_click=lambda _: adjust_stock(1),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                tight=True,
                width=460,
                spacing=8,
            ),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.show_dialog(dlg)

    # --- Add Component Modal ---
    def open_add_dialog(_):
        part_in = ft.TextField(label="Part Number *", autofocus=True)
        cat_in = ft.TextField(label="Category *", hint_text="e.g., MOSFET, Sensor, IC")
        pkg_in = ft.TextField(
            label="Package", hint_text="e.g., TO-220, SMD 0805, DIP-8"
        )
        specs_in = ft.TextField(label="Key Specs", hint_text="e.g., 3.3V, I2C, 55V 47A")
        loc_in = ft.TextField(
            label="Storage Bin / Drawer", hint_text="e.g., Drawer B-02"
        )
        stock_in = ft.TextField(
            label="Initial Stock", value="1", keyboard_type=ft.KeyboardType.NUMBER
        )
        notes_in = ft.TextField(label="Notes", multiline=True, min_lines=2)
        url_in = ft.TextField(label="Datasheet URL (optional)")
        error_text = ft.Text("", color=ft.Colors.RED_400, size=12)

        def save_new(_):
            if not part_in.value.strip() or not cat_in.value.strip():
                error_text.value = "Part Number and Category are required."
                page.update()
                return
            try:
                qty = max(0, int(stock_in.value.strip() or "0"))
            except ValueError:
                error_text.value = "Initial Stock must be a whole number."
                page.update()
                return

            components.insert(
                0,
                {
                    "part_no": part_in.value.strip(),
                    "category": cat_in.value.strip(),
                    "package": pkg_in.value.strip() or "N/A",
                    "specs": specs_in.value.strip() or "—",
                    "location": loc_in.value.strip() or "Unassigned",
                    "stock": qty,
                    "notes": notes_in.value.strip(),
                    "datasheet": url_in.value.strip(),
                },
            )
            save_components(components)
            refresh_categories()
            render_list()
            page.pop_dialog()

        dlg = ft.AlertDialog(
            title=ft.Text("Add Electronic Component"),
            content=ft.Column(
                [
                    part_in,
                    ft.Row([cat_in, pkg_in]),
                    specs_in,
                    ft.Row([loc_in, stock_in]),
                    notes_in,
                    url_in,
                    error_text,
                ],
                tight=True,
                width=500,
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
            actions=[
                ft.TextButton(content="Cancel", on_click=lambda _: page.pop_dialog()),
                ft.Button(
                    content="Save Component", icon=ft.Icons.SAVE, on_click=save_new
                ),
            ],
        )
        page.show_dialog(dlg)

    # --- Render Filtered Component Cards ---
    def render_list():
        query = (search_field.value or "").strip().lower()
        selected_cat = category_dropdown.value or "All"
        only_in_stock = in_stock_switch.value

        filtered = []
        for comp in components:
            if selected_cat != "All" and comp["category"] != selected_cat:
                continue
            if only_in_stock and comp["stock"] <= 0:
                continue
            searchable = " ".join(
                [
                    comp["part_no"],
                    comp["category"],
                    comp["package"],
                    comp["specs"],
                    comp["location"],
                    comp["notes"],
                ]
            ).lower()
            if query and query not in searchable:
                continue
            filtered.append(comp)

        count_text.value = f"Showing {len(filtered)} of {len(components)} components"
        results_list.controls.clear()

        if not filtered:
            results_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No matching components found. Try broadening your search or filters.",
                        color=ft.Colors.GREY_400,
                    ),
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                )
            )
        else:
            for comp in filtered:
                card = ft.Card(
                    content=ft.Container(
                        padding=14,
                        ink=True,
                        border_radius=10,
                        on_click=lambda _, c=comp: open_detail_dialog(c),
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text(
                                                    comp["part_no"],
                                                    size=16,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Container(
                                                    content=ft.Text(
                                                        comp["category"], size=11
                                                    ),
                                                    bgcolor=ft.Colors.BLUE_GREY_800,
                                                    padding=ft.Padding.symmetric(
                                                        horizontal=8, vertical=2
                                                    ),
                                                    border_radius=6,
                                                ),
                                                ft.Text(
                                                    f"• {comp['package']}",
                                                    size=12,
                                                    color=ft.Colors.GREY_400,
                                                ),
                                            ],
                                            spacing=8,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        ft.Text(comp["specs"], size=13),
                                    ],
                                    expand=True,
                                    spacing=4,
                                ),
                                ft.Column(
                                    [
                                        stock_badge(comp["stock"]),
                                        ft.Row(
                                            [
                                                ft.Icon(
                                                    ft.Icons.INVENTORY_2_OUTLINED,
                                                    size=14,
                                                    color=ft.Colors.GREY_400,
                                                ),
                                                ft.Text(
                                                    comp["location"],
                                                    size=12,
                                                    color=ft.Colors.GREY_400,
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=6,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    )
                )
                results_list.controls.append(card)

        page.update()

    # --- Theme Toggle ---
    def toggle_theme(_):
        page.theme_mode = (
            ft.ThemeMode.LIGHT
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        page.update()

    header = ft.Row(
        [
            ft.Row(
                [
                    ft.Icon(
                        ft.Icons.DEVELOPER_BOARD, size=30, color=ft.Colors.CYAN_400
                    ),
                    ft.Text(
                        "Electronics Component Finder",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.BRIGHTNESS_6,
                        tooltip="Toggle Light/Dark Theme",
                        on_click=toggle_theme,
                    ),
                    ft.Button(
                        content="Add Component",
                        icon=ft.Icons.ADD,
                        on_click=open_add_dialog,
                    ),
                ],
                spacing=8,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    filter_bar = ft.Row(
        [search_field, category_dropdown, in_stock_switch],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    refresh_categories()
    page.add(header, ft.Divider(height=10), filter_bar, count_text, results_list)
    render_list()


if __name__ == "__main__":
    ft.run(main)

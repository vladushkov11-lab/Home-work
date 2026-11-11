import customtkinter as ctk

from lighting.model import HouseLighting, RoomState


BACKGROUND = "#10151F"
PANEL = "#191F2C"
BORDER = "#303A4B"
TEXT = "#F2F4F8"
MUTED = "#ABB6C9"
ACCENT = "#F4BF62"
FONT = "Segoe UI"


def label(master, text: str, size: int = 14, **kwargs) -> ctk.CTkLabel:
    """Единое оформление подписей без повторения настроек в каждом виджете."""
    return ctk.CTkLabel(
        master, text=text, font=(FONT, size), text_color=TEXT, **kwargs
    )


class RoomCard(ctk.CTkFrame):
    """Карточка этажа с лампой и текстовым обозначением состояния."""

    def __init__(self, master, room: RoomState) -> None:
        super().__init__(
            master, fg_color=PANEL, corner_radius=18,
            border_width=1, border_color=BORDER,
        )
        self.grid_columnconfigure(1, weight=1)
        self.floor = room.floor

        number = label(self, f"{room.floor:02}", 30, width=60)
        number.configure(text_color=MUTED)
        number.grid(row=0, column=0, rowspan=2, padx=(18, 12), pady=24)

        label(self, room.name, 21, anchor="w").grid(
            row=0, column=1, sticky="sw", pady=(22, 0)
        )
        self.status = label(self, "", 13, anchor="w")
        self.status.grid(row=1, column=1, sticky="nw", pady=(2, 22))

        self.window = ctk.CTkFrame(
            self, width=126, height=96, corner_radius=14,
            fg_color="#202A3A", border_width=1, border_color=BORDER,
        )
        self.window.grid(row=0, column=2, rowspan=2, padx=20, pady=18)
        self.window.grid_propagate(False)
        self.cord = ctk.CTkFrame(
            self.window, width=2, height=23, corner_radius=0, fg_color=MUTED
        )
        self.cord.place(relx=0.5, y=0, anchor="n")
        self.halo = ctk.CTkFrame(
            self.window, width=68, height=68, corner_radius=34,
            fg_color="#273346",
        )
        self.halo.place(relx=0.5, rely=0.56, anchor="center")
        self.bulb = ctk.CTkFrame(
            self.halo, width=34, height=34, corner_radius=17,
            fg_color="#5C6B81",
        )
        self.bulb.place(relx=0.5, rely=0.5, anchor="center")
        self.render(room)

    def render(self, room: RoomState) -> None:
        """Обновляем и цвет лампы, и подпись: состояние понятно без цвета."""
        self.status.configure(
            text=f"{room.floor} этаж  /  Свет {'включён' if room.is_on else 'выключен'}",
            text_color=ACCENT if room.is_on else MUTED,
        )
        self.configure(border_color="#82623B" if room.is_on else BORDER)
        self.window.configure(fg_color="#443523" if room.is_on else "#202A3A")
        self.halo.configure(fg_color="#765831" if room.is_on else "#273346")
        self.bulb.configure(fg_color="#FFE4A3" if room.is_on else "#5C6B81")


class LightingApp(ctk.CTk):
    """Окно приложения. Выбор радиокнопки меняет общую модель дома."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        super().__init__()
        self.title("Три этажа — управление светом")
        self.geometry("1040x720")
        self.minsize(940, 720)
        self.configure(fg_color=BACKGROUND)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.house = HouseLighting()
        self.light_value = ctk.IntVar(master=self, value=0)

        self._build_header()
        self._build_content()
        footer = label(
            self,
            "CUSTOMTKINTER   /   Радиокнопки   /   Один пульт — три комнаты",
            12,
        )
        footer.configure(text_color=MUTED)
        footer.grid(row=2, column=0, sticky="w", padx=32, pady=(14, 20))
        self._render()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 22))
        header.grid_columnconfigure(0, weight=1)
        label(header, "Три этажа. Один выбор.", 32, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        subtitle = label(header, "Общее управление освещением дома", 14)
        subtitle.configure(text_color=MUTED)
        subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.counter = label(
            header, "", 14, width=164, height=40, corner_radius=12,
            fg_color=PANEL,
        )
        self.counter.grid(row=0, column=1, rowspan=2, padx=(16, 0))

    def _build_content(self) -> None:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=32)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        control = ctk.CTkFrame(
            content, width=290, fg_color=PANEL, corner_radius=18,
            border_width=1, border_color=BORDER,
        )
        control.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        control.grid_propagate(False)
        control.grid_columnconfigure(0, weight=1)
        control.grid_rowconfigure(5, weight=1)

        eyebrow = label(control, "ПУЛЬТ  /  1 ЭТАЖ", 12, anchor="w")
        eyebrow.configure(text_color=ACCENT)
        eyebrow.grid(row=0, column=0, sticky="ew", padx=24, pady=(26, 12))
        label(control, "Освещение", 25, anchor="w").grid(
            row=1, column=0, sticky="ew", padx=24
        )
        description = label(
            control, "Выбери состояние.\nВсе три комнаты изменятся\nодновременно.",
            14, anchor="w", justify="left",
        )
        description.configure(text_color=MUTED)
        description.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 26))

        options = {"Свет выключен": 0, "Свет включён": 1}
        self.radios: dict[int, ctk.CTkRadioButton] = {}
        for row, (text, value) in enumerate(options.items(), start=3):
            radio = ctk.CTkRadioButton(
                control, text=text, variable=self.light_value, value=value,
                command=self._apply_selection, font=(FONT, 16),
                text_color=TEXT, fg_color=ACCENT, hover_color="#D69A40",
                border_color=MUTED, radiobutton_width=24, radiobutton_height=24,
                height=42,
            )
            radio.grid(row=row, column=0, sticky="w", padx=24, pady=(0, 10))
            self.radios[value] = radio

        self.summary = label(
            control, "", 15, anchor="w", justify="left", wraplength=240,
        )
        self.summary.grid(row=6, column=0, sticky="ew", padx=24, pady=(12, 12))
        hint = label(control, "Клавиши: 1 — включить\n0 — выключить", 12,
                        anchor="w", justify="left")
        hint.configure(text_color=MUTED)
        hint.grid(row=7, column=0, sticky="ew", padx=24, pady=(0, 24))

        floors = ctk.CTkFrame(content, fg_color="transparent")
        floors.grid(row=0, column=1, sticky="nsew")
        floors.grid_columnconfigure(0, weight=1)
        self.room_cards: dict[int, RoomCard] = {}
        for index, room in enumerate(reversed(self.house.rooms)):
            floors.grid_rowconfigure(index, weight=1, uniform="floors")
            card = RoomCard(floors, room)
            card.grid(row=index, column=0, sticky="nsew",
                        pady=(0, 14 if index < 2 else 0))
            self.room_cards[room.floor] = card


        self.bind("1", lambda _event: self.radios[1].invoke())
        self.bind("0", lambda _event: self.radios[0].invoke())

    def _apply_selection(self) -> None:
        self.house.set_lights(self.light_value.get() == 1)
        self._render()

    def _render(self) -> None:
        for room in self.house.rooms:
            self.room_cards[room.floor].render(room)
        self.counter.configure(
            text=f"Горит {self.house.lit_count} из {len(self.house.rooms)}",
            text_color=ACCENT if self.house.is_on else MUTED,
        )
        self.summary.configure(
            text="Свет включён\nна всех этажах." if self.house.is_on
            else "Свет выключен\nна всех этажах.",
            text_color=ACCENT if self.house.is_on else MUTED,
        )

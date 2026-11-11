from time import perf_counter

import customtkinter as ctk

from lamp_puzzle.model import LampObservation, LampPuzzle, Phase


BG = "#10151F"
PANEL = "#191F2C"
BORDER = "#303A4B"
TEXT = "#F2F4F8"
MUTED = "#ABB6C9"
ACCENT = "#F4BF62"
GREEN = "#92D7B0"
RED = "#F49B9B"
FONT = "Segoe UI"


def label(master, text: str, size: int = 14, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(master, text=text, text_color=TEXT,
                        font=(FONT, size), **kwargs)


class LampCard(ctk.CTkFrame):
    """До входа карточка не раскрывает ни свет, ни температуру лампы."""

    def __init__(self, master, number: int) -> None:
        super().__init__(master, fg_color=PANEL, corner_radius=16,
                            border_width=1, border_color=BORDER)
        self.grid_columnconfigure(1, weight=1)
        self.halo = ctk.CTkFrame(self, width=66, height=66, corner_radius=33,
                                fg_color="#273346")
        self.halo.grid(row=0, column=0, rowspan=3, padx=20, pady=18)
        self.bulb = ctk.CTkFrame(self.halo, width=32, height=32, corner_radius=16,
                                fg_color="#536078")
        self.bulb.place(relx=0.5, rely=0.5, anchor="center")
        label(self, f"Лампа {number}", 19, anchor="w").grid(
            row=0, column=1, sticky="ew", pady=(15, 0))
        self.status = label(self, "", 13, anchor="w")
        self.status.grid(row=1, column=1, sticky="ew")
        self.temperature = label(self, "", 13, anchor="w")
        self.temperature.grid(row=2, column=1, sticky="ew", pady=(0, 15))
        self.choice = ctk.CTkOptionMenu(
            self, values=["Выключатель 1", "Выключатель 2", "Выключатель 3"],
            width=172, height=36, font=(FONT, 13), fg_color="#283447",
            button_color="#36465F", button_hover_color="#475D7D",
            dropdown_fg_color=PANEL, dropdown_text_color=TEXT,
        )
        self.choice.grid(row=0, column=2, rowspan=3, padx=(12, 20))
        self.hide()

    def hide(self) -> None:
        self.configure(border_color=BORDER)
        self.status.configure(text="Состояние скрыто", text_color=MUTED)
        self.temperature.configure(text="Температура: неизвестна", text_color=MUTED)
        self.halo.configure(fg_color="#273346")
        self.bulb.configure(fg_color="#536078")
        self.choice.set("Выбери выключатель")
        self.choice.configure(state="disabled")

    def reveal(self, observation: LampObservation) -> None:
        self.status.configure(text="Горит" if observation.is_on else "Не горит",
                                text_color=ACCENT if observation.is_on else TEXT)
        self.temperature.configure(
            text=f"{observation.temperature:.1f} °C  /  {observation.thermal_state}",
            text_color=ACCENT if observation.temperature >= 30 else MUTED,
        )
        self.bulb.configure(fg_color="#FFE4A3" if observation.is_on else "#536078")
        self.halo.configure(fg_color="#765831" if observation.is_on else "#273346")
        self.configure(border_color="#82623B" if observation.is_on else BORDER)
        self.choice.configure(state="normal")


class PuzzleApp(ctk.CTk):
    """Время идёт до входа; затем сохраняется снимок для решения загадки."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        super().__init__()
        self.title("Три лампы — один вход")
        self.geometry("1120x740")
        self.minsize(1060, 720)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.puzzle = LampPuzzle()
        self._last_tick = perf_counter()
        self._timer_id: str | None = None
        self._build_header()
        self._build_content()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._refresh_clock()
        self._timer_id = self.after(200, self._tick)

    def _build_header(self) -> None:
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 20))
        head.grid_columnconfigure(0, weight=1)
        label(head, "Три лампы. Один вход.", 30, anchor="w").grid(row=0, column=0, sticky="w")
        subtitle = label(head, "Выясни, какой выключатель управляет каждой лампой", 14)
        subtitle.configure(text_color=MUTED)
        subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.entry_badge = label(head, "Входов осталось: 1", 14, width=175, height=38,
                                    fg_color=PANEL, corner_radius=12)
        self.entry_badge.grid(row=0, column=1, rowspan=2, padx=(12, 0))

    def _build_content(self) -> None:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 22))
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        control = ctk.CTkFrame(content, width=300, fg_color=PANEL,
                                corner_radius=18, border_width=1, border_color=BORDER)
        control.grid(row=0, column=0, sticky="ns", padx=(0, 18))
        control.grid_propagate(False)
        control.grid_columnconfigure(0, weight=1)
        label(control, "КОРИДОР", 12, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=22, pady=(22, 10))
        label(control, "Выключатели", 23, anchor="w").grid(
            row=1, column=0, sticky="ew", padx=22, pady=(0, 12))
        self.switch_vars = [ctk.IntVar(master=self, value=0) for _ in range(3)]
        self.switch_widgets = []
        for index, variable in enumerate(self.switch_vars):
            switch = ctk.CTkSwitch(
                control, text=f"Выключатель {index + 1}", variable=variable,
                command=lambda number=index + 1: self._change_switch(number),
                font=(FONT, 16), text_color=TEXT, progress_color=ACCENT,
                button_color="#F2F4F8", button_hover_color="#D8DEEA", height=40,
            )
            switch.grid(row=index + 2, column=0, sticky="w", padx=22, pady=5)
            self.switch_widgets.append(switch)
        self.clock = label(control, "", 14, anchor="w")
        self.clock.grid(row=5, column=0, sticky="ew", padx=22, pady=(16, 10))
        wait = ctk.CTkFrame(control, fg_color="transparent")
        wait.grid(row=6, column=0, sticky="ew", padx=22)
        wait.grid_columnconfigure((0, 1), weight=1)
        self.wait_buttons = []
        for column, seconds in enumerate((30, 60)):
            button = ctk.CTkButton(
                wait, text=f"+ {seconds} секунд", width=112, height=34,
                fg_color="#2A364A", hover_color="#3B4D68", text_color=TEXT,
                command=lambda value=seconds: self._wait(value),
            )
            button.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
            self.wait_buttons.append(button)
        note = label(control, "Время идёт само. Кнопки\nускоряют ожидание.", 12,
                        anchor="w", justify="left")
        note.configure(text_color=MUTED)
        note.grid(row=7, column=0, sticky="ew", padx=22, pady=(9, 18))
        self.enter_button = ctk.CTkButton(
            control, text="Войти в комнату", height=42, font=(FONT, 15, "bold"),
            fg_color=ACCENT, hover_color="#DCA348", text_color="#20190F",
            command=self._enter,
        )
        self.enter_button.grid(row=8, column=0, sticky="ew", padx=22)
        self.hint_button = ctk.CTkButton(
            control, text="Показать подсказку", fg_color="transparent",
            hover_color="#283447", text_color=MUTED, command=self._show_hint,
        )
        self.hint_button.grid(row=9, column=0, sticky="ew", padx=22, pady=(10, 3))
        self.hint = label(control, "Лампы накаливания\nсохраняют тепло после\nвыключения.", 12,
                            anchor="w", justify="left", wraplength=250)
        self.hint.configure(text_color=MUTED)
        self.hint.grid(row=10, column=0, sticky="ew", padx=22, pady=(0, 18))

        room = ctk.CTkFrame(content, fg_color="transparent")
        room.grid(row=0, column=1, sticky="nsew")
        room.grid_columnconfigure(0, weight=1)
        self.room_title = label(room, "Комната закрыта", 21, anchor="w")
        self.room_title.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        self.room_note = label(room, "До входа свет и температура ламп скрыты.", 13, anchor="w")
        self.room_note.configure(text_color=MUTED)
        self.room_note.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.cards = [LampCard(room, number) for number in (1, 2, 3)]
        for row, card in enumerate(self.cards, start=2):
            card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.check_button = ctk.CTkButton(
            room, text="Проверить соответствие", height=38, state="disabled",
            fg_color="#2E4661", hover_color="#3D5D80", command=self._submit,
        )
        self.check_button.grid(row=5, column=0, sticky="ew", pady=(2, 8))
        self.feedback = label(room, "Сначала подготовь выключатели, затем войди.", 13,
                                anchor="w", justify="left", wraplength=650)
        self.feedback.configure(text_color=MUTED)
        self.feedback.grid(row=6, column=0, sticky="ew")
        room.grid_rowconfigure(7, weight=1)
        ctk.CTkButton(room, text="Новая попытка", width=150,
                        fg_color="transparent", border_width=1, border_color=BORDER,
                        hover_color=PANEL, text_color=TEXT, command=self._reset).grid(
                        row=8, column=0, sticky="e", pady=(12, 0))

    def _sync_time(self) -> None:
        now = perf_counter()
        if self.puzzle.phase is Phase.PREPARING:
            self.puzzle.advance(max(0.0, now - self._last_tick))
        self._last_tick = now

    def _refresh_clock(self) -> None:
        total = int(self.puzzle.elapsed)
        self.clock.configure(text=f"Модельное время: {total // 60:02}:{total % 60:02}")

    def _tick(self) -> None:
        self._sync_time()
        self._refresh_clock()
        self._timer_id = self.after(200, self._tick)

    def _change_switch(self, number: int) -> None:
        self._sync_time()
        self.puzzle.set_switch(number, self.switch_vars[number - 1].get() == 1)

    def _wait(self, seconds: int) -> None:
        self._sync_time()
        self.puzzle.advance(seconds)
        self._refresh_clock()

    def _enter(self) -> None:
        self._sync_time()
        for card, observation in zip(self.cards, self.puzzle.enter_room()):
            card.reveal(observation)
        for widget in self.switch_widgets + self.wait_buttons + [self.enter_button]:
            widget.configure(state="disabled")
        self.check_button.configure(state="normal")
        self.entry_badge.configure(text="Входов осталось: 0", text_color=ACCENT)
        self.room_title.configure(text="Ты в комнате")
        self.room_note.configure(text="Снимок на момент входа: время и температуры зафиксированы.")
        self.feedback.configure(text="Укажи выключатель для каждой лампы. Проверка ответа одна.",
                                text_color=TEXT)
        self._refresh_clock()

    def _submit(self) -> None:
        choices = [card.choice.get() for card in self.cards]
        if any(value not in ("Выключатель 1", "Выключатель 2", "Выключатель 3") for value in choices):
            self.feedback.configure(text="Выбери выключатель для каждой из трёх ламп.", text_color=RED)
            return
        answer = tuple(int(value[-1]) for value in choices)
        try:
            correct = self.puzzle.submit(answer)
        except ValueError as error:
            self.feedback.configure(text=str(error), text_color=RED)
            return
        actual = ";  ".join(f"лампа {lamp} → выкл. {switch}"
                                for lamp, switch in enumerate(self.puzzle.solution, start=1))
        self.feedback.configure(
            text=("Верно! " if correct else "Ответ не совпал. ") + "Проводка:\n" + actual,
            text_color=GREEN if correct else RED,
        )
        self.check_button.configure(state="disabled")
        for card in self.cards:
            card.choice.configure(state="disabled")

    def _show_hint(self) -> None:
        self.hint.configure(text="Включи №1, подожди 60 с.\nВыключи №1, включи №2.\nВойди: горит — №2,\nтёплая — №1, холодная — №3.")
        self.hint_button.configure(state="disabled")

    def _reset(self) -> None:
        self.puzzle = LampPuzzle()
        self._last_tick = perf_counter()
        for variable, switch in zip(self.switch_vars, self.switch_widgets):
            variable.set(0)
            switch.configure(state="normal")
        for button in self.wait_buttons + [self.enter_button, self.hint_button]:
            button.configure(state="normal")
        for card in self.cards:
            card.hide()
        self.check_button.configure(state="disabled")
        self.entry_badge.configure(text="Входов осталось: 1", text_color=TEXT)
        self.room_title.configure(text="Комната закрыта")
        self.room_note.configure(text="До входа свет и температура ламп скрыты.")
        self.feedback.configure(text="Сначала подготовь выключатели, затем войди.", text_color=MUTED)
        self.hint.configure(text="Лампы накаливания\nсохраняют тепло после\nвыключения.")
        self._refresh_clock()

    def destroy(self) -> None:
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        super().destroy()

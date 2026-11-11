"""Локальная проверка геометрии и снимки собственного тестируемого окна."""

import sys
from pathlib import Path

from PIL import ImageGrab

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'hpwe_work_1'))

from lighting.app import LightingApp


app = LightingApp()
errors = []
app.report_callback_exception = lambda *args: errors.append(str(args))


def capture(name):
    app.update_idletasks()
    x, y = app.winfo_rootx(), app.winfo_rooty()
    ImageGrab.grab(bbox=(x, y, x + app.winfo_width(), y + app.winfo_height())).save(
        ROOT / '.qa' / f'{name}.png'
    )
    for card in app.room_cards.values():
        assert card.winfo_height() >= 130
        assert card.winfo_width() >= 400
        for widget in (card.window, card.status):
            assert widget.winfo_x() + widget.winfo_width() <= card.winfo_width()
            assert widget.winfo_y() + widget.winfo_height() <= card.winfo_height()


def check_on():
    capture('lights-off')
    app.radios[1].invoke()
    app.after(350, check_minimum)


def check_minimum():
    capture('lights-on')
    app.geometry('940x720')
    app.after(350, finish)


def finish():
    try:
        capture('lights-minimum')
        assert app.house.lit_count == 3
        app.focus_force()
        app.update()
        for key in ('0', '1'):
            app.event_generate(f'<KeyPress-{key}>')
            app.update()
            assert app.house.lit_count == int(key) * 3
        assert not errors, errors
        print('GUI: off/on/minimum size/keyboard checked; no callback errors')
    finally:
        app.destroy()


app.after(450, check_on)
app.mainloop()

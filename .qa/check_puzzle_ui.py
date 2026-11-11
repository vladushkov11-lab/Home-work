"""Проверка размеров и снимки собственного окна второй задачи."""

import sys
from pathlib import Path

from PIL import ImageGrab

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'home_work_2'))

from lamp_puzzle.app import PuzzleApp
from lamp_puzzle.model import LampPuzzle

app = PuzzleApp()
app.attributes('-topmost', True)
app.geometry('1060x720')
app.puzzle = LampPuzzle((3, 1, 2))
errors = []
app.report_callback_exception = lambda *args: errors.append(str(args))


def capture(name):
    app.update_idletasks()
    x, y = app.winfo_rootx(), app.winfo_rooty()
    ImageGrab.grab(bbox=(x, y, x + app.winfo_width(), y + app.winfo_height())).save(
        ROOT / '.qa' / f'{name}.png'
    )
    for card in app.cards:
        assert card.choice.winfo_x() + card.choice.winfo_width() <= card.winfo_width()
    hint = app.hint
    assert hint.winfo_y() + hint.winfo_height() <= hint.master.winfo_height()


def prepare():
    capture('puzzle-closed')
    app.switch_widgets[0].toggle()
    app._wait(60)
    app.switch_widgets[0].toggle()
    app.switch_widgets[1].toggle()
    app._show_hint()
    app.enter_button.invoke()
    app.after(300, solve)


def solve():
    capture('puzzle-entered')
    for card, number in zip(app.cards, (2, 3, 1)):
        card.choice.set(f'Выключатель {number}')
    app.check_button.invoke()
    app.after(300, finish)


def finish():
    try:
        capture('puzzle-solved')
        assert app.feedback.cget('text').startswith('Верно!')
        assert not errors, errors
        print('GUI checked: hidden room, entry, hint, correct answer, minimum size')
    finally:
        app.destroy()


app.after(500, prepare)
app.mainloop()

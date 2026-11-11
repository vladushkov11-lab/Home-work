import os
import sys

import pytest

from lamp_puzzle.app import PuzzleApp
from lamp_puzzle.model import LampPuzzle, Phase


@pytest.fixture(scope="module")
def window():
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        pytest.skip("Для GUI-тестов нужен графический экран DISPLAY.")
    instance = PuzzleApp()
    instance.withdraw()
    try:
        yield instance
    finally:
        instance.destroy()


@pytest.fixture
def app(window):
    window._reset()
    window.puzzle = LampPuzzle((3, 1, 2))
    return window


def test_closed_room_does_not_reveal_state_or_temperature(app):
    app.switch_widgets[0].toggle()
    app._wait(60)
    assert app.puzzle.switches == (True, False, False)
    for card in app.cards:
        assert card.status.cget("text") == "Состояние скрыто"
        assert card.temperature.cget("text") == "Температура: неизвестна"
        assert card.choice.cget("state") == "disabled"


def test_complete_solution_through_real_widgets(app):
    app.switch_widgets[0].toggle()
    app._wait(60)
    app.switch_widgets[0].toggle()
    app.switch_widgets[1].toggle()
    app.enter_button.invoke()
    assert app.puzzle.phase is Phase.OBSERVING
    assert app.entry_badge.cget("text") == "Входов осталось: 0"
    assert app.cards[0].status.cget("text") == "Горит"
    assert "Горячая" in app.cards[2].temperature.cget("text")
    assert all(switch.cget("state") == "disabled" for switch in app.switch_widgets)
    assert app.enter_button.cget("state") == "disabled"
    for card, switch in zip(app.cards, (2, 3, 1)):
        card.choice.set(f"Выключатель {switch}")
    app.check_button.invoke()
    assert app.puzzle.phase is Phase.FINISHED
    assert app.feedback.cget("text").startswith("Верно!")


def test_duplicate_choices_allow_correction_without_losing_attempt(app):
    app.enter_button.invoke()
    for card in app.cards:
        card.choice.set("Выключатель 1")
    app.check_button.invoke()
    assert app.puzzle.phase is Phase.OBSERVING
    assert "без повторений" in app.feedback.cget("text")


def test_reset_closes_room_clears_choices_and_restores_controls(app):
    app.enter_button.invoke()
    app._show_hint()
    app._reset()
    assert app.puzzle.phase is Phase.PREPARING
    assert app.puzzle.switches == (False, False, False)
    assert app.entry_badge.cget("text") == "Входов осталось: 1"
    assert app.enter_button.cget("state") == "normal"
    assert app.check_button.cget("state") == "disabled"
    assert all(card.choice.get() == "Выбери выключатель" for card in app.cards)

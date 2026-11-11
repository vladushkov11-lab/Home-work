import os
import sys

import pytest

from lighting.app import LightingApp


@pytest.fixture(scope="module")
def window():
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        pytest.skip("Для GUI-тестов на Linux нужен графический экран DISPLAY.")
    instance = LightingApp()
    instance.withdraw()
    try:
        yield instance
    finally:
        instance.destroy()


@pytest.fixture
def app(window):
    window.radios[0].invoke()
    return window


def test_initial_view_matches_dark_rooms(app):
    assert app.light_value.get() == 0
    assert app.counter.cget("text") == "Горит 0 из 3"
    assert set(app.room_cards) == {1, 2, 3}
    assert all("Свет выключен" in card.status.cget("text")
                for card in app.room_cards.values())


def test_radio_click_updates_model_and_every_room(app):
    for value in (1, 0, 1):
        app.radios[value].invoke()
        assert app.light_value.get() == value
        assert app.house.lit_count == value * 3
        assert app.counter.cget("text") == f"Горит {value * 3} из 3"
        status = "Свет включён" if value else "Свет выключен"
        for card in app.room_cards.values():
            assert status in card.status.cget("text")


def test_repeated_radio_click_keeps_the_selected_state(app):
    app.radios[1].invoke()
    app.radios[1].invoke()
    assert app.light_value.get() == 1
    assert app.house.lit_count == 3

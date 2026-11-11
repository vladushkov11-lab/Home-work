import pytest

from lighting.model import HouseLighting


def test_initially_all_rooms_are_dark():
    house = HouseLighting()
    assert not house.is_on
    assert house.lit_count == 0
    assert [room.floor for room in house.rooms] == [1, 2, 3]
    assert all(not room.is_on for room in house.rooms)


def test_one_command_lights_all_three_floors():
    house = HouseLighting()
    house.set_lights(True)
    assert house.is_on
    assert house.lit_count == 3
    assert all(room.is_on for room in house.rooms)


def test_switching_off_extinguishes_every_room():
    house = HouseLighting()
    house.set_lights(True)
    house.set_lights(False)
    assert house.lit_count == 0
    assert all(not room.is_on for room in house.rooms)


@pytest.mark.parametrize("enabled", [True, False])
def test_repeating_the_same_selection_does_not_toggle_lights(enabled):
    house = HouseLighting()
    house.set_lights(enabled)
    house.set_lights(enabled)
    assert all(room.is_on is enabled for room in house.rooms)


def test_rooms_stay_synchronised_through_multiple_changes():
    house = HouseLighting()
    for enabled in [True, False, True, True, False, False, True]:
        house.set_lights(enabled)
        assert house.lit_count == (3 if enabled else 0)
        assert all(room.is_on is enabled for room in house.rooms)


@pytest.mark.parametrize("invalid", [None, 0, 1, "on", [], {}])
def test_invalid_state_is_rejected_without_changing_the_house(invalid):
    house = HouseLighting()
    house.set_lights(True)
    with pytest.raises(TypeError, match="bool"):
        house.set_lights(invalid)
    assert house.lit_count == 3


def test_old_room_snapshot_does_not_change_after_switching():
    house = HouseLighting()
    previous_rooms = house.rooms
    house.set_lights(True)
    assert all(not room.is_on for room in previous_rooms)
    assert all(room.is_on for room in house.rooms)

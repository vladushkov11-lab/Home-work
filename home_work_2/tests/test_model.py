from itertools import permutations

import pytest

from lamp_puzzle.model import LampObservation, LampPuzzle, Phase


def test_new_game_is_closed_and_every_switch_is_off():
    puzzle = LampPuzzle()
    assert puzzle.phase is Phase.PREPARING
    assert puzzle.switches == (False, False, False)
    assert puzzle.elapsed == 0
    with pytest.raises(RuntimeError, match="скрыты"):
        _ = puzzle.observations
    with pytest.raises(RuntimeError, match="после проверки"):
        _ = puzzle.solution


@pytest.mark.parametrize("wiring", list(permutations((1, 2, 3))))
def test_temperature_strategy_solves_every_possible_wiring(wiring):
    puzzle = LampPuzzle(wiring)
    puzzle.set_switch(1, True)
    puzzle.advance(60)
    puzzle.set_switch(1, False)
    puzzle.set_switch(2, True)
    observations = puzzle.enter_room()
    answer = tuple(2 if lamp.is_on else 1 if lamp.temperature >= 30 else 3
                    for lamp in observations)
    assert sum(lamp.is_on for lamp in observations) == 1
    assert puzzle.submit(answer)
    assert puzzle.phase is Phase.FINISHED
    assert puzzle.solution == answer


def test_heating_is_gradual_and_cooling_is_slower():
    puzzle = LampPuzzle((1, 2, 3))
    puzzle.set_switch(1, True)
    puzzle.advance(60)
    puzzle.set_switch(1, False)
    puzzle.advance(30)
    warm, *cold = puzzle.enter_room()
    assert 50 < warm.temperature < 70
    assert not warm.is_on
    assert all(lamp.temperature == puzzle.AMBIENT for lamp in cold)


def test_heat_stays_bounded_and_eventually_dissipates():
    puzzle = LampPuzzle((1, 2, 3))
    puzzle.set_switch(1, True)
    puzzle.advance(100_000)
    puzzle.set_switch(1, False)
    puzzle.advance(100_000)
    lamp = puzzle.enter_room()[0]
    assert lamp.temperature == pytest.approx(puzzle.AMBIENT)


def test_one_long_interval_matches_many_small_intervals():
    single, many = LampPuzzle((1, 2, 3)), LampPuzzle((1, 2, 3))
    for puzzle in (single, many):
        puzzle.set_switch(1, True)
    single.advance(60)
    for _ in range(120):
        many.advance(0.5)
    assert single.enter_room()[0].temperature == pytest.approx(many.enter_room()[0].temperature)


def test_entry_is_single_and_freezes_observations():
    puzzle = LampPuzzle((1, 2, 3))
    observation = puzzle.enter_room()
    with pytest.raises(RuntimeError, match="один раз"):
        puzzle.enter_room()
    with pytest.raises(RuntimeError, match="возвращаться"):
        puzzle.set_switch(1, True)
    with pytest.raises(RuntimeError, match="зафиксированы"):
        puzzle.advance(30)
    assert puzzle.observations == observation


def test_wrong_answer_finishes_attempt_and_reveals_actual_wiring():
    puzzle = LampPuzzle((3, 1, 2))
    puzzle.enter_room()
    assert puzzle.submit((1, 2, 3)) is False
    assert puzzle.solution == (2, 3, 1)
    with pytest.raises(RuntimeError, match="один раз"):
        puzzle.submit((2, 3, 1))


def test_answer_before_entry_is_forbidden():
    with pytest.raises(RuntimeError, match="после входа"):
        LampPuzzle().submit((1, 2, 3))


@pytest.mark.parametrize("invalid", [(1, 1, 3), (0, 2, 3), (1, 2), (True, 2, 3)])
def test_invalid_answer_does_not_consume_attempt(invalid):
    puzzle = LampPuzzle((1, 2, 3))
    puzzle.enter_room()
    with pytest.raises(ValueError):
        puzzle.submit(invalid)
    assert puzzle.phase is Phase.OBSERVING
    assert puzzle.submit((1, 2, 3))


@pytest.mark.parametrize("invalid", [-1, float("nan"), float("inf"), True, "60"])
def test_invalid_time_changes_nothing(invalid):
    puzzle = LampPuzzle()
    with pytest.raises(ValueError):
        puzzle.advance(invalid)
    assert puzzle.elapsed == 0


@pytest.mark.parametrize("invalid", [(1, 1, 3), (1, 2, 4), (), (True, 2, 3)])
def test_invalid_wiring_is_rejected(invalid):
    with pytest.raises(ValueError):
        LampPuzzle(invalid)


@pytest.mark.parametrize("temperature, expected", [(22, "Холодная"), (30, "Тёплая"), (50, "Горячая")])
def test_temperature_labels_have_defined_thresholds(temperature, expected):
    assert LampObservation(1, False, temperature).thermal_state == expected

import math
import random
from dataclasses import dataclass
from enum import Enum, auto


class Phase(Enum):
    PREPARING = auto()
    OBSERVING = auto()
    FINISHED = auto()


@dataclass(frozen=True)
class LampObservation:
    number: int
    is_on: bool
    temperature: float

    @property
    def thermal_state(self) -> str:
        if self.temperature >= 50:
            return "Горячая"
        if self.temperature >= 30:
            return "Тёплая"
        return "Холодная"


class LampPuzzle:
    """Один вход, случайная проводка и фиксация наблюдений при открытии двери."""

    AMBIENT = 22.0
    HOT = 85.0
    HEATING_TAU = 45.0
    COOLING_TAU = 120.0

    def __init__(self, wiring: tuple[int, int, int] | None = None) -> None:
        # Позиция — номер выключателя минус один, значение — номер лампы.
        chosen = tuple(random.sample((1, 2, 3), 3)) if wiring is None else wiring
        self._validate_permutation(chosen)
        self._wiring = tuple(chosen)
        self._switches = [False, False, False]
        self._temperatures = [self.AMBIENT] * 3
        self._phase = Phase.PREPARING
        self._elapsed = 0.0
        self._observations: tuple[LampObservation, ...] = ()

    @staticmethod
    def _validate_permutation(values: tuple[int, ...]) -> None:
        if (len(values) != 3 or any(type(value) is not int for value in values)
                or set(values) != {1, 2, 3}):
            raise ValueError("Нужны номера 1, 2, 3 без повторений.")

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def elapsed(self) -> float:
        return self._elapsed

    @property
    def switches(self) -> tuple[bool, ...]:
        return tuple(self._switches)

    @property
    def observations(self) -> tuple[LampObservation, ...]:
        if self._phase is Phase.PREPARING:
            raise RuntimeError("Лампы скрыты за закрытой дверью.")
        return self._observations

    @property
    def solution(self) -> tuple[int, ...]:
        """Для каждой лампы возвращаем её выключатель, только после ответа."""
        if self._phase is not Phase.FINISHED:
            raise RuntimeError("Проводка раскрывается только после проверки ответа.")
        return tuple(self._wiring.index(lamp) + 1 for lamp in (1, 2, 3))

    def set_switch(self, number: int, enabled: bool) -> None:
        if self._phase is not Phase.PREPARING:
            raise RuntimeError("После входа нельзя возвращаться к выключателям.")
        if type(number) is not int or number not in (1, 2, 3):
            raise ValueError("Номер выключателя должен быть от 1 до 3.")
        if not isinstance(enabled, bool):
            raise TypeError("Состояние выключателя должно быть bool.")
        self._switches[number - 1] = enabled

    def advance(self, seconds: float) -> None:
        """Точное экспоненциальное приближение температуры за выбранный интервал."""
        if self._phase is not Phase.PREPARING:
            raise RuntimeError("После входа наблюдения зафиксированы.")
        if (isinstance(seconds, bool) or not isinstance(seconds, (int, float))
                or not math.isfinite(seconds) or seconds < 0):
            raise ValueError("Время должно быть конечным неотрицательным числом.")
        for switch, lamp_number in enumerate(self._wiring):
            enabled = self._switches[switch]
            target = self.HOT if enabled else self.AMBIENT
            tau = self.HEATING_TAU if enabled else self.COOLING_TAU
            index = lamp_number - 1
            previous = self._temperatures[index]
            self._temperatures[index] = target + (previous - target) * math.exp(-seconds / tau)
        self._elapsed += seconds

    def enter_room(self) -> tuple[LampObservation, ...]:
        if self._phase is not Phase.PREPARING:
            raise RuntimeError("Войти в комнату можно только один раз.")
        self._observations = tuple(
            LampObservation(number, self._switches[self._wiring.index(number)],
                            self._temperatures[number - 1])
            for number in (1, 2, 3)
        )
        self._phase = Phase.OBSERVING
        return self._observations

    def submit(self, answer: tuple[int, int, int]) -> bool:
        """answer: выключатель лампы 1, затем лампы 2 и лампы 3."""
        if self._phase is not Phase.OBSERVING:
            raise RuntimeError("Ответ можно проверить один раз, после входа.")
        self._validate_permutation(answer)
        correct = all(self._wiring[switch - 1] == lamp
                        for lamp, switch in enumerate(answer, start=1))
        self._phase = Phase.FINISHED
        return correct

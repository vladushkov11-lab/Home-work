from dataclasses import dataclass


@dataclass(frozen=True)
class RoomState:
    """Неизменяемый снимок состояния одной комнаты."""

    floor: int
    name: str
    is_on: bool


class HouseLighting:
    """Один общий выключатель управляет всеми тремя комнатами."""

    # Номер этажа и название комнаты. В интерфейсе верхний этаж рисуется первым.
    ROOM_LAYOUT = ((1, "Гостиная"), (2, "Кабинет"), (3, "Спальня"))

    def __init__(self) -> None:
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def rooms(self) -> tuple[RoomState, ...]:
        return tuple(
            RoomState(floor, name, self._is_on)
            for floor, name in self.ROOM_LAYOUT
        )

    @property
    def lit_count(self) -> int:
        return sum(room.is_on for room in self.rooms)

    def set_lights(self, enabled: bool) -> None:
        """Задаём состояние, а не инвертируем его при каждом нажатии."""
        if not isinstance(enabled, bool):
            raise TypeError("Состояние света должно быть bool: True или False.")
        self._is_on = enabled

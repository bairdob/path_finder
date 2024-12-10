from enum import Enum


class StatesEnum(Enum):
    IDLE = "Ожидание"
    PATH_FINDING = "Поиск пути"
    MOVING = "Движение"
    CAPTURE = "Захват"
    FINISH = "Завершено"


class StateManager:
    def __init__(self, status_label):
        self.state = StatesEnum.IDLE
        self.status_label = status_label
        self.update_label()

    def set_state(self, new_state):
        """Устанавливает новое состояние"""
        self.state = new_state
        self.update_label()

    def get_state(self):
        """Возвращает текущее состояние"""
        return self.state

    def is_state(self, state):
        """Проверяет, соответствует ли текущее состояние заданному"""
        return self.state == state

    def update_label(self):
        """Обновляет текст в виджете состояния"""
        self.status_label.setText(f"Состояние: {self.state.value}")

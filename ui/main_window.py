import random

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox

from algorithms.a_star import AStar
from models.grid import Grid
from ui.state_manager import StateManager, StatesEnum


class MainWindow(QMainWindow):
    def __init__(self, number_obstacles=10, number_goals=4):
        """

        :param number_obstacles: количество препятствий
        :param number_goals: количество целей
        """
        super().__init__()

        # Количество препятствий и промежуточных точек
        self.n_obstacles = number_obstacles
        self.n_goals = number_goals

        self.setWindowTitle("Path Finder")
        self.setGeometry(100, 100, 600, 600)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Установка фонового изображения для карты-подложки
        self.set_background_image(central_widget, "resources/background.png")

        # Макет
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Текстовое поле состояния
        self.state_label = QLabel()
        self.state_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        layout.addWidget(self.state_label)
        # Менеджер состояний
        self.state_manager = StateManager(self.state_label)

        # Сетка для отображения карты
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        # Кнопки управления
        self.start_button = QPushButton("Start Search")
        self.start_button.setStyleSheet("background-color: #805a00; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_search)
        layout.addWidget(self.start_button)

        # Кнопки для генерации стартовой точки, цели и препятствий
        self.generate_start_button = QPushButton("Generate Start")
        self.generate_start_button.setStyleSheet("background-color: #215f23; color: white; padding: 5px;")
        self.generate_start_button.clicked.connect(self.generate_start)
        layout.addWidget(self.generate_start_button)

        self.generate_end_button = QPushButton("Generate Goal")
        self.generate_end_button.setStyleSheet("background-color: #215f23; color: white; padding: 5px;")
        self.generate_end_button.clicked.connect(self.generate_end)
        layout.addWidget(self.generate_end_button)

        self.generate_obstacles_button = QPushButton("Generate Obstacles")
        self.generate_obstacles_button.setStyleSheet("background-color: #215f23; color: white; padding: 5px;")
        self.generate_obstacles_button.clicked.connect(self.generate_and_draw_obstacles)
        layout.addWidget(self.generate_obstacles_button)

        # Создаем модель карты
        self.grid = Grid(10, 10)  # 10x10 клеток

        # Иконки
        self.start_icon = QPixmap("resources/icons/start.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.end_icon = QPixmap("resources/icons/end.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.obstacle_icon = QPixmap("resources/icons/obstacle.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.robot_icon = QPixmap("resources/icons/robot.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.goal_icon = QPixmap("resources/icons/goal.png").scaled(40, 40, Qt.KeepAspectRatio)

        # Генерация случайных препятствий и промежуточных точек
        self.goals = self.initialize_goal_from_ontology()
        self.obstacles = self.generate_obstacles()

        # Переменные для старта и цели
        self.start = self.generate_random_edge_position()
        self.end = self.generate_random_edge_position()
        # Убедимся, что старт и цель не совпадают
        while self.start == self.end:
            self.end = self.generate_random_edge_position()

        # Отрисовка сетки
        self.draw_grid()

    def set_background_image(self, widget, image_path):
        """Устанавливает фоновое изображение для виджета"""
        palette = QPalette()
        background = QPixmap(image_path)
        palette.setBrush(QPalette.Background, QBrush(background))
        widget.setAutoFillBackground(True)
        widget.setPalette(palette)

    def generate_obstacles(self):
        """Генерация случайных препятствий на сетке"""
        all_cells = [(x, y) for x in range(10) for y in range(10)]

        # Убираем стартовую и целевую точки и цели из возможных препятствий
        all_cells.remove((0, 0))  # Стартовая точка
        all_cells.remove((9, 9))  # Целевая точка
        all_cells = [cell for cell in all_cells if cell not in self.goals]

        # Генерация случайных n препятствий
        obstacles = random.sample(all_cells, self.n_obstacles)
        return obstacles

    def generate_intermediate_points(self):
        """Генерация случайных промежуточных точек"""
        all_cells = [(x, y) for x in range(10) for y in range(10)]

        # Убираем стартовую, целевую точки и препятствия
        all_cells.remove((0, 0))  # Стартовая точка
        all_cells.remove((9, 9))  # Целевая точка

        # Генерация случайных промежуточных точек
        intermediate_points = random.sample(all_cells, self.n_goals)
        return intermediate_points

    def draw_grid(self):
        """ Отрисовка сетки с иконками """
        self.state_manager.set_state(StatesEnum.IDLE)
        # Очищаем текущую сетку
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        for x in range(self.grid.rows):
            for y in range(self.grid.cols):
                label = QLabel()
                label.setFixedSize(40, 40)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("border: 1px solid black;")

                # Стартовая и целевая точки
                if (x, y) == self.start:
                    label.setPixmap(self.start_icon)
                # Целевая точка
                elif (x, y) == self.end:
                    label.setPixmap(self.end_icon)
                # Препятствия
                elif (x, y) in self.obstacles:
                    label.setPixmap(self.obstacle_icon)
                # Промежуточные точки
                elif (x, y) in self.goals:
                    label.setPixmap(self.goal_icon)
                else:
                    # Просто пустая клетка
                    label.setText("")

                self.grid_layout.addWidget(label, x, y)

    def start_search(self):
        """ Запуск поиска пути с помощью алгоритма A* """
        # Добавляем препятствия в модель карты
        for obstacle in self.obstacles:
            self.grid.add_obstacle(obstacle)

        # Комбинируем точки для поиска пути
        points = [self.start] + self.goals + [self.end]

        if not self.state_manager.is_state(StatesEnum.IDLE):
            QMessageBox.warning(self, "Ошибка", "Робот уже выполняет задачу!")
            return

        # Здесь будем вызывать алгоритм A* через все промежуточные точки
        self.state_manager.set_state(StatesEnum.PATH_FINDING)
        a_star = AStar(self.grid)
        full_path = []
        for i in range(len(points) - 1):
            path = a_star.search(points[i], points[i + 1])
            if path:
                full_path.extend(path)
            else:
                QMessageBox.warning(self, "No Path", f"Path not found between {points[i]} and {points[i + 1]}")
                return

        QMessageBox.information(self, "Path Found", f"Path: {full_path}")
        self.animate_path(full_path)

    def generate_start(self):
        """ Генерация случайной стартовой точки на границе """
        self.start = self.generate_random_edge_position()
        self.draw_grid()

    def generate_end(self):
        """ Генерация случайной целевой точки на границе """
        self.end = self.generate_random_edge_position()

        # Убедимся, что старт и цель не совпадают
        while self.start == self.end:
            self.end = self.generate_random_edge_position()

        self.draw_grid()

    def generate_and_draw_obstacles(self):
        """ Генерация случайных препятствий и обновление сетки """
        self.obstacles = self.generate_obstacles()
        self.draw_grid()

    def generate_random_edge_position(self):
        """ Генерирует случайную позицию на границе карты (крае сетки) """
        rows = self.grid.rows - 1
        cols = self.grid.cols - 1

        # Генерируем случайную позицию на границе
        if random.choice([True, False]):  # Выбираем между горизонтальной или вертикальной границей
            # Горизонтальная граница (первый или последний ряд)
            x = random.choice([0, rows])
            y = random.randint(0, cols)
        else:
            # Вертикальная граница (первая или последняя колонка)
            x = random.randint(0, rows)
            y = random.choice([0, cols])

        return x, y

    def animate_path(self, path):
        """ Анимация движения робота по найденному пути с задержкой """
        self.step_index = 0
        self.path = path
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_robot_step)
        self.timer.start(500)  # Интервал между шагами (500 мс)

    def move_robot_step(self):
        """ Двигает робота на один шаг """
        if self.step_index >= len(self.path):
            self.timer.stop()
            return

        step = self.path[self.step_index]
        self.step_index += 1

        if step in self.goals:
            self.state_manager.set_state(StatesEnum.CAPTURE)
        elif step == self.end:
            self.state_manager.set_state(StatesEnum.FINISH)
        else:
            self.state_manager.set_state(StatesEnum.MOVING)

        # Очищаем предыдущий шаг
        if self.step_index > 1:
            prev_step = self.path[self.step_index - 2]
            prev_label = self.grid_layout.itemAtPosition(prev_step[0], prev_step[1]).widget()
            prev_label.clear()

        # Обновляем текущее положение робота
        current_label = self.grid_layout.itemAtPosition(step[0], step[1]).widget()
        current_label.setPixmap(self.robot_icon)

        # Обновляем интерфейс
        QApplication.processEvents()

    def initialize_goal_from_ontology(self):
        """Инициализация цедей на основе данных из онтологии"""
        from owlready2 import get_ontology

        goals = []
        onto = get_ontology("ui/goal.xml").load()
        for goal in onto.Goal.instances():
            point = goal.x_position[0], goal.y_position[0]
            goals.append(point)
        return goals

import random

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox

from algorithms.a_star import AStar
from models.grid import Grid


class MainWindow(QMainWindow):
    def __init__(self, n_obstacles=10, n_intermediate=4):
        super().__init__()
        self.setWindowTitle("Path Finder")
        self.setGeometry(100, 100, 600, 600)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Макет
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Сетка для отображения карты
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        # Кнопки управления
        self.start_button = QPushButton("Start Search")
        self.start_button.clicked.connect(self.start_search)
        layout.addWidget(self.start_button)

        # Создаем модель карты
        self.grid = Grid(10, 10)  # 10x10 клеток

        # Иконки
        self.start_icon = QPixmap("resources/icons/start.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.goal_icon = QPixmap("resources/icons/goal.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.obstacle_icon = QPixmap("resources/icons/obstacle.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.robot_icon = QPixmap("resources/icons/robot.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.intermediate_icon = QPixmap("resources/icons/goal.png").scaled(40, 40, Qt.KeepAspectRatio)

        # Количество препятствий и промежуточных точек
        self.n_obstacles = n_obstacles
        self.n_intermediate = n_intermediate

        # Генерация случайных препятствий и промежуточных точек
        self.obstacles = self.generate_obstacles()
        self.intermediate_points = self.generate_intermediate_points()

        # Отрисовка сетки
        self.draw_grid()

    def generate_obstacles(self):
        """Генерация случайных препятствий на сетке"""
        all_cells = [(x, y) for x in range(10) for y in range(10)]

        # Убираем стартовую и целевую точки из возможных препятствий
        all_cells.remove((0, 0))  # Стартовая точка
        all_cells.remove((9, 9))  # Целевая точка

        # Генерация случайных n препятствий
        obstacles = random.sample(all_cells, self.n_obstacles)
        return obstacles

    def generate_intermediate_points(self):
        """Генерация случайных промежуточных точек"""
        all_cells = [(x, y) for x in range(10) for y in range(10)]

        # Убираем стартовую, целевую точки и препятствия
        all_cells.remove((0, 0))  # Стартовая точка
        all_cells.remove((9, 9))  # Целевая точка
        all_cells = [cell for cell in all_cells if cell not in self.obstacles]

        # Генерация случайных промежуточных точек
        intermediate_points = random.sample(all_cells, self.n_intermediate)
        return intermediate_points


    def draw_grid(self):
        """ Отрисовка сетки с иконками """
        for x in range(self.grid.rows):
            for y in range(self.grid.cols):
                label = QLabel()
                label.setFixedSize(40, 40)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("border: 1px solid black;")

                # Стартовая и целевая точки
                if (x, y) == (0, 0):
                    label.setPixmap(self.start_icon)
                # Целевая точка
                elif (x, y) == (9, 9):
                    label.setPixmap(self.goal_icon)
                # Препятствия
                elif (x, y) in self.obstacles:
                    label.setPixmap(self.obstacle_icon)
                # Промежуточные точки
                elif (x, y) in self.intermediate_points:
                    label.setPixmap(self.intermediate_icon)
                else:
                    # Просто пустая клетка
                    label.setText("")

                self.grid_layout.addWidget(label, x, y)


    def start_search(self):
        """ Запуск поиска пути с помощью алгоритма A* """
        start = (0, 0)  # Начальная позиция
        goal = (9, 9)  # Целевая позиция

        # Добавляем препятствия в модель карты
        for obstacle in self.obstacles:
            self.grid.add_obstacle(obstacle)

        # Комбинируем точки для поиска пути
        points = [start] + self.intermediate_points + [goal]

        # Здесь будем вызывать алгоритм A* через все промежуточные точки
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

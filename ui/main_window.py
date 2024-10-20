import random

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QBrush
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

        # Установка фонового изображения для карты-подложки
        self.set_background_image(central_widget, "resources/background.png")

        # Макет
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

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

        self.generate_goal_button = QPushButton("Generate Goal")
        self.generate_goal_button.setStyleSheet("background-color: #215f23; color: white; padding: 5px;")
        self.generate_goal_button.clicked.connect(self.generate_goal)
        layout.addWidget(self.generate_goal_button)

        self.generate_obstacles_button = QPushButton("Generate Obstacles")
        self.generate_obstacles_button.setStyleSheet("background-color: #215f23; color: white; padding: 5px;")
        self.generate_obstacles_button.clicked.connect(self.generate_and_draw_obstacles)
        layout.addWidget(self.generate_obstacles_button)

        # Создаем модель карты
        self.grid = Grid(10, 10)  # 10x10 клеток

        # Иконки
        self.start_icon = QPixmap("resources/icons/start.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.goal_icon = QPixmap("resources/icons/goal.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.obstacle_icon = QPixmap("resources/icons/obstacle.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.robot_icon = QPixmap("resources/icons/robot.png").scaled(40, 40, Qt.KeepAspectRatio)
        self.intermediate_icon = QPixmap("resources/icons/flag.png").scaled(40, 40, Qt.KeepAspectRatio)

        # Количество препятствий и промежуточных точек
        self.n_obstacles = n_obstacles
        self.n_intermediate = n_intermediate

        # Генерация случайных препятствий и промежуточных точек
        self.intermediate_points = self.generate_intermediate_points()
        self.obstacles = self.generate_obstacles()

        # Переменные для старта и цели
        self.start = self.generate_random_edge_position()
        self.goal = self.generate_random_edge_position()
        # Убедимся, что старт и цель не совпадают
        while self.start == self.goal:
            self.goal = self.generate_random_edge_position()

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
        all_cells = [cell for cell in all_cells if cell not in self.intermediate_points]

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
        intermediate_points = random.sample(all_cells, self.n_intermediate)
        return intermediate_points

    def draw_grid(self):
        """ Отрисовка сетки с иконками """
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
                elif (x, y) == self.goal:
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
        # Добавляем препятствия в модель карты
        for obstacle in self.obstacles:
            self.grid.add_obstacle(obstacle)

        # Комбинируем точки для поиска пути
        points = [self.start] + self.intermediate_points + [self.goal]

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

    def generate_start(self):
        """ Генерация случайной стартовой точки на границе """
        self.start = self.generate_random_edge_position()
        self.draw_grid()

    def generate_goal(self):
        """ Генерация случайной целевой точки на границе """
        self.goal = self.generate_random_edge_position()

        # Убедимся, что старт и цель не совпадают
        while self.start == self.goal:
            self.goal = self.generate_random_edge_position()

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
